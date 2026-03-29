# MathPuzzle

A fun and educational math quiz game available in both console and web interfaces. Test your math skills across various categories and difficulty levels within a time limit!

📖 **[Quick User Guide](USER_GUIDE.md)** - Step-by-step instructions for getting started.
🎮 **[Game Mode Feature](GAME_MODE_FEATURE.md)** - Learn about Time Mode and Question Count Mode options.
📊 **[Medium Mode Logic](MEDIUM_MODE_EXPLANATION.md)** - Deep dive into how medium difficulty works for Percentage and Profit questions.

## Features

### Game Modes
- **Console Version**: Interactive command-line interface for quick play.
- **Web Version**: User-friendly web application built with Flask.

### Question Categories
- **Basic Arithmetic**: Addition, subtraction, multiplication, and division.
- **Decimals and Fractions**: Operations with decimal numbers and fractions.
- **Percentages**: Calculate percentages and percentage-based problems.
- **Profit and Loss**: Business math problems involving profit and loss calculations.
- **Algebra**: Simple algebraic equations.

### Difficulty Levels
- **Easy**: Smaller numbers and simpler operations. Open-ended questions.
- **Medium**: Moderate complexity. Multiple-choice questions (4 options).
- **Hard**: Larger numbers and more challenging problems. Multiple-choice questions (4 options).

### Gameplay
- **Timed Challenges**: Answer as many questions as you can in a custom time limit (5-300 seconds, default 20 seconds).
- **Question Count Mode**: Answer a specific number of questions (1-100, default 10 questions).
- **Scoring**: Earn points for each correct answer.
- **Leaderboard**: View high scores with details like time taken and score percentage. **Now includes sorting and filtering options.**
- **Session Management**: Web version supports user sessions for seamless gameplay.

### Web Application Features
- **Responsive Design**: Simple HTML/CSS interface.
- **Real-time Timer**: Client-side countdown during gameplay.
- **Multiple Choice UI**: Buttons for easy selection in Medium/Hard modes.
- **Form Validation**: Ensures proper input for names and answers.
- **Error Handling**: Displays messages for unimplemented categories/difficulties.
- **Navigation**: Easy access to leaderboard and game restart.
- **Enhanced Leaderboard**: Sort by Name, Score, or Time and filter by Category or Difficulty.

## Installation

### Prerequisites
- Python 3.7+
- Flask (for web version)
- Selenium (for UI tests)

### Setup
1. Clone or download the repository.
2. Install dependencies (if using virtual environment):
   ```bash
   pip install flask selenium
   ```
3. Ensure all files are in the same directory.

## Usage

### Console Version
Run the game from the command line:
```bash
python math_game.py
```
- Follow the menu prompts to select category and difficulty.
- Choose between **Time Mode** (answer as many as you can in X seconds) or **Question Count Mode** (answer exactly X questions).
- Enter your custom time limit (5-300 seconds) or question count (1-100).
- Answer questions as they appear.
- View high scores after each round.

### Web Version
Start the web server:
```bash
python app.py
```
- Open a web browser and go to `http://127.0.0.1:5000/`.
- Enter your name, select category and difficulty.
- Choose between **Time Mode** (custom time limit 5-300 seconds) or **Question Count Mode** (custom question count 1-100).
- Play the game and view your score.
- Check the leaderboard at `/leaderboard`. Use the new filtering and sorting options to customize the view.

### Testing
Run the test suites:
```bash
# Test console version
python -m unittest test_math_game.py

# Test web version
python -m unittest test_app.py

# Test UI automation
python test_ui_automation.py

# Run all tests
python run_all_tests.py
```

## Project Structure
```
AIHandsOn/
├── .ai-assistant-instructions   # AI agent instructions (Android Studio AI)
├── .copilot-instructions        # AI agent instructions (GitHub Copilot)
├── README.md                    # Project documentation
├── USER_GUIDE.md                # Quick user guide
├── app.py                       # Flask web application
├── math_game.py                 # Console game logic
├── test_math_game.py            # Tests for console version
├── test_app.py                  # Tests for web version
├── test_ui_automation.py        # UI automation tests
├── highscore_manager.py         # Highscore logic
├── highscores.json              # Persistent high scores
├── questions/                   # Question generation modules
│   ├── __init__.py
│   ├── base.py
│   ├── basic_arithmetic.py
│   ├── decimal_fraction.py
│   ├── percentage.py
│   ├── profit_loss.py
│   └── algebra.py
└── templates/                   # HTML templates for web app
    ├── index.html
    ├── game.html
    ├── game_over.html
    ├── leaderboard.html
    └── quit.html
```

## Contributing
Feel free to contribute by adding new question categories, difficulties, or improving the UI/UX.

## License
This project is open-source. Use and modify as needed for educational purposes.
