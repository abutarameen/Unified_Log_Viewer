package com.cryptmainica.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.lifecycle.viewmodel.compose.viewModel
import com.cryptmainica.app.ui.CoinDashboardScreen
import com.cryptmainica.app.ui.SignalViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val vm: SignalViewModel = viewModel()
            val state by vm.uiState.collectAsState()
            CoinDashboardScreen(state = state, onRefresh = vm::refresh)
        }
    }
}
