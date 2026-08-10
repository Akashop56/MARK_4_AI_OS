package com.roninai.providers

import com.roninai.core.context.BrainContext
import com.roninai.data.security.ApiKeyVault
import com.roninai.data.settings.ProviderSettingsStore
import com.roninai.domain.model.AiProviderType
import com.roninai.domain.model.AiResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject

class AiProviderRouter(
    private val vault: ApiKeyVault,
    private val settings: ProviderSettingsStore,
    private val client: OkHttpClient = OkHttpClient()
) {
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    suspend fun think(context: BrainContext): Result<AiResponse> = withContext(Dispatchers.IO) {
        runCatching {
            val config = settings.currentConfig() ?: error("No active AI provider configured. Add a provider in Settings → AI Providers.")
            val apiKey = vault.get(config.type.name) ?: error("No API key is saved for ${config.type.name}. Add it in Settings → AI Providers.")
            when (config.type) {
                AiProviderType.Gemini -> callGemini(apiKey, config.model, context)
                AiProviderType.Groq -> callOpenAiCompatible("https://api.groq.com/openai/v1/chat/completions", apiKey, config.model, context)
                AiProviderType.OpenAI -> callOpenAiCompatible("https://api.openai.com/v1/chat/completions", apiKey, config.model, context)
                AiProviderType.Custom -> error("Custom providers are saved in settings but are not part of Phase 2 provider execution.")
            }
        }
    }

    private fun callGemini(apiKey: String, model: String, context: BrainContext): AiResponse {
        val body = JSONObject()
            .put("contents", JSONArray().put(JSONObject().put("parts", JSONArray().put(JSONObject().put("text", context.asPrompt())))))
            .toString()
            .toRequestBody(jsonMediaType)
        val request = Request.Builder()
            .url("https://generativelanguage.googleapis.com/v1beta/models/$model:generateContent")
            .header("x-goog-api-key", apiKey)
            .post(body)
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) error("Gemini request failed with HTTP ${response.code}")
            val payload = JSONObject(response.body?.string().orEmpty())
            val text = payload.optJSONArray("candidates")
                ?.optJSONObject(0)
                ?.optJSONObject("content")
                ?.optJSONArray("parts")
                ?.optJSONObject(0)
                ?.optString("text")
                .orEmpty()
            if (text.isBlank()) error("Gemini returned an empty response")
            return AiResponse(text.trim())
        }
    }

    private fun callOpenAiCompatible(url: String, apiKey: String, model: String, context: BrainContext): AiResponse {
        val messages = JSONArray()
            .put(JSONObject().put("role", "system").put("content", context.systemInstruction))
        context.conversation.forEach { message ->
            messages.put(JSONObject().put("role", if (message.role == "assistant") "assistant" else "user").put("content", message.content))
        }
        context.resolvedReference?.let { messages.put(JSONObject().put("role", "system").put("content", "Resolved context: $it")) }
        messages.put(JSONObject().put("role", "user").put("content", context.userInput))
        val body = JSONObject()
            .put("model", model)
            .put("messages", messages)
            .put("temperature", 0.4)
            .toString()
            .toRequestBody(jsonMediaType)
        val request = Request.Builder()
            .url(url)
            .header("Authorization", "Bearer $apiKey")
            .post(body)
            .build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) error("Provider request failed with HTTP ${response.code}")
            val payload = JSONObject(response.body?.string().orEmpty())
            val text = payload.optJSONArray("choices")
                ?.optJSONObject(0)
                ?.optJSONObject("message")
                ?.optString("content")
                .orEmpty()
            if (text.isBlank()) error("Provider returned an empty response")
            return AiResponse(text.trim())
        }
    }
}
