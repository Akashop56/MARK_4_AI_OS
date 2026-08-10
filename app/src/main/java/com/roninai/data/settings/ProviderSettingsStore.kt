package com.roninai.data.settings

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.roninai.domain.model.AiProviderType
import com.roninai.domain.model.ProviderConfig
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.providerDataStore by preferencesDataStore("provider_settings")

class ProviderSettingsStore(private val context: Context) {
    private val activeProvider = stringPreferencesKey("active_provider")
    private val activeModel = stringPreferencesKey("active_model")

    val activeConfig: Flow<ProviderConfig?> = context.providerDataStore.data.map { prefs ->
        prefs.toProviderConfig()
    }

    suspend fun currentConfig(): ProviderConfig? = context.providerDataStore.data.first().toProviderConfig()

    suspend fun setActive(type: AiProviderType, model: String) {
        context.providerDataStore.edit {
            it[activeProvider] = type.name
            it[activeModel] = model
        }
    }

    private fun androidx.datastore.preferences.core.Preferences.toProviderConfig(): ProviderConfig? {
        val providerName = this[activeProvider] ?: return null
        val type = AiProviderType.entries.firstOrNull { it.name == providerName } ?: return null
        return ProviderConfig(type.name, type, type.name, this[activeModel] ?: defaultModel(type), "••••", active = true)
    }

    private fun defaultModel(type: AiProviderType): String = when (type) {
        AiProviderType.Gemini -> "gemini-1.5-flash"
        AiProviderType.Groq -> "llama-3.1-8b-instant"
        AiProviderType.OpenAI -> "gpt-4o-mini"
        AiProviderType.Custom -> ""
    }
}
