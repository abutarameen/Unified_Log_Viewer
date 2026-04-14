package com.cryptmainica.app.data

data class SignalCoin(
    val pair_address: String,
    val token_symbol: String,
    val token_name: String,
    val price_usd: Double,
    val volume_h24: Double,
    val liquidity_usd: Double,
    val buy_sell_ratio: Double,
    val score: Int,
    val signal: String,
    val risks: List<String>
)

data class UiState(
    val loading: Boolean = true,
    val items: List<SignalCoin> = emptyList(),
    val error: String? = null
)
