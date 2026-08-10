package com.roninai.ui.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.roninai.core.brain.RoninBrain
import com.roninai.domain.model.ChatMessage
import com.roninai.domain.model.PendingMemoryCandidate
import com.roninai.domain.model.RoninState
import com.roninai.memory.LongTermMemory
import com.roninai.memory.ShortTermMemory
import com.roninai.voice.VoiceSystem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class MainViewModel(
    private val brain: RoninBrain,
    private val shortTermMemory: ShortTermMemory,
    private val longTermMemory: LongTermMemory,
    private val voiceSystem: VoiceSystem
) : ViewModel() {
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()
    private val _pendingMemory = MutableStateFlow<PendingMemoryCandidate?>(null)
    val pendingMemory: StateFlow<PendingMemoryCandidate?> = _pendingMemory.asStateFlow()
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    val state: StateFlow<RoninState> = voiceSystem.state

    init {
        viewModelScope.launch {
            voiceSystem.transcript.collect { transcript ->
                if (!transcript.isNullOrBlank()) {
                    voiceSystem.consumeTranscript()
                    send(transcript)
                }
            }
        }
        viewModelScope.launch {
            voiceSystem.error.collect { voiceError ->
                if (!voiceError.isNullOrBlank()) _error.value = voiceError
            }
        }
    }

    fun send(text: String) {
        if (text.isBlank()) return
        viewModelScope.launch {
            voiceSystem.startThinking()
            _error.value = null
            runCatching { brain.processUserText(text) }
                .onSuccess { turn ->
                    _pendingMemory.value = turn.memoryCandidate
                    _messages.value = shortTermMemory.current
                    voiceSystem.speak(turn.message.content)
                }
                .onFailure { throwable ->
                    _error.value = throwable.message ?: "RONIN could not think through the active provider."
                    _messages.value = shortTermMemory.current
                    voiceSystem.idle()
                }
        }
    }

    fun confirmMemory(remember: Boolean) {
        val candidate = _pendingMemory.value ?: return
        viewModelScope.launch {
            longTermMemory.saveWithPermission(
                content = candidate.content,
                reason = candidate.reason,
                permissionGranted = remember,
                category = candidate.category,
                importanceScore = candidate.importanceScore,
                usefulnessScore = candidate.usefulnessScore
            )
            _pendingMemory.value = null
        }
    }

    fun toggleMic() {
        if (voiceSystem.microphoneEnabled) voiceSystem.startListening()
    }

    override fun onCleared() {
        voiceSystem.release()
        super.onCleared()
    }

    class Factory(
        private val brain: RoninBrain,
        private val shortTermMemory: ShortTermMemory,
        private val longTermMemory: LongTermMemory,
        private val voiceSystem: VoiceSystem
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            require(modelClass.isAssignableFrom(MainViewModel::class.java)) { "Unknown ViewModel: ${modelClass.name}" }
            return MainViewModel(brain, shortTermMemory, longTermMemory, voiceSystem) as T
        }
    }
}
