import json
from pathlib import Path

import boto3
from google.cloud import bigquery

# Configuration -- edit these values
S3_BUCKET = "your-s3-bucket"
S3_PREFIX = "logs/"  # prefix inside the bucket
BIGQUERY_DATASET = "your_project.your_dataset"
CRASHLYTICS_TABLE = "firebase_crashlytics"  # exported table name
OUTPUT_FILE = Path("merged_logs.jsonl")


def fetch_s3_logs(bucket: str, prefix: str) -> list[dict]:
    """Download JSON log files from S3 and return list of entries."""
    s3 = boto3.client("s3")
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


def fetch_crashlytics_logs(dataset: str, table: str) -> list[dict]:
    """Query Crashlytics BigQuery export and return list of entries."""
    client = bigquery.Client()
    query = f"SELECT * FROM `{dataset}.{table}`"
    rows = client.query(query).result()
    return [dict(row) for row in rows]


def main() -> None:
    s3_logs = fetch_s3_logs(S3_BUCKET, S3_PREFIX)
    crash_logs = fetch_crashlytics_logs(BIGQUERY_DATASET, CRASHLYTICS_TABLE)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for entry in s3_logs + crash_logs:
            f.write(json.dumps(entry) + "\n")
    print(f"Merged {len(s3_logs) + len(crash_logs)} records into {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
