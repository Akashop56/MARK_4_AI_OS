package com.roninai.core.brain

import com.roninai.domain.model.ChatMessage
import com.roninai.domain.model.IntentType
import com.roninai.memory.ShortTermMemory
import com.roninai.reasoning.ReasoningLayer
import com.roninai.understanding.UnderstandingEngine

class RoninBrain(
    private val understandingEngine: UnderstandingEngine,
    private val reasoningLayer: ReasoningLayer,
    private val shortTermMemory: ShortTermMemory
) {
    fun processUserText(input: String): ChatMessage {
        val userMessage = ChatMessage(role = "user", content = input)
        shortTermMemory.add(userMessage)
        val understanding = understandingEngine.understand(input, shortTermMemory.current)
        val reasoning = reasoningLayer.reason(understanding)
        val response = when (understanding.intent) {
            IntentType.Unknown -> "I need a clearer signal. Say it another way."
            IntentType.Command -> "I understand the action. I’ll wait for your confirmation before doing anything."
            IntentType.Preference -> "That may be worth remembering. Should I save it to long-term memory?"
            IntentType.Correction -> "Understood. I’ll treat this as a correction and learn from it."
            IntentType.Conversation -> "I’m following. ${reasoning.decision}"
        }
        return ChatMessage(role = "assistant", content = response).also(shortTermMemory::add)
    }
}
