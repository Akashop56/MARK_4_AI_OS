package com.roninai.understanding

import com.roninai.domain.model.ChatMessage
import com.roninai.domain.model.IntentType
import com.roninai.domain.model.UnderstandingResult

class UnderstandingEngine {
    fun understand(input: String, recentConversation: List<ChatMessage>): UnderstandingResult {
        val normalized = input.trim()
        val previousContext = recentConversation.lastOrNull { it.role == "assistant" || it.role == "user" }?.content
        val intent = when {
            normalized.contains("remember", ignoreCase = true) -> IntentType.Preference
            normalized.contains("actually", ignoreCase = true) || normalized.contains("correction", ignoreCase = true) -> IntentType.Correction
            normalized.startsWith("open", ignoreCase = true) -> IntentType.Command
            normalized.isBlank() -> IntentType.Unknown
            else -> IntentType.Conversation
        }
        val resolved = if (normalized.equals("open it", true) || normalized.equals("do it", true)) previousContext else null
        return UnderstandingResult(
            originalText = normalized,
            intent = intent,
            resolvedContext = resolved,
            requiresPermission = intent == IntentType.Command || intent == IntentType.Preference
        )
    }
}
