# Android Signal App Sample (MVVM + Retrofit + WebSocket)

This is a lightweight sample to connect to the FastAPI backend in `realtime_backend/main.py`.

## Wire to backend

- REST: `http://<YOUR_HOST>:8000/top`
- WebSocket: `ws://<YOUR_HOST>:8000/ws`

## Included files

- `CoinSignal.kt` model used by both REST and WebSocket parsing.
- `ApiService.kt` Retrofit interface.
- `CoinViewModel.kt` LiveData state and WebSocket updates.
- `CoinAdapter.kt` RecyclerView adapter with color-coded signal labels.
- `item_coin.xml` row layout.
- `ui/CoinDashboardScreen.kt` Jetpack Compose dashboard screen (includes empty-state `Box` fix).

## Notes

- For production, add paging, retries, and local Room caching.
- Use your own risk controls and never auto-trade without strict limits.
