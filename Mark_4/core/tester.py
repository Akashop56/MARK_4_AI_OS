import json
from typing import Dict, Any, List, Optional
from Mark_4.core.validator import CodeValidator
from Mark_4.core.runner import CodeRunner

class CodeTester:
    """
    MARK_4 Phase 4 Automated Testing Suite (tester.py):
    1. Validates code syntax & safety using CodeValidator.
    2. Executes test scripts inside CodeRunner sandbox.
    3. Verifies assertions and reports structured pass/fail metrics.
    """
    def __init__(self):
        self.validator = CodeValidator()
        self.runner = CodeRunner()

    def run_test_case(self, code_string: str, expected_output_substr: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs an isolated code test case after validating AST safety.
        Checks if expected_output_substr appears in stdout.
        """
        # Stage 1: Safety & Syntax Audit
        audit = self.validator.validate_code(code_string)
        if not audit["passed"]:
            return {
                "passed": False,
                "stage": "validation_failed",
                "error": audit["reason"]
            }

        # Stage 2: Sandbox Execution
        exec_result = self.runner.run_python_code(code_string)
        if not exec_result["success"]:
            return {
                "passed": False,
                "stage": "execution_failed",
                "error_type": exec_result.get("error_type"),
                "error": exec_result["stderr"]
            }

        # Stage 3: Assertion Check
        stdout = exec_result["stdout"]
        if expected_output_substr and expected_output_substr not in stdout:
            return {
                "passed": False,
                "stage": "assertion_failed",
                "expected_substring": expected_output_substr,
                "actual_stdout": stdout,
                "error": f"Output did not contain expected substring: '{expected_output_substr}'"
            }

        return {
            "passed": True,
            "stage": "passed",
            "stdout": stdout
        }

    def run_suite(self, test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Runs multiple test cases and returns summary metrics.
        Input format: [{"name": "Test 1", "code": "...", "expected": "..."}]
        """
        passed_count = 0
        total = len(test_cases)
        results = []

        for tc in test_cases:
            name = tc.get("name", "Unnamed Test")
            code = tc.get("code", "")
            expected = tc.get("expected")

            res = self.run_test_case(code, expected_output_substr=expected)
            res["test_name"] = name
            results.append(res)
            if res["passed"]:
                passed_count += 1

        return {
            "total_tests": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "all_passed": (passed_count == total),
            "details": results
        }

# Standalone verification test
if __name__ == "__main__":
    tester = CodeTester()
    print("🤖 Testing MARK_4 Automated Testing Suite (tester.py)...")

    sample_suite = [
        {
            "name": "Addition Unit Test",
            "code": "print('Result:', 15 + 25)",
            "expected": "Result: 40"
        },
        {
            "name": "Assertion Failure Test",
            "code": "print('Result:', 10 + 10)",
            "expected": "Result: 99"  # Deliberate mismatch
        },
        {
            "name": "Security Block Test",
            "code": "import os\nos.system('rm -rf /')",
            "expected": "anything"
        }
    ]

    summary = tester.run_suite(sample_suite)
    print(f"\n📊 Summary: {summary['passed']}/{summary['total_tests']} Tests Passed.")
    for res in summary["details"]:
        status = "✅ PASS" if res["passed"] else f"❌ FAIL ({res['stage']})"
        print(f"  [{status}] - {res['test_name']}")
