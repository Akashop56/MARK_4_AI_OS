package com.roninai.core.brain

import com.roninai.core.context.ContextManager
import com.roninai.core.response.ResponseAnalyzer
import com.roninai.domain.model.ChatMessage
import com.roninai.domain.model.PendingMemoryCandidate
import com.roninai.experience.ExperienceSystem
import com.roninai.learning.LearningSystem
import com.roninai.memory.MemoryScorer
import com.roninai.memory.ShortTermMemory
import com.roninai.providers.AiProviderRouter
import com.roninai.reasoning.ReasoningLayer
import com.roninai.understanding.UnderstandingEngine

class RoninBrain(
    private val understandingEngine: UnderstandingEngine,
    private val contextManager: ContextManager,
    private val aiProviderRouter: AiProviderRouter,
    private val responseAnalyzer: ResponseAnalyzer,
    private val reasoningLayer: ReasoningLayer,
    private val learningSystem: LearningSystem,
    private val shortTermMemory: ShortTermMemory,
    private val experienceSystem: ExperienceSystem
) {
    suspend fun processUserText(input: String): BrainTurn {
        val userMessage = ChatMessage(role = "user", content = input)
        shortTermMemory.add(userMessage)

        val understanding = understandingEngine.understand(input, shortTermMemory.current)
        val reasoning = reasoningLayer.reason(understanding)
        val brainContext = contextManager.buildContext(understanding, reasoning, shortTermMemory.current)

        val aiResult = aiProviderRouter.think(brainContext)
        val responseText = aiResult.getOrElse { error ->
            experienceSystem.record(
                problem = "AI provider request failed",
                analysis = error.message ?: "Unknown provider error",
                solution = "Keep the conversation state stable and ask the user to verify provider settings.",
                futureImprovement = "Retry with another active provider only after user approval.",
                patternKey = "provider_failure",
                confidence = reasoning.confidence
            )
            throw error
        }.text

        val assistantMessage = ChatMessage(role = "assistant", content = responseText)
        shortTermMemory.add(assistantMessage)
        val responseAnalysis = responseAnalyzer.analyze(understanding, responseText)
        val reflection = learningSystem.reflect(understanding, responseAnalysis, responseText)
        experienceSystem.record(
            problem = "Self reflection after response",
            analysis = "useful=${reflection.useful}; confidence=${reflection.confidence}; corrected=${reflection.correctedByUser}",
            solution = reflection.futureBehaviorChange ?: "Keep current behavior for similar context.",
            futureImprovement = reflection.futureBehaviorChange ?: "Continue monitoring future corrections and usefulness signals.",
            patternKey = if (reflection.correctedByUser) "user_correction" else "self_reflection",
            confidence = reflection.confidence
        )
        val memoryCandidate = responseAnalysis.memoryCandidate?.let { candidate ->
            PendingMemoryCandidate(
                content = candidate,
                reason = "Classified as ${responseAnalysis.interactionClass}; confidence=${responseAnalysis.confidence}",
                category = MemoryScorer.category(candidate),
                importanceScore = MemoryScorer.importance(candidate),
                usefulnessScore = MemoryScorer.usefulness(candidate)
            )
        }
        return BrainTurn(message = assistantMessage, memoryCandidate = memoryCandidate)
    }
}

data class BrainTurn(
    val message: ChatMessage,
    val memoryCandidate: PendingMemoryCandidate?
)
