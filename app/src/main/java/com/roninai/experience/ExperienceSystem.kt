package com.roninai.experience

import com.roninai.data.db.ExperienceDao
import com.roninai.data.db.ExperienceEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first

class ExperienceSystem(private val dao: ExperienceDao) {
    fun observe(): Flow<List<ExperienceEntity>> = dao.observeAll()

    suspend fun record(
        problem: String,
        analysis: String,
        solution: String,
        futureImprovement: String,
        patternKey: String = patternKeyFor(problem, analysis),
        confidence: Double = 0.5
    ) {
        dao.insert(
            ExperienceEntity(
                problem = problem,
                analysis = analysis,
                solution = solution,
                futureImprovement = futureImprovement,
                patternKey = patternKey,
                confidence = confidence.coerceIn(0.0, 1.0)
            )
        )
    }

    suspend fun detectPatterns(): List<ExperiencePattern> {
        return dao.observeAll().first()
            .groupBy { it.patternKey }
            .filter { (_, experiences) -> experiences.size >= 2 }
            .map { (key, experiences) ->
                ExperiencePattern(
                    key = key,
                    occurrences = experiences.size,
                    suggestion = "Review repeated $key events and prefer the solution that succeeded most recently."
                )
            }
    }

    private fun patternKeyFor(problem: String, analysis: String): String {
        val text = "$problem $analysis".lowercase()
        return when {
            "provider" in text || "http" in text -> "provider_failure"
            "correction" in text || "correct" in text -> "user_correction"
            "preference" in text || "remember" in text -> "memory_preference"
            else -> "general"
        }
    }
}

data class ExperiencePattern(
    val key: String,
    val occurrences: Int,
    val suggestion: String
)
