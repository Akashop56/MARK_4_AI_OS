package com.roninai.reasoning

import com.roninai.domain.model.IntentType
import com.roninai.domain.model.ReasoningTrace
import com.roninai.domain.model.UnderstandingResult

class ReasoningLayer {
    fun reason(understanding: UnderstandingResult): ReasoningTrace {
        val facts = understanding.extractedFacts
        val contextAnalysis = buildContextAnalysis(understanding)
        val possibleSolutions = possibleSolutionsFor(understanding)
        val decision = possibleSolutions.firstOrNull() ?: "Ask for clarification before proceeding."
        val confidence = listOf(
            if (understanding.intent == IntentType.Unknown) 0.15 else 0.45,
            understanding.continuity.confidence * 0.25,
            if (facts.isNotEmpty()) 0.2 else 0.0,
            if (understanding.originalText.length > 6) 0.1 else 0.0
        ).sum().coerceIn(0.0, 0.95)
        return ReasoningTrace(
            facts = facts,
            contextAnalysis = contextAnalysis,
            possibleSolutions = possibleSolutions,
            decision = decision,
            confidence = confidence,
            safetyNote = if (understanding.requiresPermission) "Permission required before acting or saving." else null
        )
    }

    private fun buildContextAnalysis(understanding: UnderstandingResult): String = buildString {
        append("Intent=${understanding.intent}")
        understanding.continuity.topic?.let { append(", continuing topic=$it") }
        if (understanding.extractedFacts.isNotEmpty()) append(", facts=${understanding.extractedFacts.size}")
    }

    private fun possibleSolutionsFor(understanding: UnderstandingResult): List<String> = when (understanding.intent) {
        IntentType.Command -> listOf("Confirm the action before execution.", "Ask what object/action is intended if the reference is unclear.")
        IntentType.Preference -> listOf("Ask whether this should become long-term memory.", "Keep it only in short-term memory if declined.")
        IntentType.Correction -> listOf("Acknowledge correction and store a learning experience.", "Adjust future behavior if the pattern repeats.")
        IntentType.Question -> listOf("Answer using provider reasoning and current context.", "Ask a follow-up if facts are insufficient.")
        IntentType.Conversation -> listOf("Continue naturally using recent context.", "Extract useful preferences without saving silently.")
        IntentType.Unknown -> listOf("Ask for a clearer signal.")
    }
}
