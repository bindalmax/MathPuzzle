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

### Bug Fixes and Minor Improvements
- Fix decimal answer discrepancy: Ensure questions either have whole number answers or provide choices with decimal precision. Currently, users are confused when an expected answer is 17.90 but choices only show 18.
