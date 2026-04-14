package com.unifiedlogviewer.signals

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

class CoinAdapter : RecyclerView.Adapter<CoinAdapter.CoinViewHolder>() {
    private val items = mutableListOf<CoinSignal>()

    fun submitList(newItems: List<CoinSignal>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CoinViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_coin, parent, false)
        return CoinViewHolder(view)
    }

    override fun getItemCount(): Int = items.size

    override fun onBindViewHolder(holder: CoinViewHolder, position: Int) {
        holder.bind(items[position])
    }

    class CoinViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val name: TextView = itemView.findViewById(R.id.name)
        private val score: TextView = itemView.findViewById(R.id.score)
        private val signal: TextView = itemView.findViewById(R.id.signal)
        private val details: TextView = itemView.findViewById(R.id.details)

        fun bind(coin: CoinSignal) {
            name.text = "${coin.token_name} (${coin.token_symbol})"
            score.text = "Score: ${coin.score}"
            details.text = "Vol: ${coin.volume_h24} | Liq: ${coin.liquidity_usd} | B/S: ${coin.buy_sell_ratio}"
            signal.text = when (coin.signal) {
                "STRONG_BUY" -> "🚀 BUY"
                "WATCH" -> "⚡ WATCH"
                "RISKY" -> "⚠️ RISKY"
                else -> "❌ AVOID"
            }
            signal.setTextColor(
                when (coin.signal) {
                    "STRONG_BUY" -> Color.parseColor("#1B5E20")
                    "WATCH" -> Color.parseColor("#F57F17")
                    else -> Color.parseColor("#B71C1C")
                }
            )
        }
    }
}
