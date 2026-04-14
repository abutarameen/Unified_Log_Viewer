"""Backward-compatible entrypoint.

Keeps old path `realtime_backend/main.py` working while delegating
implementation to `crypt_mainica_backend.main`.
"""

from crypt_mainica_backend.main import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("realtime_backend.main:app", host="0.0.0.0", port=8000, reload=True)
