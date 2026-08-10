package com.roninai.core.brain

import com.roninai.core.context.ContextManager
import com.roninai.core.response.ResponseAnalyzer
import com.roninai.domain.model.ChatMessage
import com.roninai.domain.model.PendingMemoryCandidate
import com.roninai.experience.ExperienceSystem
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
    private val shortTermMemory: ShortTermMemory,
    private val experienceSystem: ExperienceSystem
) {
    suspend fun processUserText(input: String): BrainTurn {
        val userMessage = ChatMessage(role = "user", content = input)
        shortTermMemory.add(userMessage)

        val understanding = understandingEngine.understand(input, shortTermMemory.current)
        reasoningLayer.reason(understanding)
        val brainContext = contextManager.buildContext(understanding, shortTermMemory.current)

        val aiResult = aiProviderRouter.think(brainContext)
        val responseText = aiResult.getOrElse { error ->
            experienceSystem.record(
                problem = "AI provider request failed",
                analysis = error.message ?: "Unknown provider error",
                solution = "Keep the conversation state stable and ask the user to verify provider settings.",
                futureImprovement = "Retry with another active provider only after user approval."
            )
            throw error
        }.text

        val assistantMessage = ChatMessage(role = "assistant", content = responseText)
        shortTermMemory.add(assistantMessage)
        val analysis = responseAnalyzer.analyze(understanding, responseText)
        val memoryCandidate = analysis.memoryCandidate?.let { candidate ->
            PendingMemoryCandidate(content = candidate, reason = "Classified as ${analysis.interactionClass}")
        }
        return BrainTurn(message = assistantMessage, memoryCandidate = memoryCandidate)
    }
}

data class BrainTurn(
    val message: ChatMessage,
    val memoryCandidate: PendingMemoryCandidate?
)
