import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import boto3
from google.cloud import bigquery

SETTINGS_FILE = Path("settings.json")


def load_settings():
    if SETTINGS_FILE.exists():
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "aws_access_key": "",
        "aws_secret_key": "",
        "s3_bucket": "",
        "s3_prefix": "logs/",
        "bigquery_dataset": "",
        "crashlytics_table": "firebase_crashlytics",
        "google_credentials": "",
    }


def save_settings(data: dict) -> None:
    with SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def fetch_s3_logs(cfg: dict) -> list[dict]:
    session = boto3.Session(
        aws_access_key_id=cfg["aws_access_key"],
        aws_secret_access_key=cfg["aws_secret_key"],
    )
    s3 = session.client("s3")
    logs = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=cfg["s3_bucket"], Prefix=cfg["s3_prefix"]):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.endswith(".json"):
                continue
            body = s3.get_object(Bucket=cfg["s3_bucket"], Key=key)["Body"].read()
            logs.extend(json.loads(body))
    return logs


def fetch_crashlytics_logs(cfg: dict) -> list[dict]:
    client = bigquery.Client.from_service_account_json(cfg["google_credentials"])
    query = f"SELECT * FROM `{cfg['bigquery_dataset']}.{cfg['crashlytics_table']}`"
    rows = client.query(query).result()
    return [dict(row) for row in rows]


def merge_logs(cfg: dict) -> None:
    s3_logs = fetch_s3_logs(cfg)
    crash_logs = fetch_crashlytics_logs(cfg)
    output_file = Path("merged_logs.jsonl")
    with output_file.open("w", encoding="utf-8") as f:
        for entry in s3_logs + crash_logs:
            f.write(json.dumps(entry) + "\n")
    messagebox.showinfo("Done", f"Merged {len(s3_logs) + len(crash_logs)} records into {output_file}")


class SettingsWindow(tk.Toplevel):
    def __init__(self, master, cfg):
        super().__init__(master)
        self.title("Settings")
        self.cfg = cfg
        self.resizable(False, False)

        entries = {
            "AWS Access Key": "aws_access_key",
            "AWS Secret Key": "aws_secret_key",
            "S3 Bucket": "s3_bucket",
            "S3 Prefix": "s3_prefix",
            "BigQuery Dataset": "bigquery_dataset",
            "Crashlytics Table": "crashlytics_table",
            "Google Credentials JSON": "google_credentials",
        }
        self.vars = {}
        for idx, (label, key) in enumerate(entries.items()):
            ttk.Label(self, text=label).grid(row=idx, column=0, sticky="e", padx=5, pady=2)
            var = tk.StringVar(value=cfg.get(key, ""))
            ttk.Entry(self, textvariable=var, width=40).grid(row=idx, column=1, padx=5, pady=2)
            self.vars[key] = var

        btn = ttk.Button(self, text="Save", command=self.save)
        btn.grid(row=len(entries), column=0, columnspan=2, pady=10)

    def save(self):
        for key, var in self.vars.items():
            self.cfg[key] = var.get()
        save_settings(self.cfg)
        self.destroy()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Log Unifier")
        self.geometry("300x100")
        self.cfg = load_settings()

        menubar = tk.Menu(self)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Configure", command=self.open_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        self.config(menu=menubar)

        ttk.Button(self, text="Merge Logs", command=self.run_merge).pack(pady=30)

    def open_settings(self):
        SettingsWindow(self, self.cfg)

    def run_merge(self):
        try:
            merge_logs(self.cfg)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
