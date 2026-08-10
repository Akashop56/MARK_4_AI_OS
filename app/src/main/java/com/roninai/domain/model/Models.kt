package com.roninai.domain.model

import java.time.Instant

enum class RoninState { IDLE, LISTENING, THINKING, SPEAKING, ERROR }
enum class IntentType { Conversation, Question, Command, Preference, Correction, Unknown }
enum class AiProviderType { Gemini, Groq, OpenAI, Custom }
enum class InteractionClass { Conversation, Question, Command, LearningOpportunity, MemoryCandidate }
enum class MemoryCategory { Preference, Identity, Goal, Relationship, Correction, Experience, General }

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
    val continuity: ConversationContinuity,
    val extractedFacts: List<String>,
    val requiresPermission: Boolean
)

data class ConversationContinuity(
    val referencedMessageId: Long?,
    val topic: String?,
    val confidence: Double
)

data class ReasoningTrace(
    val facts: List<String>,
    val contextAnalysis: String,
    val possibleSolutions: List<String>,
    val decision: String,
    val confidence: Double,
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

data class ResponseAnalysis(
    val interactionClass: InteractionClass,
    val memoryCandidate: String?,
    val learningOpportunity: Boolean,
    val confidence: Double,
    val usefulnessSignals: List<String>
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
    val reason: String,
    val category: MemoryCategory,
    val importanceScore: Double,
    val usefulnessScore: Double
)

data class MemoryRanking(
    val memoryId: Long,
    val content: String,
    val category: MemoryCategory,
    val rankScore: Double
)

data class ReflectionResult(
    val useful: Boolean,
    val confidence: Double,
    val correctedByUser: Boolean,
    val futureBehaviorChange: String?
)


enum class VoiceLanguage(val speechTag: String) {
    English("en-IN"),
    Hindi("hi-IN"),
    Hinglish("en-IN")
}

data class VoicePreferences(
    val speed: Float = 0.95f,
    val pitch: Float = 1.0f,
    val language: VoiceLanguage = VoiceLanguage.Hinglish,
    val responseLength: ResponseLength = ResponseLength.Brief
)

enum class ResponseLength { Brief, Balanced, Detailed }

data class PerceptionSnapshot(
    val notificationsAvailable: Boolean = false,
    val deviceStateAvailable: Boolean = true,
    val environmentAvailable: Boolean = false,
    val batteryPercent: Int? = null,
    val charging: Boolean? = null
)
