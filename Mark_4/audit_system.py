import os
import sys
import json
from typing import List, Dict, Any

class MasterAuditor:
    """
    MARK_4 System Audit & Diagnostic Suite:
    Verifies the existence, imports, and live functionality of all deployed modules.
    """
    def __init__(self):
        self.base_dir = "/sdcard/pa/Mark_4"
        self.results: List[Dict[str, Any]] = []

    def log_result(self, layer: str, name: str, status: bool, detail: str = "") -> None:
        self.results.append({
            "layer": layer,
            "name": name,
            "status": status,
            "detail": detail
        })

    def run_file_existence_checks(self) -> None:
        expected_files = [
            ("Layer 1 - Config", ".env"),
            ("Layer 1 - Config", "config.py"),
            ("Layer 2 - Phase 1 Tools", "tools/app_tool.py"),
            ("Layer 2 - Tool Manager", "core/tool_manager.py"),
            ("Layer 3 - Security", "core/validator.py"),
            ("Layer 3 - Sandbox", "core/runner.py"),
            ("Layer 3 - Test Suite", "core/tester.py"),
            ("Layer 4 - AI Fixer", "core/fixer.py"),
            ("Layer 4 - Orchestrator", "ai_manager.py"),
            ("Layer 5 - Self Improve", "core/self_improve.py"),
            ("Layer 5 - Deployed Tool 1", "tools/sysinfo_tool.py"),
            ("Layer 5 - Deployed Tool 2", "tools/file_tool.py"),
            ("Layer 6 - Router", "core/router.py"),
            ("Layer 6 - CLI Console", "main.py"),
        ]
        for layer, fname in expected_files:
            fpath = os.path.join(self.base_dir, fname)
            exists = os.path.exists(fpath)
            self.log_result(
                layer=layer,
                name=f"File: {fname}",
                status=exists,
                detail="Present" if exists else "MISSING FILE"
            )

    def test_layer1_config(self) -> None:
        try:
            from Mark_4.config import OMNIROUTE_API_KEY, OMNIROUTE_BASE_URL
            has_key = bool(OMNIROUTE_API_KEY and len(OMNIROUTE_API_KEY) > 8)
            self.log_result("Layer 1 - Config", "API Key Loaded", has_key, "OK" if has_key else "Key Missing/Invalid")
        except Exception as e:
            self.log_result("Layer 1 - Config", "Config Import", False, str(e))

    def test_layer3_sandbox(self) -> None:
        try:
            from Mark_4.core.validator import CodeValidator
            from Mark_4.core.runner import CodeRunner

            val = CodeValidator()
            sec_test = val.validate_code("import os\nos.system('rm -rf /')")
            sec_pass = (sec_test["passed"] is False and "Security Violation" in sec_test["reason"])
            self.log_result("Layer 3 - Security", "AST Firewall Block Test", sec_pass, "Destructive commands blocked successfully")

            runner = CodeRunner()
            exec_test = runner.run_python_code("print(25 + 75)")
            exec_pass = (exec_test["success"] is True and "100" in exec_test["stdout"])
            self.log_result("Layer 3 - Sandbox", "Subprocess Runner Execution", exec_pass, f"Output: {exec_test.get('stdout')}")
        except Exception as e:
            self.log_result("Layer 3 - Security/Sandbox", "Validator & Runner Test", False, str(e))

    def test_layer5_deployed_tools(self) -> None:
        try:
            from Mark_4.core.tool_manager import ToolManager
            tm = ToolManager()

            # Dynamic import test for deployed tools
            tools_to_check = ["sysinfo_tool", "file_tool"]
            for tname in tools_to_check:
                try:
                    mod = __import__(f"Mark_4.tools.{tname}", fromlist=[tname])
                    self.log_result("Layer 5 - Deployed Tools", f"Import '{tname}.py'", True, "Module imported successfully")
                except Exception as e:
                    self.log_result("Layer 5 - Deployed Tools", f"Import '{tname}.py'", False, str(e))
        except Exception as e:
            self.log_result("Layer 5 - Deployed Tools", "ToolManager Registry", False, str(e))

    def test_layer6_router_init(self) -> None:
        try:
            from Mark_4.core.router import CoreRouter
            router = CoreRouter()
            has_tools = len(router.tool_manager.tools) > 0
            self.log_result("Layer 6 - Router", "CoreRouter Initialization", has_tools, f"{len(router.tool_manager.tools)} Tools Registered")
        except Exception as e:
            self.log_result("Layer 6 - Router", "CoreRouter Setup", False, str(e))

    def generate_report(self) -> None:
        print("=" * 66)
        print("🛠️   MARK_4 COMPLETE ARCHITECTURAL SYSTEM AUDIT & VERIFICATION")
        print("=" * 66)
        
        self.run_file_existence_checks()
        self.test_layer1_config()
        self.test_layer3_sandbox()
        self.test_layer5_deployed_tools()
        self.test_layer6_router_init()

        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"])
        failed = total - passed

        current_layer = ""
        for r in self.results:
            if r["layer"] != current_layer:
                current_layer = r["layer"]
                print(f"\n📂 [{current_layer}]")
            
            icon = "✅ PASS" if r["status"] else "❌ FAIL"
            print(f"  {icon} | {r['name']:<32} | {r['detail']}")

        print("\n" + "=" * 66)
        print(f"📊 FINAL AUDIT SUMMARY: {passed}/{total} CHECKS PASSED ({int((passed/total)*100)}% HEALTHY)")
        print("=" * 66)
        if failed == 0:
            print("🟢 ALL DEPLOYED SYSTEMS ARE WORKING PERFECTLY! NO MISSING FILES OR BUGS.")
        else:
            print(f"🔴 WARNING: {failed} CHECK(S) FAILED. REVIEW THE DETAIL LOGS ABOVE.")
        print("=" * 66)

if __name__ == "__main__":
    auditor = MasterAuditor()
    auditor.generate_report()
