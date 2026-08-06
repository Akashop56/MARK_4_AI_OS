import subprocess
import os
from typing import Dict, Any, Optional

class TermuxBackend:
    """
    MARK_4 Smart Android Launcher Backend:
    1. Tries termux-am start
    2. Fallbacks to am start
    3. Last resort fallback to monkey launcher
    4. Returns clear, structured error logs if all fail.
    """
    @staticmethod
    def _run_cmd(cmd_list: list) -> Dict[str, Any]:
        try:
            res = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            return {"success": (res.returncode == 0), "stdout": res.stdout.strip(), "stderr": res.stderr.strip()}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e)}

    @classmethod
    def launch_app(cls, package_name: str, activity_name: Optional[str] = None) -> Dict[str, Any]:
        # Method 1: Try termux-am start
        if activity_name:
            cmd1 = ["termux-am", "start", "-n", f"{package_name}/{activity_name}"]
        else:
            cmd1 = ["termux-am", "start", "--user", "0", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", "-p", package_name]
        
        res1 = cls._run_cmd(cmd1)
        if res1["success"]:
            return {"success": True, "method": "termux-am", "package": package_name, "message": "Launched via termux-am"}

        # Method 2: Try standard Android am start
        cmd2 = ["am", "start", "-n", f"{package_name}/{activity_name}"] if activity_name else ["monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
        res2 = cls._run_cmd(cmd2)
        if res2["success"] and "No activities found" not in res2.get("stderr", ""):
            return {"success": True, "method": "am_start", "package": package_name, "message": "Launched via am start"}

        # Method 3: Last Resort Fallback -> monkey
        cmd3 = ["monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
        res3 = cls._run_cmd(cmd3)
        if res3["success"] and "No activities found" not in res3.get("stderr", ""):
            return {"success": True, "method": "monkey_fallback", "package": package_name, "message": "Launched via monkey fallback"}

        return {
            "success": False,
            "error": f"Failed to launch '{package_name}'. All launcher methods (termux-am, am start, monkey) failed.",
            "debug": {"termux_am": res1.get("stderr"), "am_start": res2.get("stderr"), "monkey": res3.get("stderr")}
        }
