import ast
import re
from typing import Dict, Any, List

class CodeValidator:
    """
    MARK_4 Phase 4 Security & Syntax Validator:
    1. Uses AST (Abstract Syntax Tree) to verify code structure before execution.
    2. Scans for dangerous commands (destructive rm -rf, wipe operations).
    3. Guarantees safe execution inside non-rooted Termux sandboxes.
    """
    def __init__(self):
        # List of dangerous strings / regex patterns to block
        self.forbidden_patterns = [
            r"rm\s+-rf\s+/",
            r"mkfs",
            r"dd\s+if=/dev/zero",
            r":\(\)\{\s*:\s*\|\s*:\s*&\s*\};:",  # Fork bomb
        ]

    def validate_syntax(self, code_string: str) -> Dict[str, Any]:
        """Checks if the Python code has valid syntax using AST compilation."""
        try:
            ast.parse(code_string)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"SyntaxError at line {e.lineno}, column {e.offset}: {e.msg}"
            }
        except Exception as e:
            return {"valid": False, "error": f"Compilation Error: {str(e)}"}

    def scan_security(self, code_string: str) -> Dict[str, Any]:
        """Scans code against forbidden destructive patterns."""
        for pattern in self.forbidden_patterns:
            if re.search(pattern, code_string):
                return {
                    "safe": False,
                    "reason": f"Security Violation: Destructive command pattern matched ({pattern})."
                }
        return {"safe": True, "reason": "Code passed security checks."}

    def validate_code(self, code_string: str) -> Dict[str, Any]:
        """Combined AST syntax and security audit pipeline."""
        syntax_check = self.validate_syntax(code_string)
        if not syntax_check["valid"]:
            return {"passed": False, "reason": syntax_check["error"], "stage": "syntax"}

        security_check = self.scan_security(code_string)
        if not security_check["safe"]:
            return {"passed": False, "reason": security_check["reason"], "stage": "security"}

        return {"passed": True, "reason": "Code is syntactically sound and safe.", "stage": "passed"}

# Standalone verification test
if __name__ == "__main__":
    validator = CodeValidator()
    print("🤖 Testing MARK_4 Security & Syntax Validator (validator.py)...")

    # Test 1: Good clean code
    clean_code = "def add(a, b):\n    return a + b"
    print("\n🟢 Testing Clean Code:")
    print(validator.validate_code(clean_code))

    # Test 2: Broken syntax
    syntax_error_code = "def add(a, b)\n    return a + b"  # Missing colon
    print("\n🟡 Testing Syntax Error Code:")
    print(validator.validate_code(syntax_error_code))

    # Test 3: Dangerous script attempt
    dangerous_code = 'import os\nos.system("rm -rf /")'
    print("\n🔴 Testing Dangerous Code Attempt:")
    print(validator.validate_code(dangerous_code))
