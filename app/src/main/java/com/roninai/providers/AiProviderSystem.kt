package com.roninai.providers

import com.roninai.data.security.ApiKeyVault
import com.roninai.data.settings.ProviderSettingsStore
import com.roninai.domain.model.AiProviderType
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request

class AiProviderSystem(
    private val vault: ApiKeyVault,
    private val settings: ProviderSettingsStore,
    private val client: OkHttpClient = OkHttpClient()
) {
    suspend fun saveKey(type: AiProviderType, key: String, model: String) {
        vault.save(type.name, key)
        settings.setActive(type, model)
    }

    fun deleteKey(type: AiProviderType) = vault.delete(type.name)
    fun maskedKey(type: AiProviderType): String = vault.mask(type.name)

    suspend fun testConnection(type: AiProviderType, customEndpoint: String? = null): Boolean = withContext(Dispatchers.IO) {
        val key = vault.get(type.name) ?: return@withContext false
        val url = when (type) {
            AiProviderType.OpenAI -> "https://api.openai.com/v1/models"
            AiProviderType.Groq -> "https://api.groq.com/openai/v1/models"
            AiProviderType.Gemini -> "https://generativelanguage.googleapis.com/v1beta/models?key=$key"
            AiProviderType.Custom -> customEndpoint ?: return@withContext false
        }
        val requestBuilder = Request.Builder().url(url)
        if (type != AiProviderType.Gemini) requestBuilder.header("Authorization", "Bearer $key")
        client.newCall(requestBuilder.build()).execute().use { it.isSuccessful }
    }
}
