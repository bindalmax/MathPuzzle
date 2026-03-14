# Method Dependencies & Usage Tracking

## Critical Methods and Their Dependencies

### 1. HighscoreManager.add_score()

**Method Signature:**
```python
def add_score(self, name, score, category="unknown", difficulty="unknown"):
    # Stores: name, score, category, difficulty, timestamp
```

**Used by:**
| File | Location | Function | Call | Status |
|------|----------|----------|------|--------|
| math_game.py | Line 184 | main() | `add_score(player_name, final_score, category, level)` | ✅ Updated |
| app.py | Line 112 | game_over() | `add_score(player_name, score, category, difficulty)` | ✅ Updated |
| test_math_game.py | Line 29 | test_add_score() | `add_score('Player1', 10, 'basic', 'easy')` | ✅ Updated |
| test_app.py | Line 94-95 | test_leaderboard() | `add_score('Player1', 10, 'basic', 'easy')` | ✅ Updated |

**Displayed by:**
| File | Location | Usage |
|------|----------|-------|
| math_game.py | Line 33-40 | display() - formats and prints scores |
| templates/leaderboard.html | Line 70-86 | Jinja2 template displays all fields |

**Accessed fields:**
- name: ✓
- score: ✓
- category: ✓ (NEW)
- difficulty: ✓ (NEW)
- timestamp: ✓ (NEW)

---

### 2. HighscoreManager.display()

**Method Signature:**
```python
def display(self, highscores):
    # Accesses: name, score, category, difficulty
    # Formats output with category and difficulty
```

**Used by:**
| File | Location | Context |
|------|----------|---------|
| math_game.py | Line 186 | After game ends, displays high scores |

**Accesses:**
- entry['name']: ✓
- entry['score']: ✓
- entry['category']: ✓ (Gets with .get() for backward compatibility)
- entry['difficulty']: ✓ (Gets with .get() for backward compatibility)

---

### 3. Game.__init__()

**Method Signature:**
```python
def __init__(self, player_name, question_factory, mode='time', value=20):
    # mode: 'time' or 'questions'
    # value: duration in seconds or question count
```

**Used by:**
| File | Location | Call | Status |
|------|----------|------|--------|
| math_game.py | Line 181 | main() | `Game(player_name, factory, mode=mode, value=value)` | ✅ Correct |
| test_math_game.py | Line 110 | test_run_game_loop_quit() | `Game("TestPlayer", mock_factory, mode='time', value=20)` | ✅ Correct |
| test_math_game.py | Line 123 | test_game_ends_after_timer() | `Game("TestPlayer", mock_factory, mode='time', value=20)` | ✅ Correct |
| test_math_game.py | Line 150 | test_game_question_count_mode() | `Game("TestPlayer", mock_factory, mode='questions', value=3)` | ✅ Correct |

---

### 4. Flask route: game_over()

**Session Variables Used:**
| Variable | Type | Set by | Used for |
|----------|------|--------|----------|
| player_name | string | index route | Display in game_over |
| score | int | game logic | Display and save |
| category | string | index route | Save with score |
| difficulty | string | index route | Save with score |
| start_time | float | game route | Timer tracking |
| current_answer | float | game route | Answer validation |
| mode | string | index route | Game termination logic |
| mode_value | int | index route | Timer/question count limit |
| questions_answered | int | submit_answer | Question count tracking |

**Called from:**
| File | Location | Context |
|------|----------|---------|
| templates/game.html | Line - | Redirect on game over |
| templates/leaderboard.html | - | Navigate after game |

---

## Dependency Change Impact Analysis

### If you change: HighscoreManager.add_score() signature

**Impact radius:**
1. **Direct Usage** (4 files):
   - math_game.py: main()
   - app.py: game_over()
   - test_math_game.py: test_add_score()
   - test_app.py: test_leaderboard()

2. **Indirect Usage** (2 files):
   - math_game.py: display() - accesses fields
   - templates/leaderboard.html - displays fields

3. **Related Tests** (2 files):
   - test_math_game.py: TestHighscoreManager (3 tests)
   - test_app.py: TestWebApp (8 tests)

**Checklist before changing:**
- [ ] Update method signature
- [ ] Update 4 direct usages
- [ ] Verify display() logic
- [ ] Update HTML template
- [ ] Update 3 highscore manager tests
- [ ] Update 8 web app tests
- [ ] Run full test suite
- [ ] Check backward compatibility

### If you change: Game.__init__() signature

**Impact radius:**
1. **Direct Usage** (1 file):
   - math_game.py: main()

2. **Related Tests** (1 file):
   - test_math_game.py: TestGame (3 tests)

**Checklist before changing:**
- [ ] Update method signature
- [ ] Update 1 direct usage in main()
- [ ] Update 3 game tests
- [ ] Run TestGame suite
- [ ] Run full test suite

---

## Testing Checklist for Method Changes

### Before Committing Code

```bash
# Step 1: Search for all usages
grep -r "add_score\|Game\(" --include="*.py" .

# Step 2: Verify all usages updated
# (Method signatures and calls should match)

# Step 3: Run syntax check
python -m py_compile *.py questions/*.py

# Step 4: Run relevant tests
python -m unittest test_math_game.TestHighscoreManager -v
python -m unittest test_app.TestWebApp -v

# Step 5: Run all tests
python -m unittest discover -s . -p "test_*.py"

# Step 6: Verify no hardcoded test data
grep -r "magic number\|hardcode" --include="*.py" test_*.py
```

### Before Deployment

```bash
# Run the CI validator
python ci_validator.py

# Expected output:
# ✅ ALL CHECKS PASSED!
# 🚀 Ready for deployment!
```

---

## Backward Compatibility Notes

### For add_score() - Default Parameters

```python
# Old code (without category/difficulty):
mgr.add_score('Player', 100, category, difficulty)


# Still works because:
def add_score(self, name, score, category="unknown", difficulty="unknown"):
# category defaults to "unknown"
# difficulty defaults to "unknown"
```

### For display() - Safe Field Access

```python
# Safe access with .get():
category = entry.get('category', 'unknown')
difficulty = entry.get('difficulty', 'unknown')

# Prevents KeyError if old scores don't have these fields
```

---

## Version Control Practices

### Good Commit Messages

```
commit: "Enhance leaderboard with category/difficulty tracking

- Update HighscoreManager.add_score() signature
- Add category and difficulty parameters (with defaults)
- Update all callers in math_game.py, app.py, tests
- Update leaderboard template to display new fields
- Maintain backward compatibility with default values
- All 28 tests passing"
```

### Dangerous Commit Messages

```
❌ "Fix stuff"
❌ "Update add_score"
❌ "Tests now pass" (without saying what changed)
❌ "Method signature change" (without listing all usages updated)
```

---

## Summary

**Key Dependencies Document:**
1. **add_score()** - Used in 4 files, displayed in 2 files
2. **Game.__init__()** - Used in 1 file, tested in 3 test methods
3. **display()** - Accesses new fields from add_score()
4. **leaderboard.html** - Displays new fields from add_score()

**Before changing any method:**
1. Grep for all usages
2. Update all callers
3. Update all tests
4. Run full test suite
5. Verify backward compatibility
6. Clear commit message

**Result:** No more TypeErrors! ✅

