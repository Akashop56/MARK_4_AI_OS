package com.roninai.ui.screens

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.roninai.core.brain.RoninBrain
import com.roninai.domain.model.ChatMessage
import com.roninai.domain.model.RoninState
import com.roninai.memory.ShortTermMemory
import com.roninai.voice.VoiceSystem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class MainViewModel(
    private val brain: RoninBrain,
    private val shortTermMemory: ShortTermMemory,
    private val voiceSystem: VoiceSystem
) : ViewModel() {
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()
    val state: StateFlow<RoninState> = voiceSystem.state

    fun send(text: String) {
        if (text.isBlank()) return
        voiceSystem.startThinking()
        brain.processUserText(text)
        _messages.value = shortTermMemory.current
        voiceSystem.idle()
    }

    fun toggleMic() {
        if (voiceSystem.microphoneEnabled) voiceSystem.startListening()
    }

    class Factory(
        private val brain: RoninBrain,
        private val shortTermMemory: ShortTermMemory,
        private val voiceSystem: VoiceSystem
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            require(modelClass.isAssignableFrom(MainViewModel::class.java)) { "Unknown ViewModel: ${modelClass.name}" }
            return MainViewModel(brain, shortTermMemory, voiceSystem) as T
        }
    }
}
