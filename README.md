# AI Data Log Unifier

This repository contains a simple example of how to aggregate logs from Amazon S3 and Firebase Crashlytics using Python. The `log_unifier.py` script downloads log files from your S3 bucket and retrieves Crashlytics crash reports via BigQuery. The merged logs are saved locally for easy inspection.

## Requirements

- Python 3.8+
- AWS credentials with read access to the target S3 bucket
- Google Cloud credentials with access to the Crashlytics BigQuery dataset

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run `desktop_unifier.py` and open the **Settings** menu to enter your AWS keys, S3 bucket details, and Crashlytics/Firebase credentials. These values are stored in `settings.json` and used by both the GUI and the `log_unifier.py` CLI tool. If a file named `awsconfiguration.json` exists (such as one created by AWS Amplify), the S3 bucket name and region are loaded automatically unless overridden. The path to this file can also be set via the **AWS Config File** field. The settings file is excluded from version control via `.gitignore`, so your credentials remain local. After saving your settings, run the unifier script:

```bash
python log_unifier.py
```

The script downloads the logs and merges them into `merged_logs.jsonl`.

## Desktop GUI

`desktop_unifier.py` provides a minimal Tkinter interface. Use the **Settings** menu to configure AWS credentials, S3 bucket information (or point to an `awsconfiguration.json` file), and Crashlytics/Firebase keys such as your BigQuery dataset, Firebase API key, and Crashlytics token. These details are saved to `settings.json` for next time.

Run the GUI with:

```bash
python desktop_unifier.py
```

## Disclaimer

This is a minimal example intended for demonstration purposes only. A production ready desktop application would require additional features such as a graphical user interface, incremental log fetching, and robust error handling.
