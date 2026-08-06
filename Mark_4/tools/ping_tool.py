import subprocess
import time
from typing import Dict, Any

class PingTool:
    """
    MARK_4 Autonomous Ping Tool:
    Checks internet connectivity by pinging google.com.
    Supports standard actions: 'ping', 'execute', 'check', 'run'.
    """
    def __init__(self):
        self.name = "ping_tool"
        self.description = "Checks internet connectivity and latency by pinging google.com."

    def execute(self, action: str = "ping", **kwargs) -> Dict[str, Any]:
        # Treat execute/run/check as default 'ping' action
        action_clean = str(action).lower().strip()
        if action_clean not in ["ping", "execute", "check", "run", "default"]:
            return {
                "success": False,
                "error": f"Unsupported action: '{action}'. Use 'ping' or 'check'."
            }

        target_host = kwargs.get("host", "google.com")
        timeout_sec = kwargs.get("timeout", 3)

        try:
            start_time = time.time()
            # Run 1 packet ping with timeout
            cmd = ["ping", "-c", "1", "-W", str(timeout_sec), target_host]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            elapsed_ms = round((time.time() - start_time) * 1000, 2)

            if res.returncode == 0:
                return {
                    "success": True,
                    "data": {
                        "status": "ONLINE",
                        "host": target_host,
                        "latency_ms": elapsed_ms,
                        "message": f"Successfully pinged {target_host}"
                    }
                }
            else:
                return {
                    "success": False,
                    "data": {
                        "status": "OFFLINE_OR_UNREACHABLE",
                        "host": target_host,
                        "error": res.stderr.strip() or "Ping command failed or timed out."
                    }
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    tool = PingTool()
    print("Test default execute():", tool.execute("execute"))
    print("Test ping action:", tool.execute("ping", host="1.1.1.1"))
