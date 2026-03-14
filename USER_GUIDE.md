# MathPuzzle User Guide

Welcome to MathPuzzle! This guide will help you get started with the math quiz game in both console and web versions.

## Quick Start

1. **Install Python 3.7+** if not already installed.
2. **Install Flask** for the web version: `pip install flask`
3. **Download** all project files to the same directory.

## Console Version

### Starting the Game
Run: `python math_game.py`

### Gameplay Steps
1. Enter your name when prompted.
2. Choose a category:
   - 1: Basic Arithmetic
   - 2: Decimals and Fractions
   - 3: Percentages
   - 4: Profit and Loss
   - 5: Algebra
3. Select difficulty:
   - 1: Easy
   - 2: Medium
   - 3: Hard
4. Choose game mode:
   - 1: Time Mode - Answer as many questions as you can in X seconds (5-300 seconds)
   - 2: Question Count Mode - Answer exactly X questions (1-100 questions)
5. Enter your custom time or question count.
6. Answer questions as they appear.
7. Type 'quit' to end early.
8. View your score and high scores.

### Tips
- Answers are checked with a small tolerance for decimals.
- Press Enter after each round to continue.

## Web Version

### Starting the Server
Run: `python app.py`

Open your browser to: `http://127.0.0.1:5000/`

### Gameplay Steps
1. Enter your name.
2. Select a category and difficulty from the dropdowns.
3. Choose a game mode:
   - **Time Mode**: Answer as many as you can in X seconds (5-300 seconds, default 20)
   - **Question Count Mode**: Answer exactly X questions (1-100 questions, default 10)
4. Enter your custom time or question count value.
5. Click "Start Game".
6. Answer the questions shown.
7. Submit each answer.
8. View your final score.
9. Click "Play Again" or "View Leaderboard".

### Navigation
- **Leaderboard**: Click the link on the main page or game over page.
- **Quit**: Use the "End Game" link during play.

## General Tips
- Practice with Easy difficulty first.
- Some categories have limited difficulty support.
- Scores are saved automatically.
- Close the terminal or browser tab to exit.

## Troubleshooting
- **Web server not starting?** Ensure Flask is installed and port 5000 is free.
- **Questions not loading?** Check if all question files are present.
- **High scores not saving?** Ensure write permissions for `highscores.json`.

For more details, see the full README.md.</content>
<parameter name="filePath">/Users/keshavbindal/IdeaProjects/AIHandsOn/USER_GUIDE.md
