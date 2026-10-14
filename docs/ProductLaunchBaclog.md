# 📋 Mathpuzzle Product Backlog

**Priority Legend:**
- **P0**: High Market Impact (The "Hook")
- **P1**: High Usability Impact (The "Stickiness")
- **P2**: Competitive/Social Depth
- **P3**: Technical Polish & Aesthetic

---

## 🚀 P0: Market Hooks (Immediate Growth)

### 1. The "Startup Challenge" Narrative Mode
* **Target Category:** Profit and Loss / Percentages.
* **Description:** Instead of isolated questions, create a 10-question "Business Simulation." Every correct answer grows a virtual startup; every wrong answer causes a loss.
* **Marketability:** Highly "shareable" on social media. Users love seeing a "CEO Score" rather than just a "Math Score."

### 2. PyPI & Homebrew CLI Release
* **Target Category:** Console Version.
* **Description:** Package the console version for easy installation (`pip install mathpuzzle` or `brew install mathpuzzle`).
* **Marketability:** Captures the "Developer/Linux Enthusiast" niche. This creates a viral "cool factor" within the tech community.

### 3. Progressive Web App (PWA) Conversion
* **Target Category:** Web Version.
* **Description:** Add a web manifest and service worker to allow users to "Install" the web app on their mobile home screen.
* **Usability:** Solves the "Web vs. Mobile" debate instantly. It allows offline play and makes the app feel native without the overhead of the App Store.

---

## 📈 P1: Retention & Usability (The "Stickiness")

### 4. AI-Driven "Survival" Timer
* **Target Category:** Timed Challenges.
* **Description:** A mode where the timer starts at 10 seconds and shrinks by 0.5 seconds for every correct answer, but gains 2 seconds for every "Perfect" (fast) answer.
* **Usability:** Prevents the "Easy is too boring" plateau. Keeps the user in a state of "Flow."

### 5. LaTeX Equation Rendering
* **Target Category:** Algebra / Fractions.
* **Description:** Integrate `MathJax` or `KaTeX` into the Flask templates.
* **Usability:** Fractions and Algebra equations look professional ($\frac{2}{3}x + 5 = 12$) rather than messy text (`2/3x + 5 = 12`). Essential for credibility in the educational market.

### 6. Personal Progress Analytics
* **Target Category:** Session Management.
* **Description:** Use the existing session data to show a simple graph of "Accuracy vs. Time" over the last 7 days.
* **Usability:** Users stay when they can see their brain getting faster.

---

## 🏆 P2: Social & Competitive Depth

### 7. "Ghost" Racing (Async Multiplayer)
* **Target Category:** Multiplayer / WebSockets.
* **Description:** Allow users to challenge a top score from the leaderboard. The WebSocket streams the "Ghost" of the record-holder's progress bar in real-time.
* **Marketability:** Allows for competition even when a live opponent isn't available.

### 8. Shareable "Room UUID" via URL
* **Target Category:** Security / Multiplayer.
* **Description:** Update the room logic so `mathpuzzle.com/play/[UUID]` automatically joins a room.
* **Usability:** Makes "Invite a Friend" a one-click process on WhatsApp or Discord.

### 9. Ranked Matchmaking
* **Target Category:** Multiplayer.
* **Description:** Use the Leaderboard data to group players into "Bronze, Silver, Gold" brackets for WebSocket games.
* **Marketability:** High competitive appeal for students and hardcore puzzle fans.

---

## 🎨 P3: Technical Polish & Aesthetic

### 10. "Precision Mode" for Hard Difficulty
* **Target Category:** Difficulty Levels.
* **Description:** Remove Multiple Choice for "Hard" mode. Require a direct numeric or algebraic string input.
* **Usability:** Ensures that "Hard" is actually hard and prevents "process of elimination" cheating.

### 11. Dark Mode / OLED Theme
* **Target Category:** UI/UX.
* **Description:** A CSS toggle for high-contrast dark mode.
* **Usability:** Reduces eye strain for late-night "Brain Training" sessions.

### 12. Haptic & Audio Feedback
* **Target Category:** Web Application.
* **Description:** Trigger the `navigator.vibrate()` API for mobile users on wrong answers and a high-pitched "ding" for correct ones.
* **Usability:** Provides immediate sensory reinforcement, making the game feel more "responsive."