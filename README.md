# AI Data Log Unifier

This repository contains a simple example of how you might aggregate logs from Amazon S3 and Firebase Crashlytics using Python. The `log_unifier.py` script downloads log files from the specified S3 bucket and retrieves Crashlytics crash reports via BigQuery. The combined logs are saved locally for easy inspection.

## Requirements

- Python 3.8+
- AWS credentials with read access to the target S3 bucket
- Google Cloud credentials with access to the Crashlytics BigQuery dataset

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Edit the configuration variables at the top of `log_unifier.py` to point to your S3 bucket and BigQuery dataset. Then run:

```bash
python log_unifier.py
```

The script downloads the logs and merges them into `merged_logs.jsonl`.

## Desktop GUI

`desktop_unifier.py` provides a very small Tkinter interface. Use the **Settings**
menu to enter your AWS keys, S3 bucket information, and Crashlytics/BigQuery
credentials. These details are saved to `settings.json` for next time.

Run the GUI with:

```bash
python desktop_unifier.py
```

## Disclaimer

This is a minimal example intended for demonstration purposes only. A production-ready desktop application would require additional features such as a graphical user interface, incremental log fetching, and error handling.
