"""Termux API wrappers (battery, TTS, speech-to-text, camera)."""
# tools/android_tool.py

import subprocess
import json


class AndroidTool:


    @staticmethod
    def battery():

        try:

            result = subprocess.check_output(
                [
                    "termux-battery-status"
                ],
                text=True
            )


            data = json.loads(result)


            return (
                f"Battery {data['percentage']}% "
                f"and status {data['status']}"
            )


        except Exception as e:

            return f"Battery error: {e}"



    @staticmethod
    def notify(message):

        try:

            subprocess.run(
                [
                    "termux-notification",
                    "--title",
                    "Mark_4",
                    "--content",
                    message
                ]
            )


            return "Notification sent."


        except Exception as e:

            return f"Notification error: {e}"