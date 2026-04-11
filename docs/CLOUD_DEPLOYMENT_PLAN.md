# Cloud Deployment Plan - MathPuzzle

## Phase 1: Application Readiness
- [ ] **Cloud-Aware SSL**: Update `app.py` to only use local `ssl_context` if `FLASK_ENV` is not `production`.
- [ ] **Health Checks**: Ensure the `/` route returns 200 OK for cloud platform keep-alive pings.
- [ ] **Dependency Audit**: Verify `psycopg2-binary` and `gunicorn` are in `requirements.txt`.

## Phase 2: Docker Optimization
- [ ] **Production Compose**: Create `docker-compose.prod.yml` without development mounts.
- [ ] **Port Standardization**: Standardize container port to 8080 (common for cloud PaaS).

## Phase 3: Infrastructure Setup (Example: Railway/Render)
1. **Database**: Provision a Managed PostgreSQL instance.
2. **Environment Variables**:
   - `FLASK_ENV=production`
   - `DATABASE_URL` (Provided by the cloud DB)
   - `SECRET_KEY` (Generate a long random string)
   - `ALLOWED_ORIGINS` (Set to your custom domain)
3. **Deployment**: Connect GitHub repository to the PaaS provider.

## Phase 4: Testing & Monitoring
- [ ] **Pyramid Check**: Ensure `python run_tests.py` passes in the CI environment.
- [ ] **WebSocket Ping**: Verify that the cloud proxy allows long-lived WebSocket connections (disable "H3" or "HTTP/3" if issues arise with SocketIO).
- [ ] **Persistence Test**: Add a highscore, trigger a manual redeploy, and verify the score persists.
