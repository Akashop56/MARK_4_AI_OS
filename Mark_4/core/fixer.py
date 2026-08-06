import re
from typing import Dict, Any, Optional
from Mark_4.brains.omniroute_brain import OmniRouteBrain
from Mark_4.core.runner import CodeRunner
from Mark_4.config import OMNIROUTE_API_KEY

class SelfRepairEngine:
    """
    MARK_4 Phase 4 Self-Repair Engine (fixer.py):
    1. Takes broken code and execution traceback from CodeRunner.
    2. Sends the failure context to the AI Brain for debugging.
    3. Extracts the repaired code block and re-tests in the sandbox.
    """
    def __init__(self, api_key: str = OMNIROUTE_API_KEY):
        self.brain = OmniRouteBrain(api_key=api_key)
        self.runner = CodeRunner()

    def _extract_code_from_llm(self, response: str) -> str:
        """Extracts pure Python code from LLM Markdown fences (```python ... ```)."""
        match = re.search(r"```(?:python)?\s*([\s\S]*?)\s*```", response)
        if match:
            return match.group(1).strip()
        return response.strip()

    def fix_and_verify(self, broken_code: str, error_context: str, max_retries: int = 2) -> Dict[str, Any]:
        """
        Runs an autonomous debugging loop until code succeeds or max_retries is reached.
        """
        current_code = broken_code

        for attempt in range(1, max_retries + 1):
            print(f"\n🛠️ [Fixer attempt {attempt}/{max_retries}]: Asking AI Brain to repair error...")
            
            prompt = (
                "The following Python code failed during execution:\n"
                f"```python\n{current_code}\n```\n\n"
                f"ERROR TRACEBACK / CONTEXT:\n{error_context}\n\n"
                "Please fix the error and return ONLY the corrected, executable Python code inside ```python ``` block."
            )

            llm_reply = self.brain.think(
                prompt=prompt,
                system_prompt="You are MARK_4's autonomous bug-fixing engine. Output ONLY Python code inside markdown blocks."
            )

            fixed_code = self._extract_code_from_llm(llm_reply)

            print("🧪 [Fixer]: Re-testing repaired code in sandbox...")
            test_result = self.runner.run_python_code(fixed_code)

            if test_result.get("success"):
                print("✅ [Fixer]: Code successfully repaired and verified!")
                return {
                    "success": True,
                    "repaired_code": fixed_code,
                    "stdout": test_result.get("stdout"),
                    "attempts": attempt
                }
            else:
                print(f"⚠️ [Fixer]: Repaired code still failed ({test_result.get('error_type')}). Retrying...")
                error_context = test_result.get("stderr", "Unknown error")
                current_code = fixed_code

        return {
            "success": False,
            "error": "Failed to repair code after maximum attempts.",
            "last_error": error_context
        }

# Standalone verification test
if __name__ == "__main__":
    fixer = SelfRepairEngine()
    print("🤖 Testing MARK_4 Autonomous Self-Repair Engine...")

    # Simulated broken code that raises ZeroDivisionError
    buggy_code = """
def calculate_ratio(a, b):
    return a / b

print(f"Result: {calculate_ratio(10, 0)}")
"""
    error_msg = "ZeroDivisionError: division by zero"

    print("\n🔴 Feeding Broken Code to Fixer Engine...")
    repair_result = fixer.fix_and_verify(buggy_code, error_msg)

    print("\nFINAL REPAIR OUTPUT:\n" + "-"*40)
    print(repair_result)
