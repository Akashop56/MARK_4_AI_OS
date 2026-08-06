import os
import json
import importlib
import inspect
from typing import Dict, Any, List
from Mark_4.tools.app_tool import AppTool

class ToolManager:
    """
    MARK_4 Autonomous Dynamic Tool Manager:
    1. Scans Mark_4/tools/ automatically for any valid *_tool.py modules.
    2. Dynamically loads and registers available tool classes.
    3. Provides refresh_tools() to instantly load newly deployed Phase 5 tools.
    """
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.tools_dir = "/sdcard/pa/Mark_4/tools"
        self.refresh_tools(verbose=False)

    def register_tool(self, tool_instance: Any) -> None:
        if hasattr(tool_instance, "name"):
            self.tools[tool_instance.name] = tool_instance

    def refresh_tools(self, verbose: bool = True) -> Dict[str, Any]:
        """Scans tools/ directory and dynamically reloads all *_tool.py files."""
        self.tools.clear()
        
        # 1. Register base AppTool
        self.register_tool(AppTool())

        # 2. Scan tools directory
        loaded_list = ["app_tool"]
        if os.path.exists(self.tools_dir):
            for filename in sorted(os.listdir(self.tools_dir)):
                if filename.endswith("_tool.py") and filename != "app_tool.py":
                    module_name = filename[:-3]
                    try:
                        mod = importlib.import_module(f"Mark_4.tools.{module_name}")
                        importlib.reload(mod)  # Force reload for newly patched files
                        for _, obj in inspect.getmembers(mod, inspect.isclass):
                            if hasattr(obj, "execute") and hasattr(obj, "__init__"):
                                try:
                                    inst = obj()
                                    if hasattr(inst, "name") and inst.name not in self.tools:
                                        self.register_tool(inst)
                                        loaded_list.append(inst.name)
                                except Exception:
                                    pass
                    except Exception as e:
                        if verbose:
                            print(f"⚠️ [ToolManager Error]: Could not load '{filename}': {e}")

        if verbose:
            print("\n📦 [ToolManager Refreshed] Currently Loaded Tools:")
            for t_name in sorted(list(self.tools.keys())):
                print(f"   • {t_name}")

        return {"success": True, "loaded_tools": list(self.tools.keys())}

    def list_tools(self) -> List[Dict[str, Any]]:
        schema_list = []
        for name, tool in sorted(self.tools.items()):
            schema_list.append({
                "name": name,
                "description": getattr(tool, "description", "Autonomous MARK_4 Tool"),
                "methods": [m for m in dir(tool) if not m.startswith("_") and callable(getattr(tool, m))]
            })
        return schema_list

    def parse_and_execute_llm_action(self, ai_response_text: str) -> Dict[str, Any]:
        try:
            json_str = ai_response_text
            if "```json" in ai_response_text:
                json_str = ai_response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response_text:
                json_str = ai_response_text.split("```")[1].split("```")[0].strip()
            elif "{" in ai_response_text and "}" in ai_response_text:
                json_str = ai_response_text[ai_response_text.find("{"):ai_response_text.rfind("}")+1]

            action_data = json.loads(json_str)
            tool_name = action_data.get("tool")
            action = action_data.get("action")
            args = action_data.get("args", {})

            if not tool_name or tool_name not in self.tools:
                return {"success": False, "error": f"Tool '{tool_name}' not found. Available: {list(self.tools.keys())}"}

            return self.tools[tool_name].execute(action, **args)
        except Exception as e:
            return {"success": False, "error": f"Failed to parse or execute action: {str(e)}"}

# Verification Test
if __name__ == "__main__":
    tm = ToolManager()
    tm.refresh_tools(verbose=True)
