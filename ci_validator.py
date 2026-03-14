#!/usr/bin/env python
"""
Comprehensive CI/CD Validation Script
Runs all tests and validation checks before deployment
"""

import subprocess
import sys
import os
from pathlib import Path

class CIValidator:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def run_check(self, name, command, critical=True):
        """Run a single check and track results"""
        print(f"\n[{'CRITICAL' if critical else 'WARNING'}] {name}...")
        print("-" * 70)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(f"✅ PASS: {name}")
                self.results.append((name, "PASS", critical))
                self.passed += 1
                return True
            else:
                print(f"❌ FAIL: {name}")
                if result.stderr:
                    print(f"Error: {result.stderr[:200]}")
                self.results.append((name, "FAIL", critical))
                self.failed += 1
                return not critical  # Critical failures stop execution
        except subprocess.TimeoutExpired:
            print(f"❌ TIMEOUT: {name}")
            self.results.append((name, "TIMEOUT", critical))
            self.failed += 1
            return False
        except Exception as e:
            print(f"❌ ERROR: {name} - {str(e)}")
            self.results.append((name, "ERROR", critical))
            self.failed += 1
            return False

    def run_all_checks(self):
        """Run all validation checks"""
        print("=" * 70)
        print("COMPREHENSIVE CI/CD VALIDATION")
        print("=" * 70)
        print(f"Workspace: {os.getcwd()}")
        print(f"Python Version: {sys.version}")
        print("=" * 70)

        # Critical checks - must pass
        checks = [
            ("Python Syntax Check", "python -m py_compile *.py questions/*.py app.py math_game.py test_*.py", True),
            ("Import Verification", "python -c 'import math_game; import app; import questions'", True),
            ("Unit Tests - Math Game", "python -m unittest test_math_game.py -v", True),
            ("Unit Tests - Web App", "python -m unittest test_app.py -v", True),
            ("All Tests Discovery", "python -m unittest discover -s . -p 'test_*.py'", True),
        ]

        # Run all checks
        all_pass = True
        for name, cmd, critical in checks:
            if not self.run_check(name, cmd, critical):
                if critical:
                    all_pass = False

        # Print summary
        self.print_summary()

        return all_pass

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)

        for name, status, critical in self.results:
            icon = "🔴" if status != "PASS" else "🟢"
            level = "CRITICAL" if critical else "WARNING"
            print(f"{icon} [{level}] {name}: {status}")

        print("=" * 70)
        print(f"Total: {self.passed + self.failed} checks")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print("=" * 70)

        if self.failed == 0:
            print("\n✅ ALL CHECKS PASSED!")
            print("🚀 Ready for deployment!")
            return 0
        else:
            print(f"\n❌ {self.failed} check(s) failed!")
            print("⛔ Fix issues before deployment!")
            return 1

    def run(self):
        """Run the validator"""
        success = self.run_all_checks()
        return 0 if success else 1

if __name__ == '__main__':
    validator = CIValidator()
    exit_code = validator.run()
    sys.exit(exit_code)

