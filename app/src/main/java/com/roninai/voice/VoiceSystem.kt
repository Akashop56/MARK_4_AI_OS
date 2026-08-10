package com.roninai.voice

import com.roninai.domain.model.RoninState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class VoiceSystem {
    private val _state = MutableStateFlow(RoninState.Idle)
    val state: StateFlow<RoninState> = _state
    val microphoneEnabled: Boolean get() = _state.value != RoninState.Speaking

    fun startListening() { if (microphoneEnabled) _state.value = RoninState.Listening }
    fun startThinking() { _state.value = RoninState.Thinking }
    fun startSpeaking() { _state.value = RoninState.Speaking }
    fun idle() { _state.value = RoninState.Idle }
}
