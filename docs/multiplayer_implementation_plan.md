# 4-Step Multiplayer Implementation Plan

## Phase 1: Question Synchronization & Room Ownership
1. **Server-Side Question Pool**: 
   - Modify `handle_start_game_request` in `app.py` to generate a fixed list of questions (e.g., 50–100) using the `QuestionFactory` and store them in the `rooms[room_id]` object.
   - Track `current_question_index` in the user's `session`.
   - Update the `/game` route to serve the question from the room's pre-generated list instead of creating a new one. This ensures all players face the exact same sequence.
2. **Creator Tracking**:
   - In the `index` route, when a multiplayer room is created, store the `player_name` as the `creator` in the `rooms[room_id]` dictionary.
   - Pass a `is_creator` boolean to `multiplayer_lobby.html`.

## Phase 2: UI Enhancements for Lobby & Game Over
3. **Restricted Start Button**:
   - In `templates/multiplayer_lobby.html`, wrap the "Start Game" button in a conditional check: `{% if is_creator %}`.
   - Non-creators will see a "Waiting for host to start..." message instead.
4. **Live Results on Game Over Page**:
   - Add SocketIO client logic to `templates/game_over.html`.
   - The page will listen for the existing `score_update` event.
   - When an update is received, the JavaScript will refresh the "Multiplayer Results" table in real-time without a page reload.

## Phase 3: Individual Game Flow Logic
5. **Decouple Game Over Signal**:
   - **Remove** the global `game_over_signal` emission from the `game_over` route in `app.py`.
   - Modify the `/game` timer: When a player's timer expires, only *that* player redirects to `/game_over`. 
   - Other players continue playing until their own timers expire or they finish their questions.
6. **Refine Session Cleanup**:
   - Ensure that players remain "joined" to the SocketIO room even after reaching the `game_over` page so they can continue receiving live score updates from players who are still finishing.

## Phase 4: Validation & Cleanup
7. **Room Persistence**: Keep the `rooms[room_id]` data alive until the last player leaves the results page or a timeout occurs, ensuring the "Live Results" remain accessible.
8. **Update Tests**: Modify `test_app.py` to verify that questions served to different sessions in the same room match.