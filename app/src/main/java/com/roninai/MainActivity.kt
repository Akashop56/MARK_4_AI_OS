package com.roninai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.roninai.ui.screens.MainScreen
import com.roninai.ui.theme.RoninTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { RoninTheme { MainScreen() } }
    }
}
