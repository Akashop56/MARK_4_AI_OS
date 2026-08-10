package com.roninai.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val RoninColors = darkColorScheme(
    primary = Color(0xFF70F6FF),
    secondary = Color(0xFF9B7CFF),
    background = Color(0xFF05070D),
    surface = Color(0xFF101522),
    onPrimary = Color.Black,
    onBackground = Color(0xFFE8F7FF),
    onSurface = Color(0xFFE8F7FF)
)

@Composable
fun RoninTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = RoninColors, content = content)
}
