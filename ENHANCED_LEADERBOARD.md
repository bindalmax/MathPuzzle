# Enhanced Leaderboard Implementation

## Summary of Changes

The leaderboard has been improved to display category and difficulty level for each score. This provides players with better context about the scores achieved.

## Changes Made

### 1. HighscoreManager (math_game.py)

**Updated `add_score()` method:**
```python
def add_score(self, name, score, category="unknown", difficulty="unknown"):
    highscores = self.load()
    highscores.append({
        'name': name, 
        'score': score,
        'category': category,
        'difficulty': difficulty,
        'timestamp': time.time()
    })
    self.save(highscores)
    return highscores
```

**Updated `display()` method:**
- Now shows category and difficulty when displaying console leaderboard
- Example output: `1. Alice: 50 (Basic Arithmetic, Hard)`

### 2. Console Game (math_game.py)

Updated score saving to include category and difficulty:

```python
highscore_manager.add_score(player_name, final_score, category, difficulty)
```

### 3. Flask Web App (app.py)

**Updated game_over route:**

```python
category = session.get('category', 'unknown')
difficulty = session.get('difficulty', 'unknown')
highscore_manager.add_score(player_name, score, category, difficulty)
```

### 4. Leaderboard Template (templates/leaderboard.html)

**Enhanced HTML Table:**
- Added "Category" and "Difficulty" columns
- Responsive layout with 80% max-width of 1000px
- Professional styling with:
  - Gold (1st), Silver (2nd), Bronze (3rd) place highlighting
  - Color-coded difficulty badges:
    - Easy: Green background
    - Medium: Yellow background
    - Hard: Red background
  - Hover effects for better UX
  - Trophy emoji (🏆) in heading

### 5. Tests (test_math_game.py & test_app.py)

**Updated tests:**
- `test_add_score()`: Now verifies category and difficulty are stored
- `test_game_over()`: Session includes category and difficulty

## Data Structure

High scores are now stored in `highscores.json` with this structure:
```json
{
  "name": "Alice",
  "score": 50,
  "category": "basic",
  "difficulty": "hard",
  "timestamp": 1710086400.123
}
```

## Display Features

### Console Display
```
--- High Scores ---
1. Alice: 50 (Basic Arithmetic, Hard)
2. Bob: 35 (Percentage, Medium)
3. Charlie: 45 (Profit And Loss, Easy)
```

### Web Leaderboard Display
- Rank: 1-based ranking
- Name: Player name
- Score: Points earned
- Category: Question category (formatted with spaces)
- Difficulty: Color-coded badge (Easy/Medium/Hard)

## Backward Compatibility

The system handles old scores without category/difficulty data gracefully using `.get()` with default values of "Unknown".

## Files Modified

1. `/math_game.py` - HighscoreManager and game flow
2. `/app.py` - Flask game_over route
3. `/templates/leaderboard.html` - Enhanced leaderboard UI
4. `/test_math_game.py` - Updated score tests
5. `/test_app.py` - Updated game_over tests

## Visual Enhancements

- Modern color scheme with green headers
- Responsive table design
- Trophy emoji for visual appeal
- Difficulty color coding for quick identification
- Shadow effects for depth
- Hover effects for interactivity

