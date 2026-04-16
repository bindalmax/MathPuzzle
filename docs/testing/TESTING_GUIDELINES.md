# Comprehensive Testing Guidelines

## Quick Start

### Daily Development Workflow

```bash
# 1. Before starting work
git pull

# 2. Make code changes
# Edit files...

# 3. Before committing
python ci_validator.py

# 4. If all green, commit
git add .
git commit -m "Clear message about what changed"

# 5. Push to repository
git push
```

---

## Testing Pyramid

```
        △ Integration Tests (Fewest)
       △ △ System Tests
      △ △ △ Component Tests
     △ △ △ △ Unit Tests (Many)
```

### Unit Tests (test_*.py)
- **Focus**: Individual methods/functions
- **Speed**: Fast (< 1 second)
- **Coverage**: 80%+
- **Example**: test_add_score() tests the add_score() method alone

### Component Tests
- **Focus**: Class functionality
- **Example**: TestHighscoreManager tests the entire HighscoreManager class

### System Tests
- **Focus**: Multiple components working together
- **Example**: Game flow from start to leaderboard display

### Integration Tests
- **Focus**: Console + Web + Database
- **Example**: Player plays game → score saved → appears on leaderboard

---

## Test Categories in This Project

### Category 1: Console Game Tests (test_math_game.py)
**20 Tests Total**

#### Question Generation (5 categories × 3 difficulties)
```python
TestBasicArithmeticQuestion - 1 test
TestDecimalFractionQuestion - 2 tests
TestPercentageQuestion - 3 tests
TestAlgebraQuestion - 2 tests
TestProfitLossQuestion - 4 tests
```

**What's Tested:**
- Each category generates valid questions
- Each difficulty produces appropriate complexity
- Answers are correct and in expected format

#### Game Mechanics (3 tests)
```python
TestGame.test_run_game_loop_quit
TestGame.test_game_ends_after_timer
TestGame.test_game_question_count_mode
```

**What's Tested:**
- Game quit functionality
- Timer-based termination
- Question count termination

#### Highscore Management (3 tests)
```python
TestHighscoreManager.test_load_no_file
TestHighscoreManager.test_save_and_load
TestHighscoreManager.test_add_score  [CRITICAL]
```

**What's Tested:**
- Score persistence
- Field storage (name, score, category, difficulty, timestamp)
- Backward compatibility

### Category 2: Web App Tests (test_app.py)
**8 Tests Total**

```python
TestWebApp.test_index_get
TestWebApp.test_index_post_valid
TestWebApp.test_game_with_session
TestWebApp.test_game_without_session
TestWebApp.test_submit_answer_correct
TestWebApp.test_game_over  [CRITICAL]
TestWebApp.test_leaderboard  [CRITICAL]
TestWebApp.test_quit
```

**What's Tested:**
- Route accessibility
- Session management
- Form submission
- Score saving flow
- Leaderboard display

---

## Critical Tests (Must Always Pass)

These tests catch the most common issues:

| Test | Why Critical | What It Catches |
|------|-------------|-----------------|
| test_add_score | Verifies score structure | Missing/wrong fields |
| test_game_over | Verifies session data | Missing category/difficulty |
| test_leaderboard | Verifies display logic | TypeError from wrong parameters |

**Before deployment, verify:**
```bash
python -m unittest test_math_game.TestHighscoreManager.test_add_score -v
python -m unittest test_app.TestWebApp.test_game_over -v
python -m unittest test_app.TestWebApp.test_leaderboard -v
```

---

## Test Writing Best Practices

### Rule 1: Clear Test Names

```python
# ❌ BAD
def test_1(self):
    pass

# ✅ GOOD
def test_add_score_with_category_and_difficulty(self):
    pass
```

### Rule 2: Arrange-Act-Assert Pattern

```python
def test_add_score_with_category_and_difficulty(self):
    # ARRANGE: Set up test data
    manager = HighscoreManager('test.json')

    # ACT: Perform the action
    manager.add_score('Player', 100, category, difficulty)

    # ASSERT: Verify results
    scores = manager.load()
    self.assertEqual(scores[0]['category'], 'basic')
    self.assertEqual(scores[0]['difficulty'], 'hard')
```

