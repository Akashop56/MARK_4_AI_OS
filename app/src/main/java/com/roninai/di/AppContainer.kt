package com.roninai.di

import android.content.Context
import com.roninai.core.brain.RoninBrain
import com.roninai.core.context.ContextManager
import com.roninai.core.response.ResponseAnalyzer
import com.roninai.data.db.RoninDatabase
import com.roninai.data.security.ApiKeyVault
import com.roninai.data.settings.ProviderSettingsStore
import com.roninai.experience.ExperienceSystem
import com.roninai.learning.LearningSystem
import com.roninai.memory.LongTermMemory
import com.roninai.memory.ShortTermMemory
import com.roninai.providers.AiProviderRouter
import com.roninai.providers.AiProviderSystem
import com.roninai.reasoning.ReasoningLayer
import com.roninai.understanding.UnderstandingEngine
import com.roninai.voice.VoiceSystem

class AppContainer(context: Context) {
    private val database = RoninDatabase.create(context)
    val shortTermMemory = ShortTermMemory()
    val longTermMemory = LongTermMemory(database.longTermMemoryDao())
    val experienceSystem = ExperienceSystem(database.experienceDao())
    val learningSystem = LearningSystem()
    val understandingEngine = UnderstandingEngine()
    val contextManager = ContextManager()
    val responseAnalyzer = ResponseAnalyzer()
    val reasoningLayer = ReasoningLayer()
    val voiceSystem = VoiceSystem()
    val providerSettingsStore = ProviderSettingsStore(context)
    val apiKeyVault = ApiKeyVault(context)
    val aiProviderSystem = AiProviderSystem(apiKeyVault, providerSettingsStore)
    val aiProviderRouter = AiProviderRouter(apiKeyVault, providerSettingsStore)
    val brain = RoninBrain(
        understandingEngine,
        contextManager,
        aiProviderRouter,
        responseAnalyzer,
        reasoningLayer,
        shortTermMemory,
        experienceSystem
    )
}
