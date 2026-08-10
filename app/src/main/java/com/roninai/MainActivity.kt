package com.roninai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.lifecycle.viewmodel.compose.viewModel
import com.roninai.ui.screens.MainScreen
import com.roninai.ui.screens.MainViewModel
import com.roninai.ui.theme.RoninTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val container = (application as RoninApplication).container
        val factory = MainViewModel.Factory(container.brain, container.shortTermMemory, container.longTermMemory, container.voiceSystem)
        setContent {
            RoninTheme {
                MainScreen(viewModel = viewModel(factory = factory))
            }
        }
    }
}
