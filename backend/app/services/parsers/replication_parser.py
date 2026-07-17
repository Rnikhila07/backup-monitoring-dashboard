import pandas as pd

def parse_replication(file_path: str):
    df = pd.read_csv(file_path)

    df["Latest Updated Date"] = pd.to_datetime(df["Latest Updated Date"], errors="coerce")
    df["Last Updated Date"] = pd.to_datetime(df["Last Updated Date"], errors="coerce")

    records = []

    for _, row in df.iterrows():
        record = {
            "app_job_id": None,
            "server_name": None,
            "client_name": row["Client Name"],
            "status": None,
            "status_code": None,
            "backup_level": None,
            "backup_size_gb": None,
            "total_files": None,
            "files_not_backed_up": None,
            "started_at": safe_value(row["Last Updated Date"]),
            "finished_at": safe_value(row["Latest Updated Date"]),
            "duration_minutes": None,
            "expires_on": None,
            "total_jobs": None,
            "reduction_ratio": None,
            "deduplication_ratio": None,
            "successful_copies": None,
            "failed_copies": None,
            "uploaded_report_date": None,
        }
        records.append(record)

    return records


def safe_value(value):
    if pd.isnull(value):
        return None
    return value