import json
import re
from typing import Dict, Any, Optional
from Mark_4.config import OMNIROUTE_API_KEY
from Mark_4.brains.omniroute_brain import OmniRouteBrain
from Mark_4.core.tool_manager import ToolManager
from Mark_4.ai_manager import AIManager
from Mark_4.core.self_improve import SelfImprovementEngine

class CoreRouter:
    """
    MARK_4 Dynamic Master Cognitive Router (router.py):
    1. Always refreshes tools after a new deployment.
    2. Exposes ALL dynamically loaded tools to the LLM system prompt.
    3. Seamlessly routes intents to app_tool, ping_tool, file_tool, sysinfo_tool, etc.
    """
    def __init__(self, api_key: str = OMNIROUTE_API_KEY):
        print("🧠 [CoreRouter]: Initializing Master Unified Routing Engine...")
        self.brain = OmniRouteBrain(api_key=api_key)
        self.tool_manager = ToolManager()
        self.ai_manager = AIManager(api_key=api_key)
        self.self_improve = SelfImprovementEngine(api_key=api_key)

    def _build_system_prompt(self) -> str:
        # Refresh to ensure any newly deployed tool is in memory
        self.tool_manager.refresh_tools(verbose=False)
        tools_list = self.tool_manager.list_tools()
        
        return (
            "You are MARK_4, an advanced autonomous Android AI operating layer in Termux.\n"
            "You have access to the following dynamically loaded tools:\n"
            f"{json.dumps(tools_list, indent=2)}\n\n"
            "MANDATORY ROUTING RULES:\n"
            "1. If user asks to perform an action supported by ANY loaded tool above (e.g. app_tool, ping_tool, file_tool, sysinfo_tool, battery_tool) -> respond ONLY with JSON:\n"
            "```json\n"
            "{\n"
            '  "tool": "<tool_name>",\n'
            '  "action": "<method_or_action_name>",\n'
            '  "args": { ... }\n'
            "}\n"
            "```\n"
            "2. If user explicitly asks to CREATE or DEPLOY a NEW permanent TOOL -> respond ONLY with JSON:\n"
            "```json\n"
            "{\n"
            '  "route": "self_improve",\n'
            '  "tool_name": "<name_tool.py>",\n'
            '  "requirement": "<what the tool should do>"\n'
            "}\n"
            "```\n"
            "3. Do NOT output markdown JSON for casual conversation. Reply directly in short Hinglish."
        )

    def process_user_prompt(self, user_prompt: str) -> str:
        print(f"\n🧠 [CoreRouter]: Analyzing Intent -> '{user_prompt}'")

        # Intent Check 1: Direct code execution / repair request
        code_exec_keywords = ["run this code", "fix this code", "execute script", "code repair"]
        if any(kw in user_prompt.lower() for kw in code_exec_keywords) or "```python" in user_prompt:
            print("⚡ [CoreRouter Route]: -> Phase 4 (Self-Repair Code Runner)")
            return self.ai_manager.process_request(user_prompt)

        # Build fresh prompt with currently loaded tools
        system_prompt = self._build_system_prompt()
        ai_response = self.brain.think(prompt=user_prompt, system_prompt=system_prompt)
        print(f"🤖 [Brain Output Preview]: {ai_response[:120]}..." if len(ai_response) > 120 else f"🤖 [Brain Output]: {ai_response}")

        # Check for JSON blocks
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", ai_response, re.DOTALL)
        if json_match or ("{" in ai_response and "}" in ai_response and '"' in ai_response):
            try:
                raw_json = json_match.group(1) if json_match else ai_response[ai_response.find("{"):ai_response.rfind("}")+1]
                data = json.loads(raw_json)

                # Route A: Phase 5 Self-Improvement
                if data.get("route") == "self_improve" or data.get("tool_name"):
                    print("⚡ [CoreRouter Route]: -> Phase 5 (Autonomous Tool Deployment)")
                    tool_filename = data.get("tool_name", "custom_tool.py")
                    requirement = data.get("requirement", user_prompt)
                    deploy_res = self.self_improve.create_and_deploy_tool(tool_filename, requirement)
                    # Automatically refresh tools in memory after deployment
                    self.tool_manager.refresh_tools(verbose=True)
                    return f"🚀 [Phase 5 Tool Deployed]:\n{json.dumps(deploy_res, indent=2)}"

                # Route B: Any Dynamically Loaded Tool
                elif data.get("tool") and data.get("action"):
                    print(f"⚡ [CoreRouter Route]: -> Dynamic Tool ({data.get('tool')})")
                    exec_res = self.tool_manager.parse_and_execute_llm_action(ai_response)
                    return f"🛠️ [Tool Executed]:\n{json.dumps(exec_res, indent=2)}"

            except json.JSONDecodeError:
                pass

        # Default Route: Conversational Chat
        print("⚡ [CoreRouter Route]: -> Natural Conversation")
        return f"💬 [MARK_4]: {ai_response}"

if __name__ == "__main__":
    router = CoreRouter()
    print("🤖 Testing Dynamic Router with ping prompt...")
    print(router.process_user_prompt("Bhai internet chal raha hai kya ping karke check karo"))
