package com.roninai.learning

import com.roninai.domain.model.IntentType
import com.roninai.domain.model.ReflectionResult
import com.roninai.domain.model.ResponseAnalysis
import com.roninai.domain.model.UnderstandingResult

class LearningSystem {
    fun memoryCandidate(understanding: UnderstandingResult): String? =
        if (understanding.intent == IntentType.Preference) understanding.originalText else null

    fun experienceCandidate(understanding: UnderstandingResult): Boolean =
        understanding.intent == IntentType.Correction

    fun reflect(understanding: UnderstandingResult, responseAnalysis: ResponseAnalysis, responseText: String): ReflectionResult {
        val usefulSignals = responseAnalysis.usefulnessSignals.size
        val responseHasSubstance = responseText.trim().split(Regex("\\s+")).size >= 3
        val corrected = understanding.intent == IntentType.Correction
        val confidence = listOf(
            responseAnalysis.confidence,
            if (responseHasSubstance) 0.15 else -0.15,
            usefulSignals * 0.05,
            if (corrected) -0.25 else 0.0
        ).sum().coerceIn(0.0, 1.0)
        return ReflectionResult(
            useful = confidence >= 0.55 && !corrected,
            confidence = confidence,
            correctedByUser = corrected,
            futureBehaviorChange = when {
                corrected -> "Apply the user correction in future similar contexts."
                confidence < 0.45 -> "Ask a clarifying question before answering with low context confidence."
                else -> null
            }
        )
    }
}
