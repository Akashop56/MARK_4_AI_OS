import os
import shutil
import subprocess
from typing import Dict, Any, List

class FileTool:
    """
    MARK_4 Universal Safe Filesystem Suite (v2.3 - Kernel Mount Detector Bypass):
    1. Bypasses Android '/storage' PermissionError using kernel mount table (/proc/mounts & df).
    2. Correctly routes '/SD card/...' to external SD chip and '/Internal storage/...' to internal memory.
    """
    def __init__(self):
        self.name = "file_tool"
        self.description = "Create, read, edit, delete files and folders safely within internal storage and external SD cards."
        self.default_dir = "/sdcard/pa"
        self.internal_root = "/storage/emulated/0"
        self.external_sd_root = self._detect_external_sd()
        
        self.allowed_roots = [
            "/sdcard",
            self.internal_root,
            "/data/data/com.termux/files/home",
            os.path.expanduser("~")
        ]
        if self.external_sd_root:
            self.allowed_roots.append(self.external_sd_root)

        self.blocked_roots = ["/system", "/data", "/proc", "/sys", "/dev"]

    def _detect_external_sd(self) -> str:
        # Method 1: Check kernel mount table (/proc/mounts) - bypasses PermissionError
        try:
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) > 1:
                        mp = parts[1]
                        if mp.startswith("/storage/") and not any(x in mp for x in ["emulated", "self", "enc", "knox"]):
                            if os.path.exists(mp):
                                return mp
        except Exception:
            pass

        # Method 2: Check via 'df' command output
        try:
            res = subprocess.run(["df"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in res.stdout.splitlines():
                parts = line.split()
                for p in parts:
                    if p.startswith("/storage/") and not any(x in p for x in ["emulated", "self", "enc", "knox"]):
                        if os.path.exists(p):
                            return p
        except Exception:
            pass

        # Method 3: Direct list with PermissionError guard
        try:
            if os.path.exists("/storage"):
                for entry in os.listdir("/storage"):
                    if entry not in ["emulated", "self", "enc_emulated", "knox-emulated"]:
                        full_p = os.path.join("/storage", entry)
                        if os.path.isdir(full_p):
                            return full_p
        except (PermissionError, Exception):
            pass

        return ""

    def _normalize_path(self, raw_path: str) -> str:
        p = raw_path.strip().replace("\\", "/")
        p_lower = p.lower()

        if p_lower.startswith("/sd card/") or p_lower.startswith("sd card/") or p_lower.startswith("/external sd/"):
            prefix_len = len("/sd card/") if p_lower.startswith("/sd card/") else (len("sd card/") if p_lower.startswith("sd card/") else len("/external sd/"))
            sub_path = p[prefix_len:].lstrip("/")
            target_root = self.external_sd_root if self.external_sd_root else self.internal_root
            p = os.path.join(target_root, sub_path)
        elif p_lower.startswith("/internal storage/") or p_lower.startswith("internal storage/"):
            prefix_len = len("/internal storage/") if p_lower.startswith("/internal storage/") else len("internal storage/")
            sub_path = p[prefix_len:].lstrip("/")
            p = os.path.join(self.internal_root, sub_path)
        elif not p.startswith("/"):
            p = os.path.join(self.default_dir, p)

        return os.path.abspath(p)

    def _extract_path(self, kwargs: Dict[str, Any]) -> str:
        for key in ["path", "file_path", "filepath", "file", "target", "target_path", "filename", "dir", "directory"]:
            if key in kwargs and kwargs[key]:
                return str(kwargs[key])
        return ""

    def _is_path_safe(self, target_path: str) -> Dict[str, Any]:
        abs_path = self._normalize_path(target_path)
        
        if abs_path == "/":
            return {"safe": False, "error": "Access denied: Cannot access system root '/' directly."}

        for blocked in self.blocked_roots:
            if abs_path == blocked or abs_path.startswith(blocked + "/"):
                if "/data/data/com.termux/files/home" in abs_path:
                    continue
                return {"safe": False, "error": f"Access denied: Path '{abs_path}' is inside blocked system root '{blocked}'."}

        is_allowed = any(abs_path == root or abs_path.startswith(root + "/") for root in self.allowed_roots)
        if not is_allowed:
            return {"safe": False, "error": f"Access denied: Path '{abs_path}' is outside permitted storage roots: {self.allowed_roots}"}

        return {"safe": True, "abs_path": abs_path}

    def execute(self, action: str = "read", **kwargs) -> Dict[str, Any]:
        action_clean = str(action).lower().strip()
        if action_clean in ["execute", "run", "do"]:
            action_clean = str(kwargs.get("operation") or kwargs.get("action") or "read").lower().strip()

        raw_path = self._extract_path(kwargs)
        if not raw_path:
            return {"success": False, "error": "Parameter 'path' is required."}

        safety_check = self._is_path_safe(raw_path)
        if not safety_check["safe"]:
            return {"success": False, "error": safety_check["error"]}

        clean_path = safety_check["abs_path"]
        content = str(kwargs.get("content") or kwargs.get("text") or kwargs.get("data") or "")

        try:
            if action_clean in ["exists", "exist", "check"]:
                return {"success": True, "exists": os.path.exists(clean_path), "path": clean_path}
            elif action_clean in ["list", "list_files", "list_dir", "ls"]:
                if not os.path.exists(clean_path):
                    return {"success": False, "error": f"Directory not found: '{clean_path}'"}
                return {"success": True, "path": clean_path, "files": sorted(os.listdir(clean_path))}
            elif action_clean in ["mkdir", "create_dir", "make_dir"]:
                os.makedirs(clean_path, exist_ok=True)
                return {"success": True, "action": "mkdir", "path": clean_path, "message": "Folder created successfully."}
            elif action_clean in ["rmdir", "delete_dir", "remove_dir"]:
                if not os.path.exists(clean_path):
                    return {"success": False, "error": f"Folder not found: '{clean_path}'"}
                shutil.rmtree(clean_path)
                return {"success": True, "action": "rmdir", "path": clean_path, "message": "Folder removed successfully."}
            elif action_clean in ["read", "read_file", "open_file_content", "view"]:
                if not os.path.exists(clean_path):
                    return {"success": False, "error": f"File not found: '{clean_path}'"}
                with open(clean_path, "r", encoding="utf-8", errors="ignore") as f:
                    return {"success": True, "action": "read", "path": clean_path, "content": f.read()}
            elif action_clean in ["write", "write_file", "create_file", "create"]:
                os.makedirs(os.path.dirname(clean_path), exist_ok=True)
                with open(clean_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return {"success": True, "action": "write", "path": clean_path, "message": "File written successfully."}
            elif action_clean in ["append", "append_file", "edit", "edit_file", "update"]:
                if not os.path.exists(clean_path):
                    return {"success": False, "error": f"File not found to edit: '{clean_path}'"}
                with open(clean_path, "a", encoding="utf-8") as f:
                    f.write(content)
                return {"success": True, "action": "append", "path": clean_path, "message": "Content appended successfully."}
            elif action_clean in ["delete", "delete_file", "remove", "rm"]:
                if not os.path.exists(clean_path):
                    return {"success": False, "error": f"File not found: '{clean_path}'"}
                os.remove(clean_path)
                return {"success": True, "action": "delete", "path": clean_path, "message": "File deleted successfully."}

            return {"success": False, "error": f"Unknown action '{action_clean}'."}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    ft = FileTool()
    print("Detected External SD Card Root ->", ft.external_sd_root if ft.external_sd_root else "(No external SD card mounted in kernel table)")
