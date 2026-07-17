from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import shutil
import os
from app.services.parsers.excel_parser import parse_excel
from app.services.parsers.html_parser import parse_html
from app.database.session import SessionLocal
from app.models.backup_job import BackupJob
from app.models.report import Report
from app.services.parsers.csv_parser import parse_csv
from app.services.parsers.replication_parser import parse_replication
from app.services.auth_service import get_current_user_id

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploaded_reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    backup_type: str = Form(...),
    unit_number: str = Form(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    allowed_extensions = (".csv", ".xlsx", ".xls", ".html", ".htm")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Only CSV, Excel, or HTML files are allowed")

    # Save each user's files in their own subfolder, so filenames never collide
    user_folder = os.path.join(UPLOAD_DIR, f"user_{user_id}")
    os.makedirs(user_folder, exist_ok=True)

    file_path = os.path.join(user_folder, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    filename_lower = file.filename.lower()

    try:
        if backup_type == "Replication":
            records = parse_replication(file_path)
        elif filename_lower.endswith((".xlsx", ".xls")):
            records = parse_excel(file_path)
        elif filename_lower.endswith((".html", ".htm")):
            records = parse_html(file_path)
        else:
            records = parse_csv(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")
    # Log this upload event
    report = Report(
        user_id=user_id,
        filename=file.filename,
        backup_type=backup_type,
        unit_number=unit_number
    )
    db.add(report)
    db.flush()  # lets us get report.id before committing

    for record in records:
        record["user_id"] = user_id
        record["backup_type"] = backup_type
        record["unit_number"] = unit_number
        record["source_report_id"] = report.id
        job = BackupJob(**record)
        db.add(job)

    db.commit()

    return {
        "filename": file.filename,
        "message": "File uploaded and parsed successfully",
        "records_inserted": len(records)
    }