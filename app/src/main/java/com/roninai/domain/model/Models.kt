package com.roninai.domain.model

import java.time.Instant

enum class RoninState { Idle, Listening, Thinking, Speaking }
enum class IntentType { Conversation, Command, Preference, Correction, Unknown }
enum class AiProviderType { Gemini, Groq, OpenAI, Custom }

data class ChatMessage(
    val id: Long = System.currentTimeMillis(),
    val role: String,
    val content: String,
    val createdAt: Instant = Instant.now()
)

data class UnderstandingResult(
    val originalText: String,
    val intent: IntentType,
    val resolvedContext: String?,
    val requiresPermission: Boolean
)

data class ReasoningTrace(
    val analysis: String,
    val decision: String,
    val safetyNote: String? = null
)

data class ProviderConfig(
    val id: String,
    val type: AiProviderType,
    val displayName: String,
    val model: String,
    val maskedKey: String,
    val endpoint: String? = null,
    val active: Boolean = false
)


enum class InteractionClass { Conversation, Question, Command, LearningOpportunity, MemoryCandidate }

data class ResponseAnalysis(
    val interactionClass: InteractionClass,
    val memoryCandidate: String?,
    val learningOpportunity: Boolean
)

data class AiRequest(
    val prompt: String,
    val model: String
)

data class AiResponse(
    val text: String
)


data class PendingMemoryCandidate(
    val content: String,
    val reason: String
)
