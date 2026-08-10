package com.roninai.ui.screens

import androidx.lifecycle.ViewModel
import com.roninai.core.brain.RoninBrain
import com.roninai.domain.model.ChatMessage
import com.roninai.domain.model.RoninState
import com.roninai.memory.ShortTermMemory
import com.roninai.reasoning.ReasoningLayer
import com.roninai.understanding.UnderstandingEngine
import com.roninai.voice.VoiceSystem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class MainViewModel : ViewModel() {
    private val shortTermMemory = ShortTermMemory()
    private val voiceSystem = VoiceSystem()
    private val brain = RoninBrain(UnderstandingEngine(), ReasoningLayer(), shortTermMemory)
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()
    val state: StateFlow<RoninState> = voiceSystem.state

    fun send(text: String) {
        if (text.isBlank()) return
        voiceSystem.startThinking()
        val reply = brain.processUserText(text)
        _messages.value = shortTermMemory.current
        voiceSystem.idle()
    }

    fun toggleMic() {
        if (voiceSystem.microphoneEnabled) voiceSystem.startListening()
    }
}
