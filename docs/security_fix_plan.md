# Security Fix Plan for MathPuzzle (Commit e44cb44d)

## Phase 1: Immediate Sanitization (XSS)
1. **Modify `templates/multiplayer_lobby.html`**:
   - Remove the `| safe` filter from `playerName`. Jinja2's default escaping is safer.
   - Use `tojson` for passing variables from Python to JavaScript to ensure they are properly quoted and escaped.

## Phase 2: Server-Authoritative Logic & Room Security
2. **Enhance Room Management in `app.py`**:
   - **Randomize Room IDs**: Replace predictable IDs (`category_difficulty`) with unique UUIDs to prevent room-guessing attacks.
   - **Authoritative Scores**: Initialize player scores in the global `rooms` object on the server when they join.
3. **Refactor Scoring Logic**:
   - Modify the `submit_answer` route in `app.py`. When a player answers correctly in a multiplayer game, the server should increment their score in the `rooms` object and then broadcast the update via `socketio.emit`.
   - **Remove Client-Side Score Emission**: Disable or remove the `answer` SocketIO event listener that accepts scores from the client. The client should only *receive* score updates.

## Phase 3: Authorization & Hardening
4. **Secure SocketIO Handlers**:
   - In `handle_start_game_request` and other events, verify that the sender's session actually belongs to the room they are trying to manipulate.
   - Use `flask_socketio.rooms()` to check if the current `sid` is a member of the target `room`.
5. **Environment Hardening**:
   - **Restrict CORS**: Update `SocketIO(app, ...)` to use a specific origin (or an environment variable) instead of `*`.
   - **Enforce Secret Keys**: Update `app.py` to raise an error if `SECRET_KEY` is not provided in a production environment (`FLASK_ENV=production`).

## Phase 4: Validation
6. **Update Tests**:
   - Modify `test_app.py` to reflect the new UUID-based room structure.
   - Add a test case to ensure that sending a manual `answer` event via a socket client no longer updates the leaderboard/score.