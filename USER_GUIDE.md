# MathPuzzle User Guide

Welcome to MathPuzzle! This guide will help you get started with the math quiz game in both console and web versions.

## Quick Start

1. **Install Python 3.7+** if not already installed.
2. **Install dependencies**: `pip install flask flask-socketio eventlet`
3. **Download** all project files to the same directory.

## Console Version

### Starting the Game
Run: `python math_game.py`

### Gameplay Steps
1. Enter your name when prompted.
2. Choose a category and difficulty.
3. Choose game mode: Time Mode or Question Count Mode.
4. Answer questions as they appear.
5. View your score and high scores.

## Web Version

### Starting the Server
Run: `python app.py`
Open your browser to: `http://127.0.0.1:5000/`

### Single Player Gameplay
1. Enter your name and select a category and difficulty.
2. Choose a game mode and value.
3. Click "Start Game".
4. Answer questions and view your final score.

### Live Multiplayer Mode (Beta)
1. Check the **"Live Multiplayer Mode"** box before starting.
2. You will be sent to the **Multiplayer Lobby**.
3. Share the URL with friends so they can join the same lobby.
4. Once everyone has joined, anyone can click **"Start Game for Everyone"**.
5. All players will begin the game at the same time.
6. A **Live Scoreboard** on the right side will update in real-time as players answer correctly.

### Leaderboard Features
The web version features an enhanced leaderboard:
- **Filtering**: Filter scores by **Category** and **Difficulty**.
- **Sorting**: Click column headers (**Name**, **Score %**, **Time Taken**) to sort.
- **Reset**: Clear all filters to see all scores.

## Troubleshooting
- **Multiplayer not syncing?** Ensure you are running the server with `eventlet` support (done automatically via `app.py`).
- **Web server not starting?** Check if port 5000 is occupied.
- **High scores not saving?** Ensure `highscores.json` is writable.

For more details, see the full README.md.
