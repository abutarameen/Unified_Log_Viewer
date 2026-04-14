package com.cryptmainica.app.data

import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET

interface SignalApi {
    @GET("signals/top")
    suspend fun topSignals(): List<SignalCoin>
}

object NetworkModule {
    // Change this to your machine IP when running on a physical device/emulator.
    const val BASE_HTTP = "http://10.0.2.2:8000/"
    const val BASE_WS = "ws://10.0.2.2:8000/signals/ws"

    val api: SignalApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_HTTP)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(SignalApi::class.java)
    }

    fun connectSignals(listener: WebSocketListener): WebSocket {
        val client = OkHttpClient()
        val request = Request.Builder().url(BASE_WS).build()
        return client.newWebSocket(request, listener)
    }
}

open class SafeWebSocketListener : WebSocketListener() {
    override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
        // no-op; handled in ViewModel
    }
}
