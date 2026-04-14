package com.unifiedlogviewer.signals

import retrofit2.Call
import retrofit2.http.GET

interface ApiService {
    @GET("top")
    fun getTopCoins(): Call<List<CoinSignal>>
}
