package com.roninai

import android.app.Application
import com.roninai.di.AppContainer

class RoninApplication : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}
