package com.roninai.devicetools

class DeviceToolRegistry {
    fun canExecute(toolName: String, userConfirmed: Boolean): Boolean =
        userConfirmed && toolName !in setOf("delete_files", "send_message_without_confirmation", "silent_settings_change")
}
