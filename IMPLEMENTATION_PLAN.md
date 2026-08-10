# RONIN AI Android Implementation Plan

RONIN AI is designed as a newborn digital mind: stable understanding, memory, experience, learning, and reasoning first; richer assistant abilities later.

## Architecture

```text
RONIN AI
├── Core Brain          - Orchestrates understanding, reasoning, memory, provider calls, and learning.
├── Understanding      - Resolves user intent, context, references, and conversation meaning.
├── Memory System      - Short-term conversation context and permission-gated long-term memory.
├── Experience System  - Stores problem → analysis → solution → future improvement records.
├── Learning System    - Converts corrections/failures/successes into candidate memories/experiences.
├── Reasoning Layer    - Explains decisions and connects facts before actions.
├── AI Providers       - Gemini, Groq, OpenAI, and custom endpoint settings with encrypted keys.
├── Voice System       - Idle/listening/thinking/speaking state model for STT/TTS integration.
├── Device Tools       - Safety-gated device action interface for future tools.
└── User Interface     - Futuristic dark Compose UI with core animation and simple menus.
```

## Build Phases

1. **Phase 1 — Newborn Brain:** create modular package structure, dark Compose shell, core state model, understanding, reasoning, and safety-first orchestration.
2. **Phase 2 — AI Provider Connection:** add provider settings, encrypted API-key storage, active model selection, and connection test abstraction.
3. **Phase 3 — Memory:** add short-term in-memory context and Room-backed long-term memory requiring user permission before saving.
4. **Phase 4 — Experience Learning:** add Room-backed experience records for successes, failures, and corrections.
5. **Phase 5 — Voice:** add microphone/TTS state model and UI safety guard that disables input while speaking.
6. **Phase 6 — Device Tools:** add permission-gated tool contracts; no dangerous silent actions.

## Version 0.1 Scope

This initial commit builds the stable foundation and intentionally avoids fake hardcoded AI answers. If no provider is configured, RONIN explains that a provider must be added in settings before cloud reasoning can occur.
