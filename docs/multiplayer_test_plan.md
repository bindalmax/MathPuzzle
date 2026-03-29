# Multiplayer Selenium Test Plan

## 1. Synchronization Test (Same Questions)
- **Scenario**: Two players join the same lobby and start the game.
- **Validation**:
  - Initialize two separate WebDriver instances (`driver1` and `driver2`).
  - Have both players join the same room.
  - Compare the text of the first question displayed on `driver1` and `driver2`.
- **Success Criteria**: The question text must be identical for both players.

## 2. Authorization Test (Creator Start Only)
- **Scenario**: A "Creator" and a "Joiner" are in the same lobby.
- **Validation**:
  - Check for the "Start Game for Everyone" button in the Creator's browser.
  - Check that the Joiner's browser **does not** see the button (or it is disabled/hidden).
  - Attempt to trigger the start via a manual script/URL as the Joiner and ensure it fails or is ignored.
- **Success Criteria**: Only the Creator has the UI element to trigger the game start.

## 3. Independence Test (Individual End Game)
- **Scenario**: Player A finishes the game (time expires or quits), while Player B is still playing.
- **Validation**:
  - Trigger an early "End Game" or wait for the timer on `driver1`.
  - Verify `driver1` is on the `game_over` page.
  - Verify `driver2` is **still** on the `game` page and can still submit answers.
- **Success Criteria**: Actions of one player do not force a redirect or state change for others.

## 4. Real-time Results Test (Auto-Refresh Scores)
- **Scenario**: Player A is already on the `game_over` page. Player B is still playing and scores a point.
- **Validation**:
  - On `driver1` (`game_over` page), locate the "Multiplayer Results" table.
  - On `driver2`, submit a correct answer.
  - Observe the table on `driver1` without a page refresh.
- **Success Criteria**: The score for Player B in Player A's results table increments automatically via WebSockets.