from tools.android_tool import AndroidTool
from tools.app_tool import AppTool


TOOLS = {

    "battery": {
        "name": "battery",
        "description": "Get phone battery information",
        "function": AndroidTool.battery
    },


    "notification": {
        "name": "notification",
        "description": "Send Android notification",
        "function": AndroidTool.notify
    },


    "open_app": {
        "name": "open_app",
        "description": "Open Android application",
        "function": AppTool.open
    },


    "close_app": {
        "name": "close_app",
        "description": "Close Android application",
        "function": AppTool.close
    }

}