### Rule 3: Test Both Success and Failure

```python
def test_add_score_success(self):
    """Test successful score addition"""
    manager.add_score('Player', 100, category, difficulty)
    self.assertEqual(len(manager.load()), 1)


def test_add_score_defaults(self):
    """Test score addition with default parameters"""
    manager.add_score('Player', 100, category, difficulty)
    score = manager.load()[0]
    self.assertEqual(score['category'], 'unknown')
    self.assertEqual(score['difficulty'], 'unknown')
```

### Rule 4: Use Meaningful Assertions

```python
# ❌ BAD - Generic assertion
self.assertTrue(result)

# ✅ GOOD - Specific assertion
self.assertEqual(score['category'], 'basic', 
                 "Score should have category 'basic'")
```

### Rule 5: Mock External Dependencies

```python
# ❌ BAD - Depends on file system
manager.add_score('Player', 100, category, difficulty)


# ✅ GOOD - Uses mocks for randomness
@patch('questions.random.choice', return_value='easy')
def test_with_mock(self, mock_choice):
# Test with controlled randomness
```

---

## Testing Checklist for New Features

When adding a new feature, follow this checklist:

```
Feature: Add ability to filter leaderboard by category

□ Write failing test first (TDD)
□ Implement the feature
□ Make test pass
□ Add edge case tests
  □ Empty leaderboard
  □ Unknown category
  □ Single entry
□ Update integration test
□ Run full test suite
  □ python -m unittest discover -s . -p "test_*.py"
□ No regression in other tests
□ Documentation updated
□ Code review completed
```

---

## Running Tests

### Run All Tests
```bash
python -m unittest discover -s . -p "test_*.py" -v
```

### Run Specific Test Class
```bash
python -m unittest test_math_game.TestHighscoreManager -v
```

### Run Specific Test Method
```bash
python -m unittest test_app.TestWebApp.test_leaderboard -v
```

### Run with CI Validator
```bash
python ci_validator.py
```

### Run with Pre-Commit Hook
```bash
bash pre-commit-validation.sh
```

---

## Fixing Test Failures

### When test_leaderboard fails with TypeError

**Step 1: Read the error**
```
TypeError: add_score() takes 3 positional arguments but 5 were given
```

**Step 2: Check the method signature**
```bash
grep -n "def add_score" math_game.py
```

**Step 3: Verify all callers**
```bash
grep -rn "add_score(" --include="*.py" .
```

**Step 4: Update mismatched calls**
```python
# Find: self.manager.add_score('Player1', 10)
# Replace: self.manager.add_score('Player1', 10, 'basic', 'easy')
```

**Step 5: Rerun test**
```bash
python -m unittest test_app.TestWebApp.test_leaderboard -v
```

---

## Test Statistics

**Current Project:**
- Total Tests: 28
- Pass Rate: 100% (after bug fix)
- Coverage: All major features
- Execution Time: < 1 second
- Critical Tests: 3

---

## Common Test Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| TypeError in add_score | Method signature mismatch | Update all callers |
| ImportError | Missing module | Check imports in test file |
| AssertionError | Expected value ≠ actual | Debug and fix implementation |
| Timeout | Infinite loop | Check game termination logic |

---

## Continuous Improvement

### Monthly Review
- [ ] Check test coverage (should be > 80%)
- [ ] Review test failures (identify patterns)
- [ ] Update test documentation
- [ ] Refactor flaky tests

### Quarterly Review
- [ ] Add tests for new features
- [ ] Remove redundant tests
- [ ] Optimize slow tests
- [ ] Update testing strategy

---

## Summary

**To ensure well-tested code:**

1. **Write tests first** (Test-Driven Development)
2. **Test all code paths** (success, failure, edge cases)
3. **Use CI validator** before deployment
4. **Grep for method usage** before changing signatures
5. **Update ALL callers** when signature changes
6. **Run full test suite** after any code change
7. **Document test dependencies** for future devs
8. **Use pre-commit hooks** to catch issues early

**Result:** No more TypeErrors! ✅

