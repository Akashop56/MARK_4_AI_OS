package com.roninai.core.context

import com.roninai.domain.model.ChatMessage
import com.roninai.domain.model.UnderstandingResult

class ContextManager(private val maxContextMessages: Int = 12) {
    fun buildContext(understanding: UnderstandingResult, recentConversation: List<ChatMessage>): BrainContext {
        val relevantMessages = recentConversation.takeLast(maxContextMessages)
        return BrainContext(
            userInput = understanding.originalText,
            resolvedReference = understanding.resolvedContext,
            conversation = relevantMessages,
            systemInstruction = "You are RONIN AI, a newborn personal AI companion. Think clearly, respond naturally and briefly, use context, and never claim actions were performed without confirmation."
        )
    }
}

data class BrainContext(
    val userInput: String,
    val resolvedReference: String?,
    val conversation: List<ChatMessage>,
    val systemInstruction: String
) {
    fun asPrompt(): String = buildString {
        appendLine(systemInstruction)
        resolvedReference?.let { appendLine("Resolved context: $it") }
        appendLine("Recent conversation:")
        conversation.forEach { appendLine("${it.role}: ${it.content}") }
        appendLine("User input: $userInput")
    }
}
