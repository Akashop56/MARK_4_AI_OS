package com.roninai.memory

import com.roninai.data.db.LongTermMemoryDao
import com.roninai.data.db.LongTermMemoryEntity
import com.roninai.domain.model.ChatMessage
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
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

    suspend fun saveWithPermission(content: String, reason: String, permissionGranted: Boolean) {
        if (permissionGranted) dao.insert(LongTermMemoryEntity(content = content, reason = reason))
    }
}
