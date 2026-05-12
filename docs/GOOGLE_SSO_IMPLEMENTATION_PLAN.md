# Google SSO Implementation Plan

This document outlines the strategy for implementing Google Single Sign-On (SSO) across the MathPuzzle Web/PWA and Flutter Mobile applications.

## Dependencies & Prerequisites
- **Google Cloud Project:** Active project with "OAuth consent screen" configured.
- **Backend (Flask):** `google-auth` and `requests` libraries.
- **Frontend (Web):** Google Identity Services (GIS) JavaScript library.
- **Frontend (Mobile):** `google_sign_in` Flutter plugin.
- **Environment Variables:**
    - `GOOGLE_CLIENT_ID` (Web)
    - `GOOGLE_CLIENT_ID_ANDROID`
    - `GOOGLE_CLIENT_ID_IOS`
    - `GOOGLE_CLIENT_SECRET` (Backend)

---

## Phase 1: Google Cloud Console Setup
1. **OAuth Consent Screen:**
   - Set User Type to "External".
   - Add scopes: `openid`, `https://www.googleapis.com/auth/userinfo.email`, `https://www.googleapis.com/auth/userinfo.profile`.
2. **Credentials Creation:**
   - **Web Client ID:** For PWA and Web version. Add Authorized JavaScript origins and redirect URIs.
   - **Android Client ID:** Requires SHA-1 fingerprint from your signing certificate.
   - **iOS Client ID:** Requires Bundle ID.

---

## Phase 2: Backend Implementation (Flask)
1. **Token Verification Endpoint:**
   - Create `POST /api/auth/google`.
   - Payload: `{ "id_token": "..." }`.
   - Logic: 
     - Use `google.oauth2.id_token.verify_oauth2_token` to validate the token.
     - Extract `sub` (Google User ID), `email`, and `name`.
2. **User Management:**
   - Check if a user with this `google_id` exists in the database.
   - If not, **auto-generate a Gamer ID** (e.g., `Gamer_` + random suffix).
   - Create a session or issue a JWT for subsequent API calls.
3. **Database Schema Update:**
   - Add `google_id` (string, indexed, unique) to the user table.
   - Ensure Gamer ID is editable but unique.

---

## Phase 3: Web & PWA Integration
1. **Google Identity Services (GIS):**
   - Include `<script src="https://accounts.google.com/gsi/client" async defer></script>`.
   - Implement "One Tap" sign-in for a seamless PWA experience.
2. **Session Sharing:**
   - Ensure the backend sets a secure, `HttpOnly` cookie for the session.
   - This allows the PWA (standalone) to share the session with the mobile browser.

---

## Phase 4: Flutter Mobile Integration
1. **Plugin Configuration:**
   - Add `google_sign_in` to `pubspec.yaml`.
   - Update `AndroidManifest.xml` and `Info.plist` with Client IDs.
2. **Sign-In Flow:**
   - Call `GoogleSignIn().signIn()`.
   - Send the `idToken` from the result to the Flask `/api/auth/google` endpoint.
   - Handle the backend response (store JWT or session).

---

## Phase 5: Security & GDPR Compliance
1. **Security:**
   - **Always** verify the ID token on the backend; never trust user IDs sent directly from the client.
   - Use CSRF protection for Web/PWA flows.
2. **GDPR:**
   - **Data Minimization:** Only store the Google User ID, Email, and Name.
   - **Consent:** Show a privacy notice before the user completes their first login.
   - **Deletion:** Provide a way for users to delete their account and associated highscores.

---

## Implementation Checklist
- [ ] Create Google Cloud Project and Credentials.
- [ ] Add `google-auth` to `requirements.txt`.
- [ ] Implement `id_token` verification in `app.py` or a dedicated auth service.
- [ ] Update `Highscore` or create a new `User` model to store `google_id`.
- [ ] Implement Gamer ID generation logic.
- [ ] Add Google Sign-In button to `index.html`.
- [ ] Integrate `google_sign_in` in Flutter app.
- [ ] Verify session sharing between PWA and Browser.
- [ ] Update Privacy Policy for GDPR compliance.
