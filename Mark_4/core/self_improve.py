import os
import re
import shutil
import json
from typing import Dict, Any, Optional
from Mark_4.config import OMNIROUTE_API_KEY
from Mark_4.brains.omniroute_brain import OmniRouteBrain
from Mark_4.core.validator import CodeValidator
from Mark_4.core.runner import CodeRunner
from Mark_4.core.fixer import SelfRepairEngine

class SelfImprovementEngine:
    """
    MARK_4 Phase 5 Autonomous Self-Improvement Engine:
    1. Generates Tool Class code.
    2. Runs AST & Sandbox Security Audits.
    3. AUTONOMOUS REPAIR: If sandbox verification fails, hands over to SelfRepairEngine.
    4. Safely deploys verified tool with automatic rollback protection.
    """
    def __init__(self, api_key: str = OMNIROUTE_API_KEY):
        print("🧠 [SelfImprovementEngine]: Initializing MARK_4 Capability Builder...")
        self.brain = OmniRouteBrain(api_key=api_key)
        self.validator = CodeValidator()
        self.runner = CodeRunner()
        self.fixer = SelfRepairEngine(api_key=api_key)
        self.tools_dir = "/sdcard/pa/Mark_4/tools"

    def _extract_code(self, text: str) -> Optional[str]:
        match = re.search(r"```(?:python)?\s*([\s\S]*?)\s*```", text)
        if match:
            return match.group(1).strip()
        return text.strip() if "class " in text else None

    def _get_tool_template_instructions(self, tool_name: str, capability_desc: str) -> str:
        return (
            "You are MARK_4's autonomous tool developer.\n"
            f"Create a production-ready Python tool named '{tool_name}' for: {capability_desc}\n\n"
            "MANDATORY ARCHITECTURAL RULES:\n"
            "1. Define a class named exactly with CamelCase (e.g., PingTool).\n"
            "2. In __init__, set self.name = '<lowercase_tool_name>' and self.description = '<what tool does>'.\n"
            "3. MUST include method: def execute(self, action: str, **kwargs) -> dict:\n"
            "4. Returns structured dictionary: {'success': bool, 'data': ...}\n"
            "5. In '__main__' block, instantiate the EXACT SAME class name and test execute().\n"
            "6. Output ONLY executable Python code inside ```python ``` fences."
        )

    def create_and_deploy_tool(self, tool_filename: str, capability_request: str) -> Dict[str, Any]:
        clean_filename = tool_filename if tool_filename.endswith(".py") else f"{tool_filename}.py"
        target_path = os.path.join(self.tools_dir, clean_filename)
        backup_path = f"{target_path}.bak"

        print(f"\n🚀 [Phase 5 - Step 1]: Designing Tool '{clean_filename}'...")
        system_instruction = self._get_tool_template_instructions(clean_filename.replace(".py", ""), capability_request)
        
        llm_reply = self.brain.think(prompt=capability_request, system_prompt=system_instruction)
        code_string = self._extract_code(llm_reply)

        if not code_string:
            return {"success": False, "stage": "code_generation", "error": "AI failed to return code."}

        # Stage 2: Security Audit
        print("🛡️ [Phase 5 - Step 2]: Running Security & AST Syntax Audit...")
        audit = self.validator.validate_code(code_string)
        if not audit["passed"]:
            return {"success": False, "stage": "security_validation_blocked", "error": audit["reason"]}

        # Stage 3: Sandbox Test with AUTONOMOUS FIXER HANDOVER
        print("🧪 [Phase 5 - Step 3]: Running Sandbox Test execution...")
        sandbox_res = self.runner.run_python_code(code_string)
        if not sandbox_res.get("success"):
            print(f"⚠️ [Phase 5 Sandbox Error]: {sandbox_res.get('error_type')}. Triggering Autonomous Fixer...")
            repair_res = self.fixer.fix_and_verify(
                broken_code=code_string,
                error_context=sandbox_res.get("stderr", "Unknown error"),
                max_retries=2
            )
            if repair_res.get("success"):
                print("🛠️ [Phase 5 Fixer]: Code successfully repaired!")
                code_string = repair_res.get("repaired_code")
            else:
                return {
                    "success": False,
                    "stage": "sandbox_verification_failed",
                    "error_type": sandbox_res.get("error_type"),
                    "error": sandbox_res.get("stderr")
                }

        # Stage 4: Backup
        had_old_file = False
        if os.path.exists(target_path):
            shutil.copyfile(target_path, backup_path)
            had_old_file = True

        # Stage 5: Deploy
        print(f"💾 [Phase 5 - Step 5]: Deploying verified tool to -> '{target_path}'")
        try:
            os.makedirs(self.tools_dir, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(code_string)
        except Exception as e:
            return {"success": False, "stage": "deployment_io_error", "error": str(e)}

        # Stage 6: Sanity Test & Rollback
        post_test = self.runner.run_python_file(target_path)
        if not post_test.get("success"):
            print("⚠️ [ROLLBACK]: Post-deployment sanity test failed! Reverting...")
            if had_old_file:
                shutil.copyfile(backup_path, target_path)
                os.remove(backup_path)
            elif os.path.exists(target_path):
                os.remove(target_path)
            return {"success": False, "stage": "rollback_executed", "error": post_test.get("stderr")}

        if os.path.exists(backup_path):
            os.remove(backup_path)

        print(f"✅ [Phase 5 - Complete]: Tool '{clean_filename}' autonomously created, verified & deployed!")
        return {
            "success": True,
            "stage": "deployed_and_verified",
            "tool_filename": clean_filename,
            "filepath": target_path,
            "stdout": post_test.get("stdout")
        }
