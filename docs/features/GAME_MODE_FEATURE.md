# Game Mode Feature Implementation

## Overview
The MathPuzzle application now supports two distinct game modes:
1. **Time Mode** - Players answer as many questions as possible within a custom time limit
2. **Question Count Mode** - Players answer a fixed number of questions

## Features

### Time Mode
- **Default Duration**: 20 seconds
- **Range**: 5-300 seconds
- **Gameplay**: Timer starts and counts down, game ends when time expires
- **Console Display**: Shows "Starting game for {Player}! You have X seconds."
- **Web Display**: Real-time countdown timer
- **Message**: "Time's up! Press Enter to see your score."

### Question Count Mode
- **Default Count**: 10 questions
- **Range**: 1-100 questions
- **Gameplay**: Game continues until all questions are answered correctly/incorrectly
- **Console Display**: Shows "Starting game for {Player}! Answer X questions."
- **Web Display**: Shows "Questions Left: X" updated after each answer
- **Message**: "You've answered X questions! Game over."

## Console Implementation

### Files Modified
- `math_game.py` - Game class updated with mode parameter

### Code Changes
```python
class Game:
    def __init__(self, player_name, question_factory, mode='time', value=20):
        # mode: 'time' or 'questions'
        # value: duration in seconds or number of questions
```

### User Flow
1. Select category and difficulty
2. Choose game mode:
   - Option 1: Time Mode
   - Option 2: Question Count Mode
3. Enter custom value (time or question count)
4. Game starts and runs based on selected mode

### Validation
- **Time Mode**: 5-300 seconds with user input validation
- **Question Count Mode**: 1-100 questions with user input validation

## Web Implementation

### Files Modified
- `app.py` - Routes updated to handle both modes
- `templates/index.html` - Form fields for mode selection
- `templates/game.html` - Conditional display of time or questions left

### Code Changes
- **Index Route**: Captures mode and value from form submission
- **Game Route**: Checks end condition based on mode (time elapsed or questions answered)
- **Submit Route**: Increments question counter

### User Interface
1. Dropdown menu to select game mode (Time Mode/Question Count Mode)
2. Dynamic input field that changes label and validation based on mode:
   - Time Mode: "Time in seconds (5-300)" with number input
   - Question Count Mode: "Number of questions (1-100)" with number input
3. JavaScript `toggleModeInput()` function handles dynamic updates

### Session Management
Session variables:
- `mode`: 'time' or 'questions'
- `mode_value`: User-provided time or question count
- `questions_answered`: Tracked for question count mode

## Testing

### Test Coverage
- **Console Tests**: 20 tests covering question generation and game logic
  - `test_run_game_loop_quit()` - Time mode termination
  - `test_game_ends_after_timer()` - Timer functionality
  - `test_game_question_count_mode()` - Question count mode (NEW)
  
- **Web Tests**: 8 tests covering Flask routes
  - All tests pass with both mode implementations

### Total: 28+ Tests (All Passing)

## Documentation Updates
- **README.md**: Features and usage sections updated
- **USER_GUIDE.md**: Step-by-step instructions updated for both modes
- **.copilot-instructions**: Guidelines for maintaining feature updated

## Backward Compatibility
- Default behavior preserved: Time mode with 20 seconds
- Console: `Game(player_name, factory)` defaults to time mode
- Web: Forms always require mode selection, with defaults

## User Experience Enhancements
1. **Flexibility**: Players can choose preferred game style
2. **Customization**: Adjust game length to available time or preferred difficulty
3. **Variety**: Different modes provide different challenges:
   - Time Mode: Speed and accuracy pressure
   - Question Count Mode: Focused, structured challenges

## Validation & Error Handling
- **Console**: Input validation with retry loops for invalid entries
- **Web**: HTML5 input constraints (min/max) and JavaScript validation
- Both versions prevent out-of-range values

## Future Enhancements
- Difficulty-based default modes (harder difficulties prefer question mode)
- Leaderboard filtering by mode
- Statistics tracking per mode
- Customizable default values in configuration file

