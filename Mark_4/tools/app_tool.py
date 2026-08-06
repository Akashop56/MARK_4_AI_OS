from typing import Dict, Any, Optional
from Mark_4.tools.app_manager import AppManager
from Mark_4.tools.android_bridge.termux_backend import TermuxBackend

class AppTool:
    """
    MARK_4 Phase 1 Unified App Tool:
    Bridges AI Brain intentions with AppManager discovery & TermuxBackend execution.
    """
    def __init__(self, app_manager: Optional[AppManager] = None, backend: Optional[TermuxBackend] = None):
        self.app_manager = app_manager or AppManager()
        self.backend = backend or TermuxBackend()
        self.name = "app_tool"
        self.description = "Controls Android apps: open apps, check installed status, and list applications."

    def execute(self, action: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Main routing method called by MARK_4 Core Router / Tool Manager.
        Supported actions: 'open_app', 'is_installed', 'list_apps', 'battery_status'
        """
        action_clean = action.lower().strip()

        if action_clean == "open_app":
            app_name = kwargs.get("app_name") or kwargs.get("name")
            if not app_name:
                return {"success": False, "error": "Missing parameter: 'app_name'"}
            return self.open_app(app_name)

        elif action_clean == "is_installed":
            app_name = kwargs.get("app_name") or kwargs.get("name")
            if not app_name:
                return {"success": False, "error": "Missing parameter: 'app_name'"}
            return self.check_installed(app_name)

        elif action_clean == "list_apps":
            include_system = kwargs.get("include_system", False)
            apps = self.app_manager.list_installed_apps(include_system=include_system)
            return {"success": True, "count": len(apps), "apps": apps[:30]}  # Top 30 to save context

        elif action_clean == "battery_status":
            return self.backend.get_battery_status()

        else:
            return {"success": False, "error": f"Unknown action '{action}'. Use: open_app, is_installed, list_apps"}

    def open_app(self, app_alias: str) -> Dict[str, Any]:
        """Resolves app alias to package/activity and launches it via TermuxBackend."""
        result = self.app_manager.search_app(app_alias)
        if not result:
            return {
                "success": False,
                "error": f"App '{app_alias}' not found on this Android device."
            }
        
        package_name, activity_name = result
        success, message = self.backend.launch_app(package_name, activity_name)
        return {
            "success": success,
            "app": app_alias,
            "package": package_name,
            "activity": activity_name,
            "message": message
        }

    def check_installed(self, app_alias: str) -> Dict[str, Any]:
        """Checks if an application is installed without opening it."""
        result = self.app_manager.search_app(app_alias)
        if result:
            package_name, _ = result
            return {
                "success": True,
                "installed": True,
                "app": app_alias,
                "package": package_name
            }
        return {
            "success": True,
            "installed": False,
            "app": app_alias,
            "package": None
        }

# Standalone verification test
if __name__ == "__main__":
    tool = AppTool()
    print("🤖 Testing MARK_4 Phase 1 Unified AppTool...")
    
    # 1. Test is_installed query
    print("\n🔍 Checking if Telegram is installed:")
    check_res = tool.execute("is_installed", app_name="telegram")
    print(check_res)

    # 2. Test opening YouTube
    print("\n🚀 Testing open_app action for YouTube:")
    open_res = tool.execute("open_app", app_name="youtube")
    print(open_res)
