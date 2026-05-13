# Google SSO Implementation Plan (Web/PWA)

This document outlines the strategy for implementing Google Single Sign-On (SSO) for the MathPuzzle Web and Progressive Web Application (PWA).

## Dependencies & Prerequisites
- **Google Cloud Project:** Active project with "OAuth consent screen" configured.
- **Backend (Flask):** `google-auth` and `requests` libraries.
- **Frontend (Web):** Google Identity Services (GIS) JavaScript library.
- **Environment Variables:**
    - `GOOGLE_CLIENT_ID`
    - `GOOGLE_CLIENT_SECRET`

---

## Phase 1: Google Cloud Console Setup
1. **OAuth Consent Screen:**
   - Set User Type to "External".
   - Add scopes: `openid`, `https://www.googleapis.com/auth/userinfo.email`, `https://www.googleapis.com/auth/userinfo.profile`.
2. **Credentials Creation:**
   - **Web Client ID:** Create a "Web application" credential.
   - **Authorized JavaScript origins:** Add your production domain (e.g., `https://mathpuzzle.com`) and local dev URL (`https://localhost:5005`).
   - **Authorized redirect URIs:** Add the endpoint that will handle the login callback if using the redirect flow.

---

## Phase 2: Backend Implementation (Flask)
1. **Token Verification Endpoint:**
   - Create `POST /api/auth/google`.
   - Payload: `{ "credential": "..." }` (This is the ID Token returned by Google GIS).
   - Logic: 
     - Use `google.oauth2.id_token.verify_oauth2_token` to validate the token.
     - Extract `sub` (Google User ID), `email`, and `name`.
2. **User Management:**
   - Check if a user with this `google_id` exists in the database.
   - If not, **auto-generate a Gamer ID** (e.g., `Gamer_` + random suffix).
   - Create a session (e.g., via Flask-Session or JWT) for subsequent API calls.
3. **Database Schema Update:**
   - Add `google_id` (string, indexed, unique) to the user table.
   - Ensure Gamer ID is unique and editable by the user.

---

## Phase 3: Web & PWA Integration
1. **Google Identity Services (GIS):**
   - Include `<script src="https://accounts.google.com/gsi/client" async defer></script>`.
   - Implement **"One Tap" sign-in** for a seamless experience on return visits.
   - Add the standard "Sign in with Google" button to the landing page.
2. **Session Persistence in PWA:**
   - Ensure the backend sets a secure, `HttpOnly`, `SameSite=Lax` cookie.
   - This ensures that once the user is logged in via the browser, the PWA (standalone mode) inherits the session seamlessly.

---

## Phase 4: Security & GDPR Compliance
1. **Security:**
   - **Backend Verification:** Never trust a user ID or email sent directly from the frontend. Always verify the JWT token from Google.
   - **CSRF Protection:** Ensure state tokens or CSRF headers are used for the auth endpoint.
2. **GDPR:**
   - **Data Minimization:** Only store the unique Google ID and basic profile info needed for the Gamer ID.
   - **Transparency:** Update the Privacy Policy to disclose that Google is used for authentication.
   - **Account Deletion:** Implement a "Delete My Account" feature that purges all user-linked data.

---

## Implementation Checklist
- [ ] Create Google Cloud Project and Web Credentials.
- [ ] Add `google-auth` to `requirements.txt`.
- [ ] Implement `id_token` verification logic in the Flask backend.
- [ ] Update database schema to store `google_id`.
- [ ] Implement auto-generation logic for Gamer IDs.
- [ ] Integrate Google One Tap and Sign-In button in `index.html`.
- [ ] Verify session sharing between browser and standalone PWA mode.
- [ ] Update Privacy Policy for GDPR compliance.
