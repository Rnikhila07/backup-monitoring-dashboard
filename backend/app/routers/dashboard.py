import math
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import pandas as pd

from app.database.session import SessionLocal
from app.models.backup_job import BackupJob
from app.models.report import Report
from app.services.auth_service import get_current_user_id

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clean_nan(obj):
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


@router.get("/summary")
def get_summary(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    base_query = db.query(BackupJob).filter(BackupJob.user_id == user_id)

    total_vms = base_query.with_entities(BackupJob.client_name).distinct().count()
    total_clients = total_vms
    total_servers = base_query.with_entities(BackupJob.server_name).distinct().count()

    success_count = base_query.filter(BackupJob.status == "Success").count()
    failed_count = base_query.filter(BackupJob.status == "Failed").count()
    running_count = base_query.filter(BackupJob.status == "Running").count()

    today = date.today()
    updated_today = (
        base_query.with_entities(BackupJob.client_name)
        .filter(func.date(BackupJob.finished_at) == today)
        .distinct()
        .count()
    )

    return {
        "total_vms": total_vms,
        "total_clients": total_clients,
        "total_servers": total_servers,
        "success_count": success_count,
        "failed_count": failed_count,
        "running_count": running_count,
        "updated_today": updated_today,
        "not_updated_today": total_vms - updated_today,
    }


@router.get("/pie/status")
def get_status_pie(
    backup_type: str = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    base_query = db.query(BackupJob).filter(BackupJob.user_id == user_id)

    if backup_type:
        base_query = base_query.filter(BackupJob.backup_type == backup_type)

    success_count = base_query.filter(BackupJob.status == "Success").count()
    failed_count = base_query.filter(BackupJob.status == "Failed").count()
    running_count = base_query.filter(BackupJob.status == "Running").count()

    return {
        "labels": ["Success", "Failed", "Running"],
        "values": [success_count, failed_count, running_count]
    }


@router.get("/pie/updated-today")
def get_updated_today_pie(
    backup_type: str = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    today = date.today()
    base_query = db.query(BackupJob).filter(BackupJob.user_id == user_id)

    if backup_type:
        base_query = base_query.filter(BackupJob.backup_type == backup_type)

    updated_today = (
        base_query.with_entities(BackupJob.client_name)
        .filter(func.date(BackupJob.finished_at) == today)
        .distinct()
        .count()
    )

    total_vms = base_query.with_entities(BackupJob.client_name).distinct().count()
    not_updated_today = total_vms - updated_today

    return {
        "labels": ["Updated Today", "Not Updated"],
        "values": [updated_today, not_updated_today]
    }


@router.get("/pie/vms")
def get_vms_pie(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    results = (
        db.query(BackupJob.client_name, func.count(BackupJob.id))
        .filter(BackupJob.user_id == user_id)
        .group_by(BackupJob.client_name)
        .all()
    )

    labels = [row[0] for row in results]
    values = [row[1] for row in results]

    return {
        "labels": labels,
        "values": values
    }


@router.get("/pie/metric")
def get_metric_pie(
    backup_type: str,
    metric: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    base_query = db.query(BackupJob).filter(
        BackupJob.user_id == user_id,
        BackupJob.backup_type == backup_type
    )

    if metric == "status":
        success_count = base_query.filter(BackupJob.status == "Success").count()
        failed_count = base_query.filter(BackupJob.status == "Failed").count()
        running_count = base_query.filter(BackupJob.status == "Running").count()

        return {
            "labels": ["Success", "Failed", "Running"],
            "values": [success_count, failed_count, running_count]
        }

    elif metric == "files":
        low = base_query.filter(BackupJob.total_files < 1000).count()
        medium = base_query.filter(BackupJob.total_files >= 1000, BackupJob.total_files <= 10000).count()
        high = base_query.filter(BackupJob.total_files > 10000).count()

        return {
            "labels": ["<1000 Files", "1000-10000 Files", "10000+ Files"],
            "values": [low, medium, high]
        }

    elif metric == "size":
        small = base_query.filter(BackupJob.backup_size_gb < 50).count()
        medium = base_query.filter(BackupJob.backup_size_gb >= 50, BackupJob.backup_size_gb <= 150).count()
        large = base_query.filter(BackupJob.backup_size_gb > 150).count()

        return {
            "labels": ["<50GB", "50-150GB", "150GB+"],
            "values": [small, medium, large]
        }

    return {"labels": [], "values": []}


@router.get("/history")
def get_history(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    reports = (
        db.query(Report)
        .filter(Report.user_id == user_id)
        .order_by(Report.uploaded_at.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "filename": r.filename,
            "backup_type": r.backup_type,
            "unit_number": r.unit_number,
            "uploaded_at": r.uploaded_at
        }
        for r in reports
    ]


@router.get("/history/{report_id}")
def get_report_details(
    report_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    jobs = (
        db.query(BackupJob)
        .filter(BackupJob.source_report_id == report_id, BackupJob.user_id == user_id)
        .all()
    )

    return [
        {
            "client_name": job.client_name,
            "server_name": job.server_name,
            "status": job.status,
            "backup_level": job.backup_level,
            "backup_size_gb": job.backup_size_gb,
            "total_files": job.total_files,
            "files_not_backed_up": job.files_not_backed_up,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
        }
        for job in jobs
    ]


@router.get("/vm-report")
def get_vm_report(
    client_name: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    jobs = (
        db.query(BackupJob)
        .filter(BackupJob.user_id == user_id, BackupJob.client_name == client_name)
        .order_by(BackupJob.started_at)
        .all()
    )

    if not jobs:
        return {"found": False}

    rows = []
    for j in jobs:
        rows.append({
            "backup_type": j.backup_type,
            "started_at": j.started_at,
            "total_files": j.total_files or 0,
            "status": j.status,
        })
    df = pd.DataFrame(rows)
    df["started_at"] = pd.to_datetime(df["started_at"])

    # ---- Daily buckets: past 7 days ----
    now = pd.Timestamp.now()
    week_labels = []
    week_values = []
    for i in range(7, 0, -1):
        start = (now - pd.Timedelta(days=i)).normalize()
        end = start + pd.Timedelta(days=1)
        day_total = df[(df["started_at"] >= start) & (df["started_at"] < end)]["total_files"].sum()
        week_labels.append(start.strftime("%b %d"))
        week_values.append(int(day_total))

    # ---- Breakdown by category ----
    by_category = {k: int(v) for k, v in df.groupby("backup_type")["total_files"].sum().items()}

    # ---- Anomaly detection using Z-score ----
    anomaly_flag = "Not enough data"
    if len(df) >= 5:
        median_files = df["total_files"].median()
        mad = (df["total_files"] - median_files).abs().median()
        latest_value = df.iloc[-1]["total_files"]

        if mad and not math.isnan(mad) and mad > 0:
            modified_z = 0.6745 * abs(latest_value - median_files) / mad
            anomaly_flag = "Abnormal" if modified_z > 3.5 else "Normal"
        else:
            anomaly_flag = "Normal"

    result = {
        "found": True,
        "client_name": client_name,
        "total_records": len(df),
        "week_labels": week_labels,
        "week_values": week_values,
        "by_category": by_category,
        "latest_status": df.iloc[-1]["status"],
        "anomaly_status": anomaly_flag
    }

    return clean_nan(result)


@router.get("/vm-report-all")
def get_vm_report_all(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    all_jobs = (
        db.query(BackupJob)
        .filter(BackupJob.user_id == user_id)
        .order_by(BackupJob.client_name, BackupJob.started_at)
        .all()
    )

    if not all_jobs:
        return []

    rows = []
    for j in all_jobs:
        rows.append({
            "client_name": j.client_name,
            "backup_type": j.backup_type,
            "started_at": j.started_at,
            "total_files": j.total_files or 0,
            "status": j.status,
        })
    df = pd.DataFrame(rows)
    df["started_at"] = pd.to_datetime(df["started_at"])

    results = []

    for client_name, group in df.groupby("client_name"):
        group = group.sort_values("started_at")
        total_records = len(group)
        latest_status = group.iloc[-1]["status"]

        anomaly_flag = "Not enough data"
        if total_records >= 5:
            median_files = group["total_files"].median()
            mad = (group["total_files"] - median_files).abs().median()
            latest_value = group.iloc[-1]["total_files"]

            if mad and not math.isnan(mad) and mad > 0:
                modified_z = 0.6745 * abs(latest_value - median_files) / mad
                anomaly_flag = "Abnormal" if modified_z > 3.5 else "Normal"
            else:
                anomaly_flag = "Normal"
        results.append({
            "client_name": client_name,
            "total_records": total_records,
            "latest_status": latest_status,
            "anomaly_status": anomaly_flag
        })

    return clean_nan(results)