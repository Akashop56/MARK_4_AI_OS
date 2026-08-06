import subprocess
import json
from typing import Tuple, Dict, Any, Optional, List

class TermuxBackend:
    """
    MARK_4 Phase 1 Hardware Bridge:
    Executes Android Activity Manager (am), Package Manager (pm),
    and Termux API calls safely within non-rooted constraints.
    """
    def __init__(self, default_timeout: int = 10):
        self.default_timeout = default_timeout

    def _exec(self, command: List[str]) -> Tuple[bool, str]:
        """Safely executes shell commands and captures stderr/stdout."""
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.default_timeout
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return False, f"Command failed ({result.returncode}): {error_msg}"
        except subprocess.TimeoutExpired:
            return False, "Error: Execution timed out."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def launch_app(self, package_name: str, activity_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Multi-Stage Android Launch Engine:
        1. If Activity is known -> uses explicit component Intent (-n pkg/act).
        2. Fallback -> uses monkey launcher trigger.
        """
        # Stage 1: Explicit Activity Launch (Fastest & most reliable)
        if activity_name and "/" in activity_name:
            cmd = ["am", "start", "--user", "0", "-n", activity_name]
            success, output = self._exec(cmd)
            if success and "Error" not in output:
                return True, f"Successfully launched [{package_name}] via Activity."

        # Stage 2: Standard Package Launch
        cmd = ["am", "start", "--user", "0", "-a", "android.intent.action.MAIN", 
               "-c", "android.intent.category.LAUNCHER", "-p", package_name]
        success, output = self._exec(cmd)
        if success and "Error" not in output:
            return True, f"Successfully launched [{package_name}] via Intent."

        # Stage 3: Ultimate Fallback (Monkey Event Launcher)
        cmd = ["monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
        success, output = self._exec(cmd)
        if success:
            return True, f"Successfully launched [{package_name}] via Monkey Fallback."

        return False, f"Failed to open {package_name}. Reason: {output}"

    def get_battery_status(self) -> Dict[str, Any]:
        """Fetches live battery stats via Termux API."""
        success, output = self._exec(["termux-battery-status"])
        if success and output:
            try:
                data = json.loads(output)
                return {
                    "success": True,
                    "percentage": data.get("percentage", 0),
                    "status": data.get("status", "UNKNOWN"),
                    "temperature": data.get("temperature", 0.0)
                }
            except json.JSONDecodeError:
                pass
        return {"success": False, "error": "Could not read Termux Battery API. Is Termux:API installed?"}

# Standalone verification test
if __name__ == "__main__":
    backend = TermuxBackend()
    print("🤖 Testing MARK_4 Termux Backend Bridge...")
    
    # 1. Test Battery Status
    bat = backend.get_battery_status()
    if bat.get("success"):
        print(f"🔋 Battery: {bat['percentage']}% | Status: {bat['status']}")
    else:
        print(f"⚠️ Battery Warning: {bat.get('error')}")

    # 2. Test Launching YouTube via package only
    pkg = "com.google.android.youtube"
    print(f"🚀 Attempting to open [{pkg}]...")
    success, result_msg = backend.launch_app(package_name=pkg)
    print(f"Result -> Success: {success} | Message: {result_msg}")
