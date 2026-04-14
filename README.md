# AI Data Log Unifier + Realtime Coin Signals

This repository now contains two runnable parts:

1. **Log Unifier** (existing functionality).
2. **Realtime Signal Backend** for Android coin dashboards.

## Requirements

- Python 3.8+
- AWS credentials with read access to the target S3 bucket
- Google Cloud credentials with access to the Crashlytics BigQuery dataset

Install dependencies:

```bash
pip install -r requirements.txt
```

## Existing log-unifier usage

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

---

## Realtime backend (FastAPI + WebSocket)

File: `realtime_backend/main.py`

Features:

- Pulls Solana pairs from DexScreener.
- Applies your MVP filters:
  - Age < 24h
  - Liquidity > $10k
  - 24h Volume > $50k
- Computes 0-100 score using:
  - Volume spike
  - Buy/sell pressure
  - Whale proxy activity
  - Liquidity sweet spot
  - Social proxy momentum
- Adds rug-risk flags (liquidity and suspicious buy-only activity).
- Exposes:
  - `GET /top` for current ranking
  - `GET /health`
  - `WS /ws` for live feed every polling interval

Run:

```bash
uvicorn realtime_backend.main:app --reload --host 0.0.0.0 --port 8000
```

Examples:

```bash
curl http://127.0.0.1:8000/top
```

```bash
wscat -c ws://127.0.0.1:8000/ws
```

## Android sample client

`android_app_sample/` contains starter Kotlin files (MVVM + Retrofit + WebSocket + RecyclerView item layout) that connect to this backend.

- Model: `CoinSignal.kt`
- REST API interface: `ApiService.kt`
- ViewModel with WebSocket updates: `CoinViewModel.kt`
- Recycler adapter with signal colors: `CoinAdapter.kt`
- Row layout: `item_coin.xml`

Use `android_app_sample/README.md` for quick wiring notes.
