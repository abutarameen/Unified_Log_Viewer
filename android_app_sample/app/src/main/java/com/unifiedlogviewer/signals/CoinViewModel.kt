package com.unifiedlogviewer.signals

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener

class CoinViewModel : ViewModel() {
    private val _coins = MutableLiveData<List<CoinSignal>>(emptyList())
    val coins: LiveData<List<CoinSignal>> = _coins

    private val gson = Gson()
    private var socket: WebSocket? = null

    fun connectWebSocket(baseWsUrl: String) {
        val client = OkHttpClient()
        val request = Request.Builder().url("$baseWsUrl/ws").build()

        socket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val listType = object : TypeToken<List<CoinSignal>>() {}.type
                val payload: List<CoinSignal> = gson.fromJson(text, listType)
                _coins.postValue(payload)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                // production: add reconnection/backoff strategy
            }
        })
    }

    override fun onCleared() {
        socket?.close(1000, "ViewModel cleared")
        socket = null
        super.onCleared()
    }
}
