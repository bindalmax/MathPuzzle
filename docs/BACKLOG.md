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

**Overview:** Streamline the homepage interface to reduce cognitive load, improve visual hierarchy, and enhance discoverability. Current implementation has 4 tabs with overlapping concerns and a cluttered 2-column layout.

#### High Priority
- **Reduce navigation tabs (4 → 3)**: Consolidate tabs to Solo Challenge, Multiplayer, and Startup Quest. Move Active Lobbies discovery into Multiplayer tab content for better organization.
- **Implement progressive form disclosure**: Simplify the homepage form by showing only essential fields initially (GamerId → Game Type → mode-specific options). Reduce cognitive load and improve UX flow.
- **Move sound/dark-mode controls to navbar**: Relocate sound (🎵/🔊) and dark mode (🌙) toggles from container top-right to main nav bar for better visual hierarchy and consistency with standard web UX patterns.

#### Medium Priority
- **Restructure to single-column focus layout**: Change from 2-column grid (form + lobbies) to single column with tab-based content switching. Improves mobile responsiveness and reduces context switching.
- **Integrate lobby discovery as tab content**: Move Active Lobbies from side column to dedicated Multiplayer tab content. Include Create New Game, Browse Lobbies, and Join interface all in one focused area.
- **Reorganize navbar for clarity**: Ensure navbar contains clear structure: Brand | Home | Leaderboard | Controls (🎵 🔊 🌙). Maintain clean visual hierarchy without floating decorative elements.

#### Lower Priority (Nice-to-Have)
- **Design card-based quick start system**: Create 3 visual action cards (Solo, Multiplayer, Startup) above tabs for immediate action without form interaction. Improves discoverability and entry points.
- **Reduce decorative visual elements**: Review and minimize math symbol decorations (∫ π Σ, √ x², etc) that add visual noise. Focus on content clarity over decoration.

---

### Bug Fixes and Minor Improvements
- Bug: Multiplayer question synchronization is unreliable. Race conditions cause players to receive different questions at game start. (Currently disabled in E2E tests)
- Fix decimal answer discrepancy: Ensure questions either have whole number answers or provide choices with decimal precision. Currently, users are confused when an expected answer is 17.90 but choices only show 18.
- Fix: Leaderboard alternate rows visibility in dark mode.
- Improvement: Make leaderboard alignment and table width dynamic for large screens to utilize available space effectively.
