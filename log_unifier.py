import json
from pathlib import Path

import boto3
from google.cloud import bigquery

SETTINGS_FILE = Path("settings.json")
AWS_CONFIG_FILE = Path("awsconfiguration.json")
OUTPUT_FILE = Path("merged_logs.jsonl")


def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        raise RuntimeError(
            "settings.json not found. Run desktop_unifier.py to configure settings."
        )

    with SETTINGS_FILE.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg


def apply_aws_config(cfg: dict) -> dict:
    """Populate S3 bucket and region from an awsconfiguration.json file if present."""
    path = Path(cfg.get("aws_config_file", AWS_CONFIG_FILE))
    if not path.exists():
        return cfg

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        bucket = (
            data.get("storage", {})
            .get("plugins", {})
            .get("awsS3StoragePlugin", {})
            .get("bucket")
        )
        region = (
            data.get("storage", {})
            .get("plugins", {})
            .get("awsS3StoragePlugin", {})
            .get("region")
        )
        if not bucket:
            bucket = (
                data.get("S3TransferUtility", {})
                .get("Default", {})
                .get("Bucket")
            )
            region = (
                data.get("S3TransferUtility", {})
                .get("Default", {})
                .get("Region")
            )
        if not bucket:
            bucket = (
                data.get("auth", {})
                .get("plugins", {})
                .get("awsCognitoAuthPlugin", {})
                .get("S3TransferUtility", {})
                .get("Default", {})
                .get("Bucket")
            )
            region = (
                data.get("auth", {})
                .get("plugins", {})
                .get("awsCognitoAuthPlugin", {})
                .get("S3TransferUtility", {})
                .get("Default", {})
                .get("Region")
            )

        if bucket and "s3_bucket" not in cfg:
            cfg["s3_bucket"] = bucket
        if region and "aws_region" not in cfg:
            cfg["aws_region"] = region
    except Exception:
        pass

    return cfg


def fetch_s3_logs(cfg: dict) -> list[dict]:
    """Download JSON log files from S3 and return list of entries."""
    session = boto3.Session(
        aws_access_key_id=cfg.get("aws_access_key"),
        aws_secret_access_key=cfg.get("aws_secret_key"),
        region_name=cfg.get("aws_region", "us-east-1"),
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
    cfg = apply_aws_config(cfg)
    s3_logs = fetch_s3_logs(cfg)
    crash_logs = fetch_crashlytics_logs(cfg)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for entry in s3_logs + crash_logs:
            f.write(json.dumps(entry) + "\n")
    print(f"Merged {len(s3_logs) + len(crash_logs)} records into {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
