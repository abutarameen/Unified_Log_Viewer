# AI Data Log Unifier


## Requirements

- Python 3.8+
- AWS credentials with read access to the target S3 bucket
- Google Cloud credentials with access to the Crashlytics BigQuery dataset

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage


```bash
python log_unifier.py
```

The script downloads the logs and merges them into `merged_logs.jsonl`.

## Desktop GUI

`desktop_unifier.py` provides a minimal Tkinter interface. Use the **Settings** menu to configure AWS credentials, S3 bucket information, and Crashlytics/Firebase keys such as your BigQuery dataset, Firebase API key, and Crashlytics token. These details are saved to `settings.json` for next time.

Run the GUI with:

```bash
python desktop_unifier.py
```

## Disclaimer

