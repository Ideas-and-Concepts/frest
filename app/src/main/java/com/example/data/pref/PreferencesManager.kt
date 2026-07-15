package com.example.data.pref

import android.content.Context
import android.content.SharedPreferences

class PreferencesManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences(
        "github_streamline_prefs",
        Context.MODE_PRIVATE
    )

    companion object {
        private const val KEY_GITHUB_TOKEN = "github_token"
        private const val KEY_FAVORITE_LANGUAGE = "favorite_language"
        private const val KEY_THEME_DARK = "theme_dark"
    }

    fun getGitHubToken(): String? {
        return prefs.getString(KEY_GITHUB_TOKEN, null)
    }

    fun saveGitHubToken(token: String?) {
        prefs.edit().putString(KEY_GITHUB_TOKEN, token?.trim()?.takeIf { it.isNotEmpty() }).apply()
    }

    fun getFavoriteLanguage(): String {
        return prefs.getString(KEY_FAVORITE_LANGUAGE, "All") ?: "All"
    }

    fun saveFavoriteLanguage(lang: String) {
        prefs.edit().putString(KEY_FAVORITE_LANGUAGE, lang).apply()
    }

    fun isDarkTheme(systemDefault: Boolean): Boolean {
        return prefs.getBoolean(KEY_THEME_DARK, systemDefault)
    }

    fun saveThemePreference(isDark: Boolean) {
        prefs.edit().putBoolean(KEY_THEME_DARK, isDark).apply()
    }
}
