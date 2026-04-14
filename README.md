# Crypt Mainica Android + Backend

This repository now contains **two separate runnable projects**:

1. `crypt_mainica_backend/` → FastAPI realtime signal backend.
2. `crypt_mainica_android/` → Android app project (Manifest + Gradle + Compose UI).

Legacy log-unifier scripts remain in root (`log_unifier.py`, `desktop_unifier.py`) but are not part of Crypt Mainica.

---

## 1) Crypt Mainica Backend

Location: `crypt_mainica_backend/`

### Install

```bash
pip install -r crypt_mainica_backend/requirements.txt
```

### Run

```bash
uvicorn crypt_mainica_backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Endpoints

- `GET /health`
- `GET /signals/top?top_n=10`
- `WS /signals/ws`

---

## 2) Crypt Mainica Android

Location: `crypt_mainica_android/`

This is now a **real Android app project** with:

- `settings.gradle.kts`
- Root/app `build.gradle.kts`
- `AndroidManifest.xml`
- `MainActivity.kt`
- Compose UI screen and ViewModel
- Retrofit + WebSocket networking

### Open and run

1. Open `crypt_mainica_android/` in Android Studio.
2. Sync Gradle.
3. Run app on emulator/device.
4. Ensure backend is running on `http://10.0.2.2:8000` (default emulator host mapping).

For emulator HTTP development, cleartext is enabled for `10.0.2.2` via `network_security_config.xml`.

If using a physical device, update base URLs in:

- `crypt_mainica_android/app/src/main/java/com/cryptmainica/app/data/Network.kt`

---

## Project rename

The active product name is now **Crypt Mainica** (Android + Backend).
