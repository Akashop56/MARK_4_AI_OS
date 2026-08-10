package com.roninai.learning

import com.roninai.domain.model.IntentType
import com.roninai.domain.model.UnderstandingResult

class LearningSystem {
    fun memoryCandidate(understanding: UnderstandingResult): String? =
        if (understanding.intent == IntentType.Preference) understanding.originalText else null

    fun experienceCandidate(understanding: UnderstandingResult): Boolean =
        understanding.intent == IntentType.Correction
}
