# Long-Term Backlog

### Scalability & Persistence
- Move multiplayer room storage to Redis for production scalability and persistence.
- Implement a 5-minute TTL cache for the global leaderboard to reduce database load.

### Security & Authentication
- Add a user account system with registration and login to track long-term progress.
- Secure REST API endpoints using JWT authentication for registered users.
- Implement stricter rate limiting on game-critical endpoints to prevent cheating.

### Android UI/UX Enhancements
- Add animations and haptic feedback to the Android app for better user engagement.
- Integrate sound effects and background music into the Flutter application.
- Implement an offline mode with local question caching for single-player practice.

### Infrastructure & Deployment
- Set up a CI/CD pipeline using GitHub Actions for automated testing and builds.
- Add analytics endpoints to track gameplay metrics and user engagement.
- Add unit and UI tests.

### UI/UX Simplification & Homepage Redesign
- **Implement progressive form disclosure**: Simplify the homepage form by showing only essential fields initially (GamerId → Game Type → mode-specific options).
- **Restructure to single-column focus layout**: Change from 2-column grid (form + lobbies) to single column with tab-based content switching.
- **Integrate lobby discovery as tab content**: Move Active Lobbies from side column to dedicated Multiplayer tab content.
- **Design card-based quick start system**: Create 3 visual action cards (Solo, Multiplayer, Startup) above tabs.
- **Reduce decorative visual elements**: Review and minimize math symbol decorations that add visual noise.

### Bug Fixes and Minor Improvements
- Bug: Multiplayer question synchronization is unreliable. Race conditions cause players to receive different questions at game start. (Currently disabled in E2E tests)
- Fix decimal answer discrepancy: Ensure questions either have whole number answers or provide choices with decimal precision.
