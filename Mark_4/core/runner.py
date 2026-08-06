import subprocess
import os
import re
from typing import Dict, Any, Optional, List

class CodeRunner:
    """
    MARK_4 Phase 4 Safe Execution Sandbox:
    Executes Python scripts and shell commands safely.
    Captures stdout, stderr, return codes, and identifies exception types
    to feed into the Self-Repair Engine (fixer.py).
    """
    def __init__(self, default_timeout: int = 15):
        self.default_timeout = default_timeout
        self.temp_exec_path = "/sdcard/pa/Mark_4/memory/temp_exec.py"

    def _extract_error_type(self, stderr: str) -> Optional[str]:
        """Extracts the Python exception type (e.g., ZeroDivisionError) from stderr."""
        if not stderr:
            return None
        # Look for typical Python error lines like 'ZeroDivisionError: division by zero'
        match = re.search(r"([a-zA-Z]+Error|Exception):", stderr)
        if match:
            return match.group(1)
        return "RuntimeError"

    def run_python_file(self, filepath: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Runs an existing Python script safely and returns structured output."""
        if not os.path.exists(filepath):
            return {
                "success": False,
                "filepath": filepath,
                "stdout": "",
                "stderr": f"FileNotFoundError: '{filepath}' does not exist.",
                "returncode": -1,
                "error_type": "FileNotFoundError"
            }

        cmd = ["python", filepath]
        return self._execute_command(cmd, timeout=timeout or self.default_timeout)

    def run_python_code(self, code_string: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Saves raw Python code to a temporary sandbox file and executes it.
        Great for testing AI-generated fixes before applying them to permanent files.
        """
        try:
            os.makedirs(os.path.dirname(self.temp_exec_path), exist_ok=True)
            with open(self.temp_exec_path, "w", encoding="utf-8") as f:
                f.write(code_string)
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"IOError: Failed to write temp file: {e}",
                "returncode": -1,
                "error_type": "IOError"
            }

        result = self.run_python_file(self.temp_exec_path, timeout=timeout)
        result["is_temp"] = True
        return result

    def run_shell(self, command: List[str], timeout: Optional[int] = None) -> Dict[str, Any]:
        """Executes a Termux shell command safely."""
        return self._execute_command(command, timeout=timeout or self.default_timeout)

    def _execute_command(self, cmd: List[str], timeout: int) -> Dict[str, Any]:
        """Internal execution engine with timeout and output capture."""
        try:
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            
            stdout_clean = process.stdout.strip()
            stderr_clean = process.stderr.strip()
            success = (process.returncode == 0)
            
            return {
                "success": success,
                "stdout": stdout_clean,
                "stderr": stderr_clean,
                "returncode": process.returncode,
                "error_type": self._extract_error_type(stderr_clean) if not success else None
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"TimeoutError: Execution exceeded {timeout} seconds.",
                "returncode": -2,
                "error_type": "TimeoutError"
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "error_type": "SystemError"
            }

# Standalone verification test
if __name__ == "__main__":
    runner = CodeRunner()
    print("🤖 Testing MARK_4 Safe Execution Sandbox (runner.py)...")

    # 1. Test running working Python code
    good_code = """
x = 10
y = 20
print(f"Sum is: {x + y}")
"""
    print("\n🟢 Testing Working Code Execution:")
    res_good = runner.run_python_code(good_code)
    print(res_good)

    # 2. Test running broken Python code (for self-repair testing)
    bad_code = """
def divide(a, b):
    return a / b

print("Calculating...")
print(divide(5, 0))
"""
    print("\n🔴 Testing Broken Code Execution (Error Capture):")
    res_bad = runner.run_python_code(bad_code)
    print(res_bad)
