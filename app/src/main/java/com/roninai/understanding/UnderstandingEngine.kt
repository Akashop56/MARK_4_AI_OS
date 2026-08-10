package com.roninai.understanding

import com.roninai.domain.model.ChatMessage
import com.roninai.domain.model.ConversationContinuity
import com.roninai.domain.model.IntentType
import com.roninai.domain.model.UnderstandingResult

class UnderstandingEngine {
    fun understand(input: String, recentConversation: List<ChatMessage>): UnderstandingResult {
        val normalized = input.trim()
        val facts = extractFacts(normalized)
        val continuity = resolveContinuity(normalized, recentConversation)
        val intent = inferIntent(normalized)
        return UnderstandingResult(
            originalText = normalized,
            intent = intent,
            resolvedContext = continuity.referencedMessageId?.let { id -> recentConversation.firstOrNull { it.id == id }?.content },
            continuity = continuity,
            extractedFacts = facts,
            requiresPermission = intent == IntentType.Command || intent == IntentType.Preference
        )
    }

    private fun inferIntent(text: String): IntentType {
        val lowered = text.lowercase()
        return when {
            text.isBlank() -> IntentType.Unknown
            lowered.contains("remember") || lowered.contains("i prefer") || lowered.contains("my favorite") -> IntentType.Preference
            lowered.contains("actually") || lowered.contains("correction") || lowered.startsWith("no,") -> IntentType.Correction
            lowered.startsWith("open") || lowered.startsWith("send") || lowered.startsWith("turn on") || lowered.startsWith("delete") -> IntentType.Command
            lowered.endsWith("?") || lowered.startsWith("what") || lowered.startsWith("why") || lowered.startsWith("how") || lowered.startsWith("can you explain") -> IntentType.Question
            else -> IntentType.Conversation
        }
    }

    private fun resolveContinuity(text: String, recentConversation: List<ChatMessage>): ConversationContinuity {
        val lowered = text.lowercase()
        val referenceWords = setOf("it", "that", "this", "there", "again", "same")
        val hasReference = lowered.split(Regex("\\s+")).any { it.trim('.', ',', '?', '!') in referenceWords }
        val referenced = if (hasReference) recentConversation.asReversed().firstOrNull { it.content.isNotBlank() } else null
        val topic = referenced?.content?.split(Regex("\\s+")).orEmpty().filter { it.length > 4 }.take(4).joinToString(" ").ifBlank { null }
        return ConversationContinuity(
            referencedMessageId = referenced?.id,
            topic = topic,
            confidence = when {
                referenced != null -> 0.72
                recentConversation.isNotEmpty() -> 0.45
                else -> 0.0
            }
        )
    }

    private fun extractFacts(text: String): List<String> {
        val lowered = text.lowercase()
        val facts = mutableListOf<String>()
        if ("my name is" in lowered) facts += text.substringAfter("my name is", "").trim().takeIf { it.isNotBlank() }?.let { "user_name=$it" }.orEmpty()
        if ("i prefer" in lowered) facts += text.substringAfter("i prefer", "").trim().takeIf { it.isNotBlank() }?.let { "preference=$it" }.orEmpty()
        if ("my favorite" in lowered) facts += text.substringAfter("my favorite", "").trim().takeIf { it.isNotBlank() }?.let { "favorite=$it" }.orEmpty()
        return facts.filter { it.isNotBlank() }
    }
}
