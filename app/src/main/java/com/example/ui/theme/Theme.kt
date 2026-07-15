package com.example.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val DarkColorScheme = darkColorScheme(
    primary = CosmicPrimary,
    onPrimary = Color(0xFF0F172A), // Dark slate text on bright cyan
    secondary = CosmicSecondary,
    onSecondary = Color.White,
    tertiary = CosmicTertiary,
    onTertiary = Color.White,
    background = CosmicBackgroundDark,
    onBackground = TextOnDarkPrimary,
    surface = CosmicSurfaceDark,
    onSurface = TextOnDarkPrimary,
    surfaceVariant = CosmicBorderDark,
    onSurfaceVariant = TextOnDarkSecondary,
    outline = CosmicBorderDark
)

private val LightColorScheme = lightColorScheme(
    primary = CosmicSecondary,
    onPrimary = Color.White,
    secondary = CosmicPrimary,
    onSecondary = Color(0xFF0F172A),
    tertiary = CosmicTertiary,
    onTertiary = Color.White,
    background = CosmicBackgroundLight,
    onBackground = TextOnLightPrimary,
    surface = CosmicSurfaceLight,
    onSurface = TextOnLightPrimary,
    surfaceVariant = CosmicBorderLight,
    onSurfaceVariant = TextOnLightSecondary,
    outline = CosmicBorderLight
)

@Composable
fun MyApplicationTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
