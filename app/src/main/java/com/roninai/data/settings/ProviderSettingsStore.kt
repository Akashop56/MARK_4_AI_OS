package com.roninai.data.settings

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.roninai.domain.model.AiProviderType
import com.roninai.domain.model.ProviderConfig
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.providerDataStore by preferencesDataStore("provider_settings")

class ProviderSettingsStore(private val context: Context) {
    private val activeProvider = stringPreferencesKey("active_provider")
    private val activeModel = stringPreferencesKey("active_model")

    val activeConfig: Flow<ProviderConfig?> = context.providerDataStore.data.map { prefs ->
        val providerName = prefs[activeProvider] ?: return@map null
        val type = AiProviderType.entries.firstOrNull { it.name == providerName } ?: return@map null
        ProviderConfig(type.name, type, type.name, prefs[activeModel] ?: "", "••••", active = true)
    }

    suspend fun setActive(type: AiProviderType, model: String) {
        context.providerDataStore.edit {
            it[activeProvider] = type.name
            it[activeModel] = model
        }
    }
}
