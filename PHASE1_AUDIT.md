# RONIN AI Phase 1 Verification and Stabilization

## Build Status

- Gradle project structure is present and uses Groovy build files to avoid Kotlin DSL runtime parsing issues on non-standard JDKs.
- Android compatibility target remains Android 13+ capable through `minSdk 23`, `targetSdk 35`, and JVM bytecode target 17.
- Local build is blocked in this container because the Android Gradle plugin cannot be resolved from Google Maven; direct network access to `dl.google.com` returns `403 Forbidden` from the environment proxy.

## Architecture Audit

Expected flow is preserved:

```text
UI -> ViewModel -> Domain/Core Brain -> Data-backed systems
```

- UI renders state and forwards user input only.
- ViewModel receives dependencies through a factory created in `MainActivity`.
- App-wide dependencies are centralized in `AppContainer`.
- UI does not directly access Room, DataStore, or encrypted key storage.

## Memory Audit

- Short-term memory is in-memory and bounded for low-RAM devices.
- Long-term memory saves only through `saveWithPermission`, and the DAO insert is guarded by `permissionGranted`.
- Room entities exist for long-term memories and experience records.

## AI Provider Audit

- API keys are stored with `EncryptedSharedPreferences` and an Android `MasterKey`.
- Public key display uses only a masked suffix.
- Active provider/model selection is stored in DataStore.
- Invalid stored provider names are ignored safely instead of throwing during startup.

## Brain Pipeline Audit

The current pipeline is:

```text
Input -> Understanding -> Reasoning -> Short-Term Memory -> Response
```

Long-term memory is intentionally permission-gated and not auto-written by the brain.

## Remaining Phase 1 Tasks

- Validate Android build on a machine with Android SDK, JDK 17, and access to Google Maven.
- Add focused unit/instrumentation tests once dependencies resolve.
- Wire explicit user confirmation UI before persisting long-term memory candidates.
