import os
import subprocess
from typing import Dict, Any

class FileOpenerTool:
    """
    MARK_4 True External SD Card File Opener Tool (v2.3 - Permission-Safe):
    Correctly resolves real External SD Card Chip paths via kernel mounts
    and opens PDF, images, docs, and media using native Android viewers.
    """
    def __init__(self):
        self.name = "file_opener_tool"
        self.description = "Open files (PDF, images, documents, media) with Android's default viewer applications."
        self.default_dir = "/sdcard/pa"
        self.internal_root = "/storage/emulated/0"
        self.external_sd_root = self._detect_external_sd()

    def _detect_external_sd(self) -> str:
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

    def execute(self, action: str = "open", **kwargs) -> Dict[str, Any]:
        raw_path = ""
        for key in ["path", "file_path", "filepath", "file", "target", "filename"]:
            if key in kwargs and kwargs[key]:
                raw_path = str(kwargs[key])
                break

        if not raw_path:
            return {"success": False, "error": "Parameter 'path' is required to open a file."}

        abs_path = self._normalize_path(raw_path)

        if not os.path.exists(abs_path):
            return {"success": False, "error": f"File not found for opening: '{abs_path}'. Checked physical path: '{abs_path}'"}

        try:
            res1 = subprocess.run(["termux-open", abs_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res1.returncode == 0:
                return {
                    "success": True,
                    "action": "open_file",
                    "path": abs_path,
                    "message": f"Successfully opened '{os.path.basename(abs_path)}' via termux-open."
                }

            uri = f"file://{abs_path}"
            cmd = ["am", "start", "-a", "android.intent.action.VIEW", "-d", uri]
            res2 = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res2.returncode == 0:
                return {
                    "success": True,
                    "action": "open_file",
                    "path": abs_path,
                    "message": f"Successfully launched Android viewer for '{os.path.basename(abs_path)}'."
                }

            return {"success": False, "error": f"Failed to launch viewer: {res1.stderr.strip() or res2.stderr.strip()}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    fot = FileOpenerTool()
    print("FileOpenerTool External SD Card Root ->", fot.external_sd_root if fot.external_sd_root else "(No external SD card mounted in kernel table)")
