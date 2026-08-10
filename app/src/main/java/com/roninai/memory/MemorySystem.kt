package com.roninai.memory

import com.roninai.data.db.LongTermMemoryDao
import com.roninai.data.db.LongTermMemoryEntity
import com.roninai.domain.model.ChatMessage
import com.roninai.domain.model.MemoryCategory
import com.roninai.domain.model.MemoryRanking
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update

class ShortTermMemory(private val maxMessages: Int = 24) {
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: Flow<List<ChatMessage>> = _messages
    val current: List<ChatMessage> get() = _messages.value

    fun add(message: ChatMessage) {
        _messages.update { (it + message).takeLast(maxMessages) }
    }
}

class LongTermMemory(private val dao: LongTermMemoryDao) {
    fun observe(): Flow<List<LongTermMemoryEntity>> = dao.observeAll()

    suspend fun saveWithPermission(
        content: String,
        reason: String,
        permissionGranted: Boolean,
        category: MemoryCategory = MemoryCategory.General,
        importanceScore: Double = MemoryScorer.importance(content),
        usefulnessScore: Double = MemoryScorer.usefulness(content)
    ) {
        if (permissionGranted) {
            dao.insert(
                LongTermMemoryEntity(
                    content = content,
                    reason = reason,
                    category = category.name,
                    importanceScore = importanceScore.coerceIn(0.0, 1.0),
                    usefulnessScore = usefulnessScore.coerceIn(0.0, 1.0)
                )
            )
        }
    }

    suspend fun rankedFor(query: String, limit: Int = 5): List<MemoryRanking> {
        val queryTerms = query.lowercase().split(Regex("\\s+")).filter { it.length > 2 }.toSet()
        return dao.observeAll().first().map { memory ->
            val overlap = memory.content.lowercase().split(Regex("\\s+")).count { it in queryTerms }
            val recencyBoost = 1.0 / (1.0 + ((System.currentTimeMillis() - memory.createdAt).coerceAtLeast(0L) / 86_400_000.0))
            val rank = memory.importanceScore * 0.45 + memory.usefulnessScore * 0.35 + overlap * 0.12 + recencyBoost * 0.08
            MemoryRanking(
                memoryId = memory.id,
                content = memory.content,
                category = runCatching { MemoryCategory.valueOf(memory.category) }.getOrDefault(MemoryCategory.General),
                rankScore = rank
            )
        }.sortedByDescending { it.rankScore }.take(limit)
    }
}

object MemoryScorer {
    fun category(content: String): MemoryCategory {
        val lowered = content.lowercase()
        return when {
            "prefer" in lowered || "favorite" in lowered -> MemoryCategory.Preference
            "my name is" in lowered || "i am" in lowered -> MemoryCategory.Identity
            "goal" in lowered || "want to" in lowered -> MemoryCategory.Goal
            "actually" in lowered || "correction" in lowered -> MemoryCategory.Correction
            else -> MemoryCategory.General
        }
    }

    fun importance(content: String): Double {
        val lowered = content.lowercase()
        var score = 0.25
        if ("my name is" in lowered || "i prefer" in lowered || "my favorite" in lowered) score += 0.35
        if ("always" in lowered || "never" in lowered || "important" in lowered) score += 0.25
        if (content.length in 12..180) score += 0.15
        return score.coerceIn(0.0, 1.0)
    }

    fun usefulness(content: String): Double {
        val lowered = content.lowercase()
        var score = 0.2
        if ("prefer" in lowered || "remember" in lowered) score += 0.3
        if ("because" in lowered || "when" in lowered) score += 0.2
        if (content.split(Regex("\\s+")).size >= 4) score += 0.2
        return score.coerceIn(0.0, 1.0)
    }
}
