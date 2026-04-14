package com.cryptmainica.app.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.cryptmainica.app.data.NetworkModule
import com.cryptmainica.app.data.SafeWebSocketListener
import com.cryptmainica.app.data.SignalCoin
import com.cryptmainica.app.data.UiState
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import okhttp3.Response
import okhttp3.WebSocket

class SignalViewModel : ViewModel() {
    private val gson = Gson()
    private var socket: WebSocket? = null

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState

    init {
        refresh()
        connectSocket()
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(loading = true, error = null) }
            runCatching { NetworkModule.api.topSignals() }
                .onSuccess { rows -> _uiState.update { it.copy(loading = false, items = rows, error = null) } }
                .onFailure { e -> _uiState.update { it.copy(loading = false, error = e.message ?: "Request failed") } }
        }
    }

    private fun connectSocket() {
        socket = NetworkModule.connectSignals(object : SafeWebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val type = object : TypeToken<List<SignalCoin>>() {}.type
                val rows: List<SignalCoin> = gson.fromJson(text, type)
                _uiState.update { it.copy(items = rows, loading = false, error = null) }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _uiState.update { it.copy(error = t.message ?: "WebSocket failed") }
            }
        })
    }

    override fun onCleared() {
        socket?.close(1000, "closing")
        socket = null
        super.onCleared()
    }
}
