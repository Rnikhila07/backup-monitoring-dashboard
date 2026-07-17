from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from app.database.session import Base

class BackupJob(Base):
    __tablename__ = "backup_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    backup_type = Column(String, index=True)
    unit_number = Column(String, index=True)

    app_job_id = Column(String, index=True)
    server_name = Column(String, index=True)
    client_name = Column(String, index=True)
    status = Column(String, index=True)
    status_code = Column(Integer)
    backup_level = Column(String)
    backup_size_gb = Column(Float)
    total_files = Column(Integer)
    files_not_backed_up = Column(Integer)
    started_at = Column(DateTime)
    finished_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    expires_on = Column(Date)
    total_jobs = Column(Integer)
    reduction_ratio = Column(Float)
    deduplication_ratio = Column(Float)
    successful_copies = Column(Integer)
    failed_copies = Column(Integer)
    uploaded_report_date = Column(Date)
    source_report_id = Column(Integer, nullable=True)