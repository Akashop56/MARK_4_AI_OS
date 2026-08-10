package com.roninai.core.response

import com.roninai.domain.model.InteractionClass
import com.roninai.domain.model.IntentType
import com.roninai.domain.model.ResponseAnalysis
import com.roninai.domain.model.UnderstandingResult

class ResponseAnalyzer {
    fun analyze(understanding: UnderstandingResult, response: String): ResponseAnalysis {
        val loweredInput = understanding.originalText.lowercase()
        val loweredResponse = response.lowercase()
        val interactionClass = when {
            understanding.intent == IntentType.Command -> InteractionClass.Command
            understanding.intent == IntentType.Preference -> InteractionClass.MemoryCandidate
            understanding.intent == IntentType.Correction -> InteractionClass.LearningOpportunity
            loweredInput.endsWith("?") || loweredInput.startsWith("what") || loweredInput.startsWith("why") || loweredInput.startsWith("how") -> InteractionClass.Question
            else -> InteractionClass.Conversation
        }
        val memoryCandidate = when {
            interactionClass == InteractionClass.MemoryCandidate -> understanding.originalText
            "remember" in loweredResponse || "preference" in loweredResponse -> understanding.originalText.takeIf { it.length in 8..240 }
            else -> null
        }
        return ResponseAnalysis(
            interactionClass = interactionClass,
            memoryCandidate = memoryCandidate,
            learningOpportunity = interactionClass == InteractionClass.LearningOpportunity
        )
    }
}
