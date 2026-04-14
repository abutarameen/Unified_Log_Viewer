from __future__ import annotations

import asyncio
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana"
DEFAULT_TOP_N = int(os.getenv("TOP_N", "10"))
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "15"))


@dataclass
class CoinSignal:
    pair_address: str
    token_symbol: str
    token_name: str
    price_usd: float
    liquidity_usd: float
    volume_h24: float
    buy_sell_ratio: float
    buys_h24: int
    sells_h24: int
    score: int
    signal: str
    risk_flags: list[str]
    created_at: str


app = FastAPI(title="Realtime Meme Coin Signal API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory cache keeps Android clients fast.
LATEST_SIGNALS: list[CoinSignal] = []


def to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def score_pair(pair: dict[str, Any]) -> tuple[int, list[str], float]:
    volume_h24 = to_float(pair.get("volume", {}).get("h24"))
    liquidity_usd = to_float(pair.get("liquidity", {}).get("usd"))
    buys = to_int(pair.get("txns", {}).get("h24", {}).get("buys"))
    sells = to_int(pair.get("txns", {}).get("h24", {}).get("sells"))

    ratio = buys / max(sells, 1)
    score = 0
    risk_flags: list[str] = []

    # 1) Volume spike score (0-25)
    if volume_h24 >= 250_000:
        score += 25
    elif volume_h24 >= 100_000:
        score += 18
    elif volume_h24 >= 50_000:
        score += 10

    # 2) Buy vs sell pressure (0-20)
    if ratio >= 1.8:
        score += 20
    elif ratio >= 1.5:
        score += 14
    elif ratio >= 1.2:
        score += 8
    elif ratio <= 0.7:
        risk_flags.append("sell-pressure")

    # 3) Whale proxy score (0-20)
    # Proxy signal using large transaction count in low market cap pools.
    tx_count = buys + sells
    if tx_count > 300 and liquidity_usd < 400_000:
        score += 20
    elif tx_count > 150:
        score += 10

    # 4) Liquidity strength (0-15)
    if 20_000 <= liquidity_usd <= 200_000:
        score += 15
    elif liquidity_usd < 10_000:
        risk_flags.append("low-liquidity")

    # 5) Social momentum placeholder (0-20)
    # Real social feeds can be inserted later; using tx acceleration proxy now.
    if tx_count >= 200:
        score += 16
    elif tx_count >= 80:
        score += 8

    # Rug risk guardrails
    if liquidity_usd < 20_000:
        risk_flags.append("rug-risk-liquidity")
    if ratio > 4.0 and sells < 3:
        risk_flags.append("possible-honeypot")

    return min(score, 100), risk_flags, ratio


def signal_label(score: int) -> str:
    if score >= 80:
        return "STRONG_BUY"
    if score >= 60:
        return "WATCH"
    if score >= 40:
        return "RISKY"
    return "AVOID"


async def fetch_pairs() -> list[dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(DEXSCREENER_URL)
            response.raise_for_status()
            payload = response.json()
        return payload.get("pairs", [])
    except Exception:
        return []


def passes_filters(pair: dict[str, Any]) -> bool:
    liquidity_usd = to_float(pair.get("liquidity", {}).get("usd"))
    volume_h24 = to_float(pair.get("volume", {}).get("h24"))
    created_at_ms = to_int(pair.get("pairCreatedAt"))

    if liquidity_usd < 10_000 or volume_h24 < 50_000:
        return False

    if created_at_ms > 0:
        age_hours = (datetime.now(timezone.utc).timestamp() - created_at_ms / 1000) / 3600
        if age_hours > 24:
            return False

    return True


async def build_signals(top_n: int = DEFAULT_TOP_N) -> list[CoinSignal]:
    pairs = await fetch_pairs()
    scored: list[CoinSignal] = []

    for pair in pairs:
        if not passes_filters(pair):
            continue

        score, risk_flags, ratio = score_pair(pair)
        coin = CoinSignal(
            pair_address=str(pair.get("pairAddress", "")),
            token_symbol=str(pair.get("baseToken", {}).get("symbol", "?")),
            token_name=str(pair.get("baseToken", {}).get("name", "Unknown")),
            price_usd=to_float(pair.get("priceUsd")),
            liquidity_usd=to_float(pair.get("liquidity", {}).get("usd")),
            volume_h24=to_float(pair.get("volume", {}).get("h24")),
            buy_sell_ratio=round(ratio, 3),
            buys_h24=to_int(pair.get("txns", {}).get("h24", {}).get("buys")),
            sells_h24=to_int(pair.get("txns", {}).get("h24", {}).get("sells")),
            score=score,
            signal=signal_label(score),
            risk_flags=risk_flags,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        scored.append(coin)

    scored.sort(key=lambda c: c.score, reverse=True)
    return scored[:top_n]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/top")
async def get_top(top_n: int = DEFAULT_TOP_N) -> list[dict[str, Any]]:
    global LATEST_SIGNALS
    if not LATEST_SIGNALS:
        LATEST_SIGNALS = await build_signals(top_n=top_n)
    return [asdict(item) for item in LATEST_SIGNALS[:top_n]]


@app.websocket("/ws")
async def stream_top(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        while True:
            data = await build_signals()
            await websocket.send_json([asdict(item) for item in data])
            await asyncio.sleep(POLL_SECONDS)
    except WebSocketDisconnect:
        return


@app.on_event("startup")
async def refresh_loop() -> None:
    async def updater() -> None:
        global LATEST_SIGNALS
        while True:
            try:
                LATEST_SIGNALS = await build_signals()
            except Exception:
                # Keep serving last good snapshot.
                pass
            await asyncio.sleep(POLL_SECONDS)

    asyncio.create_task(updater())
