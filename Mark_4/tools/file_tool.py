import os
import shutil
from typing import Dict, Any, List

class FileTool:
    """
    MARK_4 Safe Filesystem Tool:
    Allows operations ONLY inside safe Android roots:
      - /sdcard
      - /storage/emulated/0
      - /data/data/com.termux/files/home
    Blocks system roots (/, /system, /data, etc.)
    """
    def __init__(self):
        self.name = "file_tool"
        self.description = "Read, write, list, and check files safely within permitted Android storage paths."
        self.allowed_roots = [
            "/sdcard",
            "/storage/emulated/0",
            "/data/data/com.termux/files/home",
            os.path.expanduser("~")
        ]
        self.blocked_roots = ["/system", "/data", "/proc", "/sys", "/dev"]

    def _is_path_safe(self, target_path: str) -> Dict[str, Any]:
        abs_path = os.path.abspath(target_path)
        
        # Block root directly
        if abs_path == "/":
            return {"safe": False, "error": "Access denied: Cannot access system root '/' directly."}

        # Block explicit system directories
        for blocked in self.blocked_roots:
            if abs_path == blocked or abs_path.startswith(blocked + "/"):
                # Exception: Allow termux home inside /data/data/...
                if "/data/data/com.termux/files/home" in abs_path:
                    continue
                return {"safe": False, "error": f"Access denied: Path '{abs_path}' is inside blocked system root '{blocked}'."}

        # Check if inside allowed roots
        is_allowed = any(abs_path == root or abs_path.startswith(root + "/") for root in self.allowed_roots)
        if not is_allowed:
            return {"safe": False, "error": f"Access denied: Path '{abs_path}' is outside permitted storage roots."}

        return {"safe": True, "abs_path": abs_path}

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        path = kwargs.get("path", "")
        if not path:
            return {"success": False, "error": "Parameter 'path' is required."}

        safety_check = self._is_path_safe(path)
        if not safety_check["safe"]:
            return {"success": False, "error": safety_check["error"]}

        clean_path = safety_check["abs_path"]

        try:
            if action == "exists":
                return {"success": True, "exists": os.path.exists(clean_path), "path": clean_path}
            
            elif action == "list":
                if not os.path.exists(clean_path):
                    return {"success": False, "error": f"Directory not found: '{clean_path}'"}
                return {"success": True, "path": clean_path, "files": os.listdir(clean_path)}
            
            elif action == "read":
                if not os.path.exists(clean_path):
                    return {"success": False, "error": f"File not found: '{clean_path}'"}
                with open(clean_path, "r", encoding="utf-8", errors="ignore") as f:
                    return {"success": True, "path": clean_path, "content": f.read(4096)}  # 4KB max read
            
            return {"success": False, "error": f"Unknown action '{action}'. Valid actions: exists, list, read."}
        
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    ft = FileTool()
    print("🟢 Safe Path Test (/sdcard/pa):", ft.execute("list", path="/sdcard/pa"))
    print("🔴 Blocked Path Test (/system):", ft.execute("list", path="/system"))
