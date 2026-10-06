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

## Phase 5: Production Deployment on Ubuntu Server

Follow these steps to deploy and activate Google SSO on your Ubuntu production server (`https://sharphuman.app`):

### 1. Google Cloud Console Configuration
1. Go to [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials).
2. Select your project and create (or edit) your **OAuth 2.0 Client ID** (Application type: **Web application**).
3. Under **Authorized JavaScript origins**, add:
   - `https://sharphuman.app`
   - `https://www.sharphuman.app`
   *(Optional for staging/testing: `https://localhost:5005`)*
4. Under **Authorized redirect URIs**:
   - Google Identity Services (One Tap & standard button) uses credential post/callback, so redirect URI is not required, but you can set:
     - `https://sharphuman.app`
5. Copy your **Client ID** (e.g. `1234567890-abcdefg123456.apps.googleusercontent.com`).

---

### 2. Configure Environment on Ubuntu Server

Depending on how MathPuzzle is hosted on your Ubuntu server, apply the Client ID using one of the following methods:

#### Method A: Docker Compose Deployment (Recommended for VPS)
1. SSH into your Ubuntu server:
   ```bash
   ssh ubuntu@your-server-ip
   cd /path/to/mathpuzzle
   ```
2. Add `GOOGLE_CLIENT_ID` to your production `.env` file:
   ```bash
   echo 'GOOGLE_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com"' >> .env
   ```
3. Ensure `docker-compose.prod.yml` passes the variable (already configured):
   ```yaml
   environment:
     - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
   ```
4. Rebuild and restart the container:
   ```bash
   docker compose -f docker-compose.prod.yml down
   docker compose -f docker-compose.prod.yml up -d --build
   ```

#### Method B: K3s / Kubernetes Deployment
1. SSH into your Ubuntu server with `kubectl` access.
2. Edit or recreate `k8s/secrets.yaml`:
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: mathpuzzle-secrets
     namespace: mathpuzzle
   type: Opaque
   stringData:
     SECRET_KEY: "your-production-secret-key"
     DATABASE_URL: "postgresql://user:pass@postgres:5432/mathpuzzle"
     GOOGLE_CLIENT_ID: "YOUR_CLIENT_ID.apps.googleusercontent.com"
   ```
3. Apply the updated secret and rollout restart:
   ```bash
   kubectl apply -f k8s/secrets.yaml
   kubectl rollout restart deployment/mathpuzzle-web -n mathpuzzle
   ```

#### Method C: Native Systemd Service (Gunicorn without Docker)
1. If running as a systemd service (e.g. `/etc/systemd/system/mathpuzzle.service`):
   ```bash
   sudo nano /etc/systemd/system/mathpuzzle.service
   ```
2. Add to the `[Service]` section:
   ```ini
   Environment="GOOGLE_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com"
   ```
3. Reload systemd and restart service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart mathpuzzle
   ```

---

### 3. Verification on Production
1. Visit `https://sharphuman.app/` in your browser.
2. Confirm the **"Sign in to save your career stats"** Google One Tap prompt and standard Google Sign-In button render.
3. Sign in with your Google account.
4. Verify that:
   - The header displays `Logged in as: Your Name` with a `Logout` button.
   - The `GamerId` input is locked/readonly with your name.
   - Finished games save high scores associated with your user account in the database.

---

## Implementation Checklist
- [x] Integrate `google-auth` in `requirements.txt`.
- [x] Implement backend token verification and user linking in `GoogleAuthResource` (`POST /api/auth/google`).
- [x] Update database models (`User` table with `google_id`, and `Highscore.user_id` foreign key).
- [x] Integrate Google Identity Services (GIS) One Tap and standard button in `src/templates/index.html`.
- [x] Connect `GOOGLE_CLIENT_ID` in `app.py`, `docker-compose.prod.yml`, and `k8s/base/app.yaml`.
- [x] Run full automated test suite (Unit, Integration, API, E2E).
- [ ] Add `https://sharphuman.app` to Google Cloud Console Authorized Origins.
- [ ] Set `GOOGLE_CLIENT_ID` environment variable on Ubuntu server.
