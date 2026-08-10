package com.roninai.reasoning

import com.roninai.domain.model.IntentType
import com.roninai.domain.model.ReasoningTrace
import com.roninai.domain.model.UnderstandingResult

class ReasoningLayer {
    fun reason(understanding: UnderstandingResult): ReasoningTrace {
        val analysis = when (understanding.intent) {
            IntentType.Command -> "The input looks like an action request and must be confirmed before execution."
            IntentType.Preference -> "The input may be useful long-term memory and requires permission before saving."
            IntentType.Correction -> "The user is correcting RONIN, so this should become an experience record."
            IntentType.Conversation -> "The input is conversational and can use recent context."
            IntentType.Unknown -> "The input is empty or unclear."
        }
        return ReasoningTrace(
            analysis = analysis,
            decision = "Respond briefly, preserve context, and avoid unsafe silent actions.",
            safetyNote = if (understanding.requiresPermission) "Permission required before acting or saving." else null
        )
    }
}
