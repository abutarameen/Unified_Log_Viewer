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
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "15"))


@dataclass
class SignalCoin:
    pair_address: str
    token_symbol: str
    token_name: str
    price_usd: float
    volume_h24: float
    liquidity_usd: float
    buy_sell_ratio: float
    score: int
    signal: str
    risks: list[str]
    updated_at: str


app = FastAPI(title="Crypt Mainica Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LATEST_TOP10: list[SignalCoin] = []


def _float(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def _int(v: Any) -> int:
    try:
        return int(v)
    except Exception:
        return 0


def classify(score: int) -> str:
    if score >= 80:
        return "STRONG_BUY"
    if score >= 60:
        return "WATCH"
    if score >= 40:
        return "RISKY"
    return "AVOID"


def score_pair(pair: dict[str, Any]) -> tuple[int, float, list[str]]:
    volume_h24 = _float(pair.get("volume", {}).get("h24"))
    liquidity = _float(pair.get("liquidity", {}).get("usd"))
    buys = _int(pair.get("txns", {}).get("h24", {}).get("buys"))
    sells = _int(pair.get("txns", {}).get("h24", {}).get("sells"))
    ratio = buys / max(sells, 1)
    tx_count = buys + sells

    risks: list[str] = []
    score = 0

    # Volume spike (0-25)
    if volume_h24 > 250_000:
        score += 25
    elif volume_h24 > 100_000:
        score += 18
    elif volume_h24 > 50_000:
        score += 12

    # Buy/Sell pressure (0-20)
    if ratio >= 1.8:
        score += 20
    elif ratio >= 1.5:
        score += 14
    elif ratio >= 1.2:
        score += 8
    elif ratio < 0.7:
        risks.append("bearish-pressure")

    # Whale activity proxy (0-20)
    if tx_count >= 400:
        score += 20
    elif tx_count >= 200:
        score += 12

    # Liquidity strength (0-15)
    if 20_000 <= liquidity <= 200_000:
        score += 15
    elif liquidity < 10_000:
        risks.append("low-liquidity")

    # Social momentum proxy (0-20)
    if tx_count >= 300:
        score += 20
    elif tx_count >= 120:
        score += 10

    # Rug checks
    if liquidity < 20_000:
        risks.append("rug-risk")
    if ratio > 4.0 and sells <= 2:
        risks.append("possible-honeypot")

    return min(score, 100), ratio, risks


def pass_filters(pair: dict[str, Any]) -> bool:
    liquidity = _float(pair.get("liquidity", {}).get("usd"))
    volume = _float(pair.get("volume", {}).get("h24"))
    created_ms = _int(pair.get("pairCreatedAt"))

    if liquidity < 10_000 or volume < 50_000:
        return False

    if created_ms > 0:
        age_hours = (datetime.now(timezone.utc).timestamp() - (created_ms / 1000)) / 3600
        if age_hours > 24:
            return False

    return True


async def fetch_pairs() -> list[dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(DEXSCREENER_URL)
            response.raise_for_status()
            return response.json().get("pairs", [])
    except Exception:
        return []


async def compute_top(top_n: int = 10) -> list[SignalCoin]:
    pairs = await fetch_pairs()
    rows: list[SignalCoin] = []

    for pair in pairs:
        if not pass_filters(pair):
            continue

        score, ratio, risks = score_pair(pair)
        rows.append(
            SignalCoin(
                pair_address=str(pair.get("pairAddress", "")),
                token_symbol=str(pair.get("baseToken", {}).get("symbol", "")),
                token_name=str(pair.get("baseToken", {}).get("name", "")),
                price_usd=_float(pair.get("priceUsd")),
                volume_h24=_float(pair.get("volume", {}).get("h24")),
                liquidity_usd=_float(pair.get("liquidity", {}).get("usd")),
                buy_sell_ratio=round(ratio, 3),
                score=score,
                signal=classify(score),
                risks=risks,
                updated_at=datetime.now(timezone.utc).isoformat(),
            )
        )

    rows.sort(key=lambda x: x.score, reverse=True)
    return rows[:top_n]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "crypt-mainica-backend"}


@app.get("/signals/top")
async def top_signals(top_n: int = 10) -> list[dict[str, Any]]:
    global LATEST_TOP10
    if not LATEST_TOP10:
        LATEST_TOP10 = await compute_top(top_n)
    return [asdict(x) for x in LATEST_TOP10[:top_n]]


@app.websocket("/signals/ws")
async def signals_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            payload = await compute_top(10)
            await websocket.send_json([asdict(x) for x in payload])
            await asyncio.sleep(POLL_SECONDS)
    except WebSocketDisconnect:
        return


@app.on_event("startup")
async def startup_refresh() -> None:
    async def updater() -> None:
        global LATEST_TOP10
        while True:
            LATEST_TOP10 = await compute_top(10)
            await asyncio.sleep(POLL_SECONDS)

    asyncio.create_task(updater())
