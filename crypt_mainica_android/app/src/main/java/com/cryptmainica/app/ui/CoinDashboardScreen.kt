package com.cryptmainica.app.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.cryptmainica.app.data.SignalCoin
import com.cryptmainica.app.data.UiState

@Composable
fun CoinDashboardScreen(state: UiState, onRefresh: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0B1020)),
        contentAlignment = Alignment.Center,
    ) {
        when {
            state.loading -> CircularProgressIndicator()
            state.items.isEmpty() -> EmptyState(state.error, onRefresh)
            else -> CoinList(state.items, onRefresh)
        }
    }
}

@Composable
private fun EmptyState(error: String?, onRefresh: () -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = error ?: "No live signals yet",
            color = Color.White,
            style = MaterialTheme.typography.titleMedium,
        )
        Button(onClick = onRefresh, modifier = Modifier.padding(top = 12.dp)) {
            Text("Retry")
        }
    }
}

@Composable
private fun CoinList(items: List<SignalCoin>, onRefresh: () -> Unit) {
    Column(modifier = Modifier.fillMaxSize().padding(12.dp)) {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(text = "Crypt Mainica", color = Color.White, fontWeight = FontWeight.Bold)
            Button(onClick = onRefresh) { Text("Refresh") }
        }
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 8.dp)) {
            items(items, key = { it.pair_address }) { coin ->
                CoinCard(coin)
            }
        }
    }
}

@Composable
private fun CoinCard(coin: SignalCoin) {
    val signalColor = when (coin.signal) {
        "STRONG_BUY" -> Color(0xFF22C55E)
        "WATCH" -> Color(0xFFEAB308)
        "RISKY" -> Color(0xFFF97316)
        else -> Color(0xFFEF4444)
    }

    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("${coin.token_name} (${coin.token_symbol})", fontWeight = FontWeight.Bold)
            Text("Score: ${coin.score}", color = signalColor)
            Text("Price: $${coin.price_usd}")
            Text("Volume: $${coin.volume_h24}")
            Text("Liquidity: $${coin.liquidity_usd}")
            Text("Buy/Sell: ${coin.buy_sell_ratio}")
            if (coin.risks.isNotEmpty()) {
                Text("Risk: ${coin.risks.joinToString()}", color = Color(0xFFDC2626))
            }
        }
    }
}
