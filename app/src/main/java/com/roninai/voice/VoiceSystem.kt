package com.roninai.voice

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import androidx.core.content.ContextCompat
import com.roninai.domain.model.RoninState
import com.roninai.domain.model.VoiceLanguage
import com.roninai.domain.model.VoicePreferences
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.util.Locale

class VoiceSystem(private val context: Context) : TextToSpeech.OnInitListener {
    private val _state = MutableStateFlow(RoninState.IDLE)
    val state: StateFlow<RoninState> = _state
    private val _transcript = MutableStateFlow<String?>(null)
    val transcript: StateFlow<String?> = _transcript
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error
    private val _preferences = MutableStateFlow(VoicePreferences())
    val preferences: StateFlow<VoicePreferences> = _preferences

    private var textToSpeech: TextToSpeech? = TextToSpeech(context.applicationContext, this)
    private var speechRecognizer: SpeechRecognizer? = null
    val microphoneEnabled: Boolean get() = _state.value != RoninState.SPEAKING && _state.value != RoninState.THINKING

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            textToSpeech?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                override fun onStart(utteranceId: String?) { _state.value = RoninState.SPEAKING }
                override fun onDone(utteranceId: String?) { _state.value = RoninState.IDLE }
                @Deprecated("Deprecated in Android")
                override fun onError(utteranceId: String?) { fail("Text to speech playback failed") }
            })
            applyPreferences(_preferences.value)
        } else {
            fail("Text to speech unavailable")
        }
    }

    fun updatePreferences(preferences: VoicePreferences) {
        _preferences.value = preferences
        applyPreferences(preferences)
    }

    fun startListening() {
        if (!microphoneEnabled) return
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            fail("Microphone permission is required before listening.")
            return
        }
        if (!SpeechRecognizer.isRecognitionAvailable(context)) {
            fail("Speech recognition is not available on this device.")
            return
        }
        stopSpeaking()
        _error.value = null
        _state.value = RoninState.LISTENING
        val recognizer = speechRecognizer ?: SpeechRecognizer.createSpeechRecognizer(context.applicationContext).also { speechRecognizer = it }
        recognizer.setRecognitionListener(listener())
        recognizer.startListening(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, _preferences.value.language.speechTag)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        })
    }

    fun consumeTranscript(): String? = _transcript.value.also { _transcript.value = null }

    fun startThinking() {
        pauseMicrophoneForSpeechSafety()
        _state.value = RoninState.THINKING
    }

    fun speak(text: String) {
        if (text.isBlank()) {
            idle()
            return
        }
        pauseMicrophoneForSpeechSafety()
        _state.value = RoninState.SPEAKING
        textToSpeech?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "ronin-response-${System.currentTimeMillis()}") ?: fail("Text to speech unavailable")
    }

    fun stopSpeaking() {
        textToSpeech?.stop()
        if (_state.value == RoninState.SPEAKING) idle()
    }

    fun idle() { _state.value = RoninState.IDLE }

    fun release() {
        speechRecognizer?.destroy()
        speechRecognizer = null
        textToSpeech?.stop()
        textToSpeech?.shutdown()
        textToSpeech = null
        _state.value = RoninState.IDLE
    }

    private fun pauseMicrophoneForSpeechSafety() {
        speechRecognizer?.cancel()
        speechRecognizer?.destroy()
        speechRecognizer = null
    }

    private fun applyPreferences(preferences: VoicePreferences) {
        val locale = Locale.forLanguageTag(preferences.language.speechTag)
        textToSpeech?.language = locale
        textToSpeech?.setSpeechRate(preferences.speed.coerceIn(0.6f, 1.4f))
        textToSpeech?.setPitch(preferences.pitch.coerceIn(0.7f, 1.3f))
    }

    private fun listener(): RecognitionListener = object : RecognitionListener {
        override fun onReadyForSpeech(params: Bundle?) { _state.value = RoninState.LISTENING }
        override fun onBeginningOfSpeech() = Unit
        override fun onRmsChanged(rmsdB: Float) = Unit
        override fun onBufferReceived(buffer: ByteArray?) = Unit
        override fun onEndOfSpeech() { _state.value = RoninState.THINKING }
        override fun onError(error: Int) { fail("Speech recognition error: $error") }
        override fun onResults(results: Bundle?) {
            _transcript.value = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
            _state.value = RoninState.IDLE
        }
        override fun onPartialResults(partialResults: Bundle?) = Unit
        override fun onEvent(eventType: Int, params: Bundle?) = Unit
    }

    private fun fail(message: String) {
        _error.value = message
        _state.value = RoninState.ERROR
    }
}
