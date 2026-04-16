# Testing Strategy & Best Practices

## Overview
This document outlines comprehensive testing strategies to catch issues like the `TypeError` before they reach production.

## 1. Unit Test Checklist

### Before Adding New Features
- [ ] Update method signatures in documentation
- [ ] Create unit tests for new parameters
- [ ] Test with default values
- [ ] Test with explicit values
- [ ] Test edge cases

### For Method Signature Changes
- [ ] Update ALL calls to the method
- [ ] Search entire codebase for method usage
- [ ] Create integration tests
- [ ] Test backward compatibility

**Example - For `add_score()` changes:**

```python
# Test 1: With all parameters
mgr.add_score('Player', 100, category, difficulty)

# Test 2: With defaults
mgr.add_score('Player', 100, category, difficulty)

# Test 3: With partial parameters
mgr.add_score('Player', 100, category, difficulty)
```

## 2. Integration Test Pattern

Create integration tests that verify the entire flow:

```python
class TestScoreSavingIntegration(unittest.TestCase):
    def test_end_to_end_score_flow(self):
        """Test complete score saving flow in both console and web"""
        # Console: add_score call
        mgr.add_score('Player',50,category,difficulty)
        
        # Web: Flask route calling add_score
        # Leaderboard: displaying the saved score
        # Verification: all parameters present
```

## 3. Grep Search Before Deployment

Before deploying any method signature change, search for all usages:

```bash
# Search for all calls to add_score
grep -r "add_score" --include="*.py" .

# Expected output should show:
# - Console game (math_game.py)
# - Web app (app.py)
# - Tests (test_*.py)
# - All should match new signature
```

## 4. Pre-Commit Test Hook

Create a script to run before committing code:

```bash
#!/bin/bash
# pre-commit-tests.sh

echo "Running syntax checks..."
python -m py_compile questions/*.py test_*.py app.py math_game.py

echo "Running all tests..."
python -m unittest discover -s . -p "test_*.py" -v

if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Fix before committing."
    exit 1
fi
echo "✅ All tests passed!"
```

## 5. Signature Verification Checklist

When modifying method signatures:

```python
# For: def add_score(self, name, score, category="unknown", difficulty="unknown")

SIGNATURE_CHANGES_CHECKLIST = {
    "math_game.py": {
        "display()": "verify formatting with new fields",
        "main()": "verify add_score calls with new params"
    },
    "app.py": {
        "game_over()": "verify session has category/difficulty",
        "leaderboard()": "verify template can access new fields"
    },
    "templates/leaderboard.html": "verify template shows category/difficulty",
    "test_math_game.py": "verify test_add_score checks new params",
    "test_app.py": "verify all add_score calls include new params"
}
```

## 6. Automated Signature Validation

Create a test that validates method signatures:

```python
import inspect

class TestMethodSignatures(unittest.TestCase):
    def test_add_score_signature(self):
        """Verify add_score has expected parameters"""
        sig = inspect.signature(HighscoreManager.add_score)
        params = list(sig.parameters.keys())
        
        expected = ['self', 'name', 'score', 'category', 'difficulty']
        self.assertEqual(params, expected)
    
    def test_all_add_score_calls_use_new_signature(self):
        """Verify all add_score calls match signature"""
        # Read source files and check all calls
        # This catches missing parameters at test time
```

## 7. Code Review Checklist

Use this checklist when reviewing code:

### For Method Changes
- [ ] Is the method signature documented?
- [ ] Are ALL calls to this method updated?
- [ ] Did you grep for all usages?
- [ ] Are tests updated?
- [ ] Do tests cover new parameters?
- [ ] Are backward-compatible defaults provided?

### For Test Updates
- [ ] Do tests match actual method signatures?
- [ ] Are all parameters passed explicitly?
- [ ] Are edge cases tested?
- [ ] Is there integration test coverage?

## 8. Continuous Integration Script

