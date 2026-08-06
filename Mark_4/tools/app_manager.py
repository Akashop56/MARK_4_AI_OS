import os
import json
import subprocess
from typing import Dict, Optional, List, Tuple

class AppManager:
    """
    MARK_4 Phase 1 App Manager:
    Handles dynamic package discovery, multi-stage activity resolution,
    and persistent JSON memory caching for Android applications.
    """
    def __init__(self, memory_path: str = "/sdcard/pa/Mark_4/memory/apps.json"):
        self.memory_path = memory_path
        self.cache: Dict[str, Dict[str, str]] = {}
        self._ensure_memory_file()
        self._load_cache()

    def _ensure_memory_file(self) -> None:
        """Creates memory/apps.json if it does not exist."""
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        if not os.path.exists(self.memory_path):
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4)

    def _load_cache(self) -> None:
        """Loads cached package/activity mappings from disk."""
        try:
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure data is a valid dictionary structure
                if isinstance(data, dict):
                    self.cache = data
                else:
                    self.cache = {}
        except (json.JSONDecodeError, IOError):
            self.cache = {}

    def _save_cache(self) -> None:
        """Persists updated package mappings to disk."""
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=4)
        except IOError as e:
            print(f"[AppManager Error]: Failed to save cache: {e}")

    def _run_shell(self, command: List[str]) -> str:
        """Executes a Termux-safe shell command and returns output."""
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception as e:
            print(f"[AppManager Error]: Shell execution failed: {e}")
            return ""

    def list_installed_apps(self, include_system: bool = False) -> List[str]:
        """Returns a list of installed package names."""
        cmd = ["cmd", "package", "list", "packages"]
        if not include_system:
            cmd.append("-3")
        
        output = self._run_shell(cmd)
        packages = []
        for line in output.splitlines():
            if line.startswith("package:"):
                packages.append(line.split("package:")[1].strip())
        return packages

    def is_installed(self, package_name: str) -> bool:
        """Verifies if an exact package name exists on the device."""
        cmd = ["cmd", "package", "list", "packages", package_name]
        output = self._run_shell(cmd)
        return any(
            line.strip() == f"package:{package_name}"
            for line in output.splitlines()
        )

    def resolve_launcher_activity(self, package_name: str) -> Optional[str]:
        """Resolves the exact MAIN/LAUNCHER activity for cold-starting apps."""
        cmd = [
            "cmd", "package", "resolve-activity",
            "--brief",
            "-c", "android.intent.category.LAUNCHER",
            package_name
        ]
        output = self._run_shell(cmd)
        
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        for line in lines:
            if "/" in line and not line.startswith("Priority"):
                return line
        return None

    def search_app(self, app_alias: str) -> Optional[Tuple[str, Optional[str]]]:
        """
        Multi-Stage Resolution Engine:
        1. Checks persistent cache (apps.json).
        2. Dynamic fuzzy search against installed packages.
        3. Resolves exact Launcher Activity.
        4. Caches and returns (package_name, activity_name).
        """
        alias_clean = app_alias.lower().strip()

        # Stage 1: Check cache safely
        if alias_clean in self.cache:
            entry = self.cache[alias_clean]
            # Self-healing: Ensure cached entry is a dictionary
            if isinstance(entry, dict):
                pkg = entry.get("package")
                act = entry.get("activity")
                if pkg and self.is_installed(pkg):
                    return pkg, act

        # Stage 2: Dynamic discovery
        all_packages = self.list_installed_apps(include_system=True)
        matched_pkg = None
        
        for pkg in all_packages:
            if alias_clean in pkg.lower():
                matched_pkg = pkg
                break

        if not matched_pkg:
            return None

        # Stage 3: Resolve launcher activity
        activity = self.resolve_launcher_activity(matched_pkg)

        # Stage 4: Persist to memory/apps.json
        self.cache[alias_clean] = {
            "package": matched_pkg,
            "activity": activity or ""
        }
        self._save_cache()

        return matched_pkg, activity

if __name__ == "__main__":
    manager = AppManager()
    print("🤖 Testing AppManager search_app method...")
    res = manager.search_app("youtube")
    print(f"Result for youtube: {res}")
