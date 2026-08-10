package com.roninai.data.security

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class ApiKeyVault(context: Context) {
    private val prefs = EncryptedSharedPreferences.create(
        context,
        "ronin_api_keys",
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun save(providerId: String, apiKey: String) = prefs.edit().putString(providerId, apiKey).apply()
    fun get(providerId: String): String? = prefs.getString(providerId, null)
    fun delete(providerId: String) = prefs.edit().remove(providerId).apply()
    fun mask(providerId: String): String = get(providerId)?.let { "••••" + it.takeLast(4) } ?: "No key"
}
