# RONIN AI Phase 4 Voice and Perception Verification

## Files Changed

- Upgraded `VoiceSystem` with Android `SpeechRecognizer`, Android `TextToSpeech`, Hindi/English/Hinglish language selection, configurable speed/pitch/response length model support, and voice states `IDLE`, `LISTENING`, `THINKING`, `SPEAKING`, `ERROR`.
- Updated `MainViewModel` to preserve conversation context through voice transcripts, speak provider responses, release voice resources on lifecycle clear, and keep memory confirmation intact.
- Updated `MainScreen` with runtime microphone permission handling and no hidden recording path.
- Added `PerceptionSystem` as a passive foundation for future device/environment awareness without device automation or background services.

## Architecture Impact

The existing architecture is preserved:

```text
UI -> ViewModel -> Domain/Core Brain -> Data
```

- UI requests microphone permission and forwards mic events only.
- ViewModel coordinates voice events with the existing brain pipeline.
- Voice capture/speech is isolated in `VoiceSystem`.
- Perception is passive and does not start services, record audio, read notifications, or automate device actions.

## Testing Result

- Static Phase 4 checks pass for SpeechRecognizer/TextToSpeech usage, microphone permission handling, speaking-state mic pause, lifecycle release, no background service, and no hidden recording entry point.
- Android build remains environment-blocked because the container cannot resolve the Android Gradle plugin from Google Maven.

## Remaining Phase 4 Tasks

- Run on Android 13 / One UI Core 5.1 hardware to validate microphone permission prompts, STT locale behavior, and TTS output.
- Add instrumentation tests around lifecycle release and no self-hearing while speaking.
- Add settings UI later for voice preference editing without redesigning the main screen.
