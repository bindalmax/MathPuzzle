# MathPuzzle

A fun and educational math quiz game available in both console and web interfaces. Test your math skills across various categories and difficulty levels within a time limit!

📖 **[Quick User Guide](USER_GUIDE.md)** - Step-by-step instructions for getting started.

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
- **Easy**: Smaller numbers and simpler operations.
- **Medium**: Moderate complexity.
- **Hard**: Larger numbers and more challenging problems.

### Gameplay
- **Timed Challenges**: Answer as many questions as possible in 20 seconds.
- **Scoring**: Earn points for each correct answer.
- **Leaderboard**: View top 10 high scores.
- **Session Management**: Web version supports user sessions for seamless gameplay.

### Web Application Features
- **Responsive Design**: Simple HTML/CSS interface.
- **Real-time Timer**: Client-side countdown during gameplay.
- **Form Validation**: Ensures proper input for names and answers.
- **Error Handling**: Displays messages for unimplemented categories/difficulties.
- **Navigation**: Easy access to leaderboard and game restart.

## Installation

### Prerequisites
- Python 3.7+
- Flask (for web version)

### Setup
1. Clone or download the repository.
2. Install dependencies (if using virtual environment):
   ```bash
   pip install flask
   ```
3. Ensure all files are in the same directory.

## Usage

### Console Version
Run the game from the command line:
```bash
python math_game.py
```
- Follow the menu prompts to select category and difficulty.
- Answer questions as they appear.
- View high scores after each round.

### Web Version
Start the web server:
```bash
python app.py
```
- Open a web browser and go to `http://127.0.0.1:5000/`.
- Enter your name, select category and difficulty.
- Play the game and view your score.
- Check the leaderboard at `/leaderboard`.

### Testing
Run the test suites:
```bash
# Test console version
python -m unittest test_math_game.py

# Test web version
python -m unittest test_app.py

# Run all tests
python -m unittest test_math_game.py test_app.py
```

## Project Structure
```
AIHandsOn/
├── .copilot-instructions        # AI agent instructions for the project
├── README.md                    # Project documentation
├── USER_GUIDE.md                # Quick user guide
├── app.py                       # Flask web application
├── math_game.py                 # Console game logic
├── test_math_game.py            # Tests for console version
├── test_app.py                  # Tests for web version
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
