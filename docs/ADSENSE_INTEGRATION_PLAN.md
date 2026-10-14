# Implementation Plan: Google AdSense Integration for MathPuzzle

## Objective
Integrate Google AdSense into the existing Flask application to monetize the platform via non-intrusive banner and display ads, ensuring minimal impact on UX and game performance.

## Phase 1: Preparation & Compliance
- **Google AdSense Setup**: Register the domain and generate an AdSense `pub-ID`.
- **Security & Privacy**:
    - Add a Privacy Policy page (required for AdSense).
    - Update `src/templates/base.html` to include a GDPR/cookie consent banner if targeting EU/UK users.
- **CSP Adjustment**: Update the Content Security Policy (CSP) headers in `app.py` or `base.html` to allow loading scripts from `pagead2.googlesyndication.com` and `tpc.googlesyndication.com`.

## Phase 2: Technical Integration
- **Global Script Injection**: Inject the mandatory `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXX" crossorigin="anonymous"></script>` into the `<head>` of `src/templates/base.html`.
- **Component Creation**: Create a reusable Ad-Banner component (`src/templates/components/ad_banner.html`) that can be injected into different parts of the UI.

## Phase 3: Strategic Placement
- **Leaderboard Page**: Embed an ad banner between the filter section and the Hall of Fame table.
- **Game Over Page**: Embed a display ad unit beneath the game results and title.
- **Homepage (Lobby Tab)**: Place a small ad unit at the bottom of the "Active Lobbies" tab content to keep the main setup form clean.

## Phase 4: Performance & Optimization
- **Script Deferral**: Ensure all AdSense scripts are loaded asynchronously to prevent blocking the game’s core math/socket functionality.
- **Service Worker Exclusion**: Update `src/templates/sw.js` (or related service worker logic) to ensure ad requests are NOT intercepted or cached by the service worker, which can cause ad-serving issues.
- **Testing**:
    - Verify ad visibility on desktop and mobile viewports.
    - Check for any console errors during game initialization and socket events.

## Phase 5: Monitoring
- **Analytics Integration**: Ensure Google Analytics (if used) is not conflicting with AdSense.
- **UX Audit**: Review site performance metrics (Core Web Vitals) post-integration.

## Implementation Steps
1. Create the `ad_banner.html` component.
2. Modify `base.html` for script injection and CSP.
3. Update `leaderboard.html` and `game_over.html` templates.
4. Verify and push changes.
