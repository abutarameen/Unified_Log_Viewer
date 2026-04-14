package com.unifiedlogviewer.signals

data class CoinSignal(
    val pair_address: String,
    val token_symbol: String,
    val token_name: String,
    val price_usd: Double,
    val liquidity_usd: Double,
    val volume_h24: Double,
    val buy_sell_ratio: Double,
    val score: Int,
    val signal: String,
    val risk_flags: List<String>
)
