import re
import json
from typing import Dict, Any, Optional
from Mark_4.config import OMNIROUTE_API_KEY
from Mark_4.brains.omniroute_brain import OmniRouteBrain
from Mark_4.core.tool_manager import ToolManager
from Mark_4.core.validator import CodeValidator
from Mark_4.core.runner import CodeRunner
from Mark_4.core.fixer import SelfRepairEngine

class AIManager:
    """
    MARK_4 Phase 4 Master Orchestrator (ai_manager.py):
    Unifies Cognitive Reasoning, Phase 1 Tool Management, and Phase 4 Self-Repair.
    1. Validates generated/requested Python code via AST & Security checks.
    2. Executes code inside an isolated sandbox.
    3. Autonomously routes failures to SelfRepairEngine for real-time patching.
    """
    def __init__(self, api_key: str = OMNIROUTE_API_KEY):
        print("🧠 [AIManager]: Initializing MARK_4 Master Orchestrator...")
        self.brain = OmniRouteBrain(api_key=api_key)
        self.tool_manager = ToolManager()
        self.validator = CodeValidator()
        self.runner = CodeRunner()
        self.fixer = SelfRepairEngine(api_key=api_key)

    def _extract_code_block(self, text: str) -> Optional[str]:
        """Extracts code inside ```python ... ``` Markdown fences."""
        match = re.search(r"```(?:python)?\s*([\s\S]*?)\s*```", text)
        return match.group(1).strip() if match else None

    def execute_and_self_repair(self, code_string: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        The Phase 4 Core Execution Pipeline:
        Validate -> Sandbox Execute -> Autonomous Fix (if failed) -> Return Verified Result.
        """
        print("\n🛡️ [AIManager - Stage 1]: Running AST Syntax & Security Validation...")
        audit = self.validator.validate_code(code_string)
        if not audit["passed"]:
            print(f"❌ [Security/Syntax Blocked]: {audit['reason']}")
            return {
                "success": False,
                "stage": "validation_blocked",
                "error": audit["reason"]
            }

        print("🧪 [AIManager - Stage 2]: Executing code in isolated sandbox...")
        exec_res = self.runner.run_python_code(code_string)

        if exec_res.get("success"):
            print("✅ [AIManager]: Execution successful on first attempt!")
            return {
                "success": True,
                "stage": "executed",
                "code": code_string,
                "stdout": exec_res.get("stdout"),
                "repaired": False
            }

        # Stage 3: Autonomous Self-Repair Trigger
        print(f"⚠️ [AIManager - Stage 3]: Execution failed ({exec_res.get('error_type')}). Handing over to Self-Repair Engine...")
        repair_res = self.fixer.fix_and_verify(
            broken_code=code_string,
            error_context=exec_res.get("stderr", "Unknown execution error"),
            max_retries=max_retries
        )

        if repair_res.get("success"):
            return {
                "success": True,
                "stage": "repaired_and_verified",
                "code": repair_res.get("repaired_code"),
                "stdout": repair_res.get("stdout"),
                "repaired": True,
                "attempts": repair_res.get("attempts")
            }
        else:
            return {
                "success": False,
                "stage": "repair_failed",
                "error": repair_res.get("last_error")
            }

    def process_request(self, user_prompt: str) -> str:
        """
        Processes general user requests.
        If user explicitly asks to run/test/debug code, it orchestrates Phase 4 pipeline.
        """
        print(f"\n💬 [AIManager]: Processing request -> '{user_prompt}'")
        
        # Check if user wants autonomous code generation & testing
        code_keywords = ["script", "code", "run", "test", "debug", "function", "likho", "banao"]
        if any(kw in user_prompt.lower() for kw in code_keywords):
            print("⚡ [AIManager]: Coding/Testing intent detected! Asking AI to generate initial code...")
            system_instruction = (
                "You are MARK_4's autonomous code generation engine. "
                "Output clean Python code inside ```python ``` block based on the user request."
            )
            llm_reply = self.brain.think(prompt=user_prompt, system_prompt=system_instruction)
            
            code = self._extract_code_block(llm_reply)
            if not code:
                return f"🤖 [MARK_4]: Mujhe code block nahi mila:\n{llm_reply}"

            result = self.execute_and_self_repair(code)
            return (
                "🤖 [MARK_4 Phase 4 Output]:\n"
                f"• Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}\n"
                f"• Stage: {result['stage']}\n"
                f"• Repaired by AI: {result.get('repaired', False)}\n"
                "• Sandbox Output:\n"
                f"  {result.get('stdout') or result.get('error')}"
            )

        # Normal conversation or tool routing fallback
        ai_reply = self.brain.think(prompt=user_prompt)
        return f"🤖 [MARK_4]: {ai_reply}"

# Standalone end-to-end verification test
if __name__ == "__main__":
    manager = AIManager()
    print("🤖 Testing MARK_4 Master Orchestrator (ai_manager.py)...")

    # 1. Test running buggy code directly through pipeline
    buggy_test_code = """
def average(numbers):
    total = sum(numbers)
    return total / len(numbers)

# Buggy call with empty list -> causes ZeroDivisionError
print("Average:", average([]))
"""
    print("\n" + "="*50)
    print("🔴 TEST CASE: Feeding buggy code to AIManager pipeline...")
    print("="*50)
    final_result = manager.execute_and_self_repair(buggy_test_code)
    
    print("\n📊 [FINAL AIManager PIPELINE SUMMARY]:")
    print(json.dumps(final_result, indent=2))
