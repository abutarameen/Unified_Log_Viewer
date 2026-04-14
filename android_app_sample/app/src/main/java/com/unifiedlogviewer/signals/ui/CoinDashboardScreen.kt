package com.unifiedlogviewer.signals.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.unifiedlogviewer.signals.CoinSignal

@Composable
fun CoinDashboardScreen(coins: List<CoinSignal>) {
    if (coins.isEmpty()) {
        // Bugfix: Box requires a content lambda; keep modifier + centered content.
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0xFF111827)),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = "Waiting for live signals...",
                color = Color.White,
                style = MaterialTheme.typography.titleMedium,
            )
        }
        return
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF111827)),
        contentPadding = PaddingValues(12.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        items(coins, key = { it.pair_address }) { coin ->
            CoinCard(coin = coin)
        }
    }
}

@Composable
private fun CoinCard(coin: CoinSignal) {
    val signalColor = when (coin.signal) {
        "STRONG_BUY" -> Color(0xFF22C55E)
        "WATCH" -> Color(0xFFEAB308)
        "RISKY" -> Color(0xFFF97316)
        else -> Color(0xFFEF4444)
    }

    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(
                text = "${coin.token_name} (${coin.token_symbol})",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(text = "Score: ${coin.score}", color = signalColor)
            Text(text = "Price: $${coin.price_usd}")
            Text(text = "Volume(24h): $${coin.volume_h24}")
            Text(text = "Liquidity: $${coin.liquidity_usd}")
            Text(text = "Buy/Sell: ${coin.buy_sell_ratio}")
            if (coin.risk_flags.isNotEmpty()) {
                Text(text = "Risks: ${coin.risk_flags.joinToString()}", color = Color(0xFFDC2626))
            }
        }
    }
}
