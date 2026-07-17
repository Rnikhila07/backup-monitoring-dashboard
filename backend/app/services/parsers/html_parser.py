import pandas as pd

def parse_html(file_path: str):
    tables = pd.read_html(file_path)
    df = tables[0]  # assume the report's data is in the first table on the page

    df["Started"] = pd.to_datetime(df["Started"], errors="coerce")
    df["Finished"] = pd.to_datetime(df["Finished"], errors="coerce")
    df["Expires"] = pd.to_datetime(df["Expires"], errors="coerce")

    records = []

    for _, row in df.iterrows():
        record = {
            "app_job_id": row["App Job Id"],
            "server_name": row["Server"],
            "client_name": row["Client"],
            "status": row["Status"],
            "status_code": int(row["Status Code"]),
            "backup_level": row["Backup Level"],
            "backup_size_gb": float(row["Backup Size (GB)"]),
            "total_files": int(row["Total Files"]),
            "files_not_backed_up": int(row["Files Not Backed Up"]),
            "started_at": safe_value(row["Started"]),
            "finished_at": safe_value(row["Finished"]),
            "duration_minutes": int(row["Duration (Minutes)"]) if pd.notnull(row["Duration (Minutes)"]) else None,
            "expires_on": row["Expires"].date() if pd.notnull(row["Expires"]) else None,
            "total_jobs": int(row["Total Jobs"]),
            "reduction_ratio": float(row["Reduction Ratio"]),
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