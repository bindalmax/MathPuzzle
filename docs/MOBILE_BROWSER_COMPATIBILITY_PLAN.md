# Mobile & Browser Compatibility Implementation Plan (Updated)

## Overview
Make MathPuzzle application responsive, mobile-friendly, and cross-browser compatible.

## Strategy
- **Base layout template** (`base.html`) with shared `<head>`, viewport, and block-based structure.
- **Shared `static/css/responsive.css`** for complex media queries.
- **Mobile-First Design**: Optimized for 320px width upwards.
- **Touch Optimization**: Minimum touch targets of 44px for buttons and links.

---

## Phase 1: Create Base Template
### File: `templates/base.html`
- Use `{% block scripts %}` to load Socket.IO only where needed.
- Standardized viewport and container structure.
- CSS variables for consistent coloring.

---

## Phase 2: Create Shared CSS
### File: `static/css/responsive.css`
- **Grid/Flexbox Layout**: Responsive container for "New Game" and "Join Lobby" boxes.
- **Input Optimization**: Font-size at 16px to prevent iOS auto-zoom.
- **Room Discovery**: Styling for `.room-item` cards to be stackable and touch-friendly.
- **Live Scores**: Repositioned for visibility on smaller screens (relative layout vs fixed).

---

## Phase 3: Update Templates
### 3.1 `templates/index.html`
- Extend base.html.
- Use CSS Grid for the two setup boxes.
- Style `room-list` and `room-item` for mobile.
### 3.2 `templates/game.html`
- Extend base.html.
- Responsive choice buttons (stacking on narrow screens).
- Responsive live-scores panel.
### 3.3 `templates/game_over.html`
- Extend base.html.
- Responsive results table (horizontal scroll if needed).
### 3.4 `templates/leaderboard.html`
- Extend base.html.
- Wrap table in `.table-container` for mobile scrolling.
### 3.5 `templates/quit.html` & `templates/multiplayer_lobby.html`
- Extend base.html.
- Uniform container widths.

---

## Phase 4: Accessibility & Hardening
- **ARIA Labels**: Add descriptive labels for screen readers.
- **Focus States**: High-visibility focus indicators for keyboard navigation.
- **Dark Mode Support**: (Optional/Future) using `prefers-color-scheme`.

---

## Files Summary
| Action | File |
| :--- | :--- |
| CREATE | `templates/base.html` |
| CREATE | `static/css/responsive.css` |
| MODIFY | All existing `.html` files in `templates/` |

---

## Testing Checklist
- [ ] Layout responsive on mobile (320px+)
- [ ] Touch targets are 44px+
- [ ] No horizontal overflow on any page
- [ ] iOS auto-zoom disabled (via 16px font size)
- [ ] Leaderboard table scrollable on mobile
- [ ] Keyboard navigation (Tab) works logically