```python
# ci_validation.py
import subprocess
import sys

def run_tests():
    """Run comprehensive test suite"""
    print("=" * 70)
    print("COMPREHENSIVE TEST VALIDATION")
    print("=" * 70)
    
    tests = [
        ("Syntax Check", "python -m py_compile **/*.py"),
        ("Import Check", "python -c 'import test_math_game; import test_app'"),
        ("Unit Tests", "python -m unittest test_math_game.py -v"),
        ("Web Tests", "python -m unittest test_app.py -v"),
        ("All Tests", "python -m unittest discover -s . -p 'test_*.py'"),
    ]
    
    results = []
    for name, cmd in tests:
        print(f"\nRunning: {name}...")
        result = subprocess.run(cmd, shell=True, capture_output=True)
        status = "✅ PASS" if result.returncode == 0 else "❌ FAIL"
        results.append((name, status))
        print(status)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, status in results:
        print(f"{name}: {status}")
    
    return all("PASS" in status for _, status in results)

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
```

## 9. Test Coverage by Component

Ensure every component that uses a changed method is tested:

```
Method: add_score(name, score, category, difficulty)

Used in:
├── math_game.py
│   └── Test: TestHighscoreManager.test_add_score ✓
├── app.py
│   └── Test: TestWebApp.test_game_over ✓
├── app.py
│   └── Test: TestWebApp.test_leaderboard ✓
└── templates/leaderboard.html
    └── Test: TestWebApp.test_leaderboard ✓
```

## 10. Dependency Tracking

Create a file that documents method dependencies:

```python
# DEPENDENCIES.md

## add_score() Dependencies

**Signature:**
```python
def add_score(self, name, score, category="unknown", difficulty="unknown"):
```

**Used by:**
1. `math_game.py:main()` - Line 184
   - Called with: (player_name, final_score, category, level)
   - Status: ✓ Updated

2. `app.py:game_over()` - Line 112
   - Called with: (player_name, score, category, difficulty)
   - Status: ✓ Updated

3. `test_math_game.py:test_add_score()` - Line 29
   - Called with: ('Player1', 10, 'basic', 'easy')
   - Status: ✓ Updated

4. `test_app.py:test_leaderboard()` - Line 94-95
   - Called with: (name, score, category, difficulty)
   - Status: ✓ Updated

**Display by:**
1. `math_game.py:display()` - Accesses: name, score, category, difficulty
2. `templates/leaderboard.html` - Displays: name, score, category, difficulty
```

## 11. Validation Before Deployment

```bash
#!/bin/bash
# pre-deploy-check.sh

echo "1. Checking syntax..."
python -m py_compile *.py questions/*.py

echo "2. Running all tests..."
python -m unittest discover -s . -p "test_*.py"

echo "3. Checking for TODO/FIXME comments..."
grep -r "TODO\|FIXME" --include="*.py" .

echo "4. Verifying no hardcoded test data..."
grep -r "test_" --include=" ['*.py']" app.py math_game.py

echo "5. All checks passed! Ready to deploy."
```

## 12. Testing Philosophy

### Rule 1: Test the Interface, Not the Implementation
```python
# ❌ BAD - Tests internal state
self.assertEqual(len(mgr.highscores_list), 1)

# ✅ GOOD - Tests expected behavior
scores = mgr.load()
self.assertEqual(len(scores), 1)
```

### Rule 2: Test All Code Paths
```python
# For add_score with optional parameters:
# - With all parameters
# - With default parameters
# - Edge cases (empty strings, zero values)
```

### Rule 3: Update Tests When You Update Code
```
Code Change → Update Method Signature
            → Search for all usages
            → Update all calls
            → Update all tests
            → Run full test suite
            → Deploy
```

## 13. UI Automation Testing

### Overview
UI automation tests are used to verify the web application's user interface. These tests simulate user interactions in a real browser, ensuring that the frontend behaves as expected.

### Tools
- **Selenium:** A browser automation library.
- **unittest:** The standard Python testing framework.

### Running the Tests
To run the UI automation tests, execute the following command:
```bash
python test_ui_automation.py
```

### Prerequisites
Before running the tests, you need to have the following installed:
1.  **Selenium:**
    ```bash
    pip install selenium
    ```
2.  **WebDriver:** You need to have a WebDriver for your browser. For example, if you are using Chrome, you need to have `chromedriver` installed. You can download it from the official website and make sure it is in your system's PATH.

## Summary

To prevent issues like the TypeError:

1. **Grep before changes** - Search for all method usages
2. **Test comprehensively** - Unit + integration tests
3. **Document changes** - Update signature documentation
4. **Code review** - Use checklist for all changes
5. **CI/CD validation** - Run tests before deployment
6. **Track dependencies** - Know what uses what
7. **Pre-commit hooks** - Catch issues early
8. **Version control** - Clear commit messages about signature changes
