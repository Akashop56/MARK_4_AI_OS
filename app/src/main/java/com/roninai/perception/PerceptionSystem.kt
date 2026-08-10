package com.roninai.perception

import android.content.Context
import android.os.BatteryManager
import com.roninai.domain.model.PerceptionSnapshot

class PerceptionSystem(private val context: Context) {
    fun currentSnapshot(): PerceptionSnapshot {
        val batteryManager = context.getSystemService(BatteryManager::class.java)
        val batteryPercent = batteryManager?.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)?.takeIf { it >= 0 }
        return PerceptionSnapshot(
            notificationsAvailable = false,
            deviceStateAvailable = true,
            environmentAvailable = false,
            batteryPercent = batteryPercent,
            charging = null
        )
    }
}
