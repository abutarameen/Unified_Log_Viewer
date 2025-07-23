import json
from pathlib import Path

import boto3
from google.cloud import bigquery

SETTINGS_FILE = Path("settings.json")
OUTPUT_FILE = Path("merged_logs.jsonl")


def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    raise RuntimeError(
        "settings.json not found. Run desktop_unifier.py to configure settings."
    )


def fetch_s3_logs(cfg: dict) -> list[dict]:
    """Download JSON log files from S3 and return list of entries."""
    session = boto3.Session(
        aws_access_key_id=cfg.get("aws_access_key"),
        aws_secret_access_key=cfg.get("aws_secret_key"),
    )
    s3 = session.client("s3")
    bucket = cfg["s3_bucket"]
    prefix = cfg["s3_prefix"]
    logs = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.endswith(".json"):
                continue
            body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
            logs.extend(json.loads(body))
    return logs


def fetch_crashlytics_logs(cfg: dict) -> list[dict]:
    """Query Crashlytics BigQuery export and return list of entries."""
    client = bigquery.Client.from_service_account_json(cfg["google_credentials"])
    query = f"SELECT * FROM `{cfg['bigquery_dataset']}.{cfg['crashlytics_table']}`"
    rows = client.query(query).result()
    return [dict(row) for row in rows]


def main() -> None:
    cfg = load_settings()
    s3_logs = fetch_s3_logs(cfg)
    crash_logs = fetch_crashlytics_logs(cfg)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for entry in s3_logs + crash_logs:
            f.write(json.dumps(entry) + "\n")
    print(f"Merged {len(s3_logs) + len(crash_logs)} records into {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
