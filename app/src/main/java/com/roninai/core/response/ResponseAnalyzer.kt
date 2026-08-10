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
            understanding.intent == IntentType.Question || loweredInput.endsWith("?") -> InteractionClass.Question
            else -> InteractionClass.Conversation
        }
        val usefulnessSignals = buildList {
            if (response.length in 12..1200) add("substantive_length")
            if (understanding.resolvedContext != null) add("used_context")
            if (understanding.extractedFacts.isNotEmpty()) add("fact_aware")
            if ("should i" in loweredResponse || "confirm" in loweredResponse) add("permission_aware")
        }
        val memoryCandidate = when {
            interactionClass == InteractionClass.MemoryCandidate -> understanding.originalText
            "remember" in loweredResponse || "preference" in loweredResponse -> understanding.originalText.takeIf { it.length in 8..240 }
            else -> null
        }
        val confidence = (0.35 + usefulnessSignals.size * 0.12 + understanding.continuity.confidence * 0.2).coerceIn(0.0, 0.95)
        return ResponseAnalysis(
            interactionClass = interactionClass,
            memoryCandidate = memoryCandidate,
            learningOpportunity = interactionClass == InteractionClass.LearningOpportunity,
            confidence = confidence,
            usefulnessSignals = usefulnessSignals
        )
    }
}
