# 🚀 Commercial Launch (Preview Mode) Readiness Checklist
**Project**: MathPuzzle ([SharpHuman.app](https://sharphuman.app))  
**Target Milestone**: Commercial Preview / Public Beta Launch  
**Infrastructure**: Hetzner K3s Cluster, Traefik Ingress, PostgreSQL 15, Flask + Flask-SocketIO  
**Date**: October 2026  

---

## 📌 Executive Decision Matrix

This checklist separates **P0 (Must-Haves for Public Preview Launch)** from **P1 (Fast Follows for Retention)** and **P2 (Commercial Scale & Monitization)**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       COMMERCIAL READINESS HORIZONS                         │
├──────────────────────────────┬──────────────────────────────┬───────────────┤
│ 🔴 P0: Preview Launch Blocker │ 🟡 P1: Fast-Follow Week 1-2   │ 🟢 P2: Scale  │
│ - Security headers & CSP     │ - Sentry exception tracking  │ - Redis room  │
│ - Kubernetes health probes   │ - Leaderboard TTL caching    │   storage     │
│ - Automated DB backups       │ - OpenGraph social cards     │ - HPA cluster │
│ - GA4 / Telemetry funnel     │ - Haptic feedback toggle     │   scaling     │
│ - In-app feedback mechanism  │ - Rate-limit cluster store   │ - Stripe/Pro  │
└──────────────────────────────┴──────────────────────────────┴───────────────┘
---

## 🧱 MANDATORY TEST PYRAMID STRATEGY & QUALITY GATES (Agent Contract)

> [!IMPORTANT]
> **Strict Precondition for All Agents and Engineers**:
> **NO checklist item may be marked as complete, committed, or deployed without adhering to this 3-tier Test Pyramid contract.**
> Every code or configuration change MUST be accompanied by corresponding automated tests at the appropriate layer(s).

### 📐 The 3-Tier Quality Gates:

```
                       ▲
                      / \     Tier 3: E2E Browser & Console Safety Net
                     /   \       Assert zero SEVERE console errors & zero CSP blocks in Chrome.
                    / E2E \      Verify full dual-client WebSockets & UI loops.
                   /───────\
                  /         \  Tier 2: Integration & Contract Layer
                 /Integration\    - Explicit HTTP header assertions (HSTS, CSP, X-Frame)
                /             \   - Healthcheck contract (200 OK, 503 DB failure)
               /───────────────\
              /                 \ Tier 1: Unit & Logic Layer
             /    Unit Tests     \   - In-memory cache mechanics (hit, miss, expiry)
            /─────────────────────\  - Deterministic algorithm & math validation
```

1. **Tier 1: Unit Test Gate (`tests/unit/`)**
   - **Scope**: In-memory caching logic, math generation, rating engines, pure helper functions.
   - **Requirement for Caching**: Any TTL cache (e.g., Leaderboard cache) MUST have tests asserting: (a) cache MISS on first call, (b) cache HIT on subsequent calls within TTL, (c) cache expiry/refresh after TTL.
   - **Standard**: 100% pass rate, 0 warnings.

2. **Tier 2: Integration Test Gate (`tests/integration/`)**
   - **Scope**: Flask routes, response headers, middleware, database transactions, error handlers.
   - **Requirement for Security Headers**: Every new security header (`Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`) MUST be explicitly asserted on HTTP responses (`/`, `/game`, `/leaderboard`).
   - **Requirement for Health Probes**: The `/health` endpoint MUST be tested for: (a) HTTP 200 with JSON payload `{"status": "healthy", "database": "connected"}` under normal DB connection, and (b) HTTP 503 under simulated DB disconnection.
   - **Standard**: 100% pass rate, 0 warnings.

3. **Tier 3: E2E Browser & Console Safety Net Gate (`tests/e2e/`)**
   - **Scope**: Headless Chrome automation across user journeys, WebSockets, KaTeX rendering, and client-side scripts.
   - **MANDATORY BROWSER CONSOLE INSPECTION**: All E2E test runs MUST inspect Chrome browser console logs (`driver.get_log('browser')`) and assert **ZERO SEVERE console errors and ZERO CSP violation blocks**. 
   - *Rationale*: A server returning HTTP 200 does NOT mean the frontend works. If CSP blocks KaTeX fonts, Google SSO iframe, or WebSockets, the page loads but the app is broken. Inspecting browser console logs guarantees zero silent frontend breakages.
   - **Standard**: 100% pass rate, 0 warnings.

### 📜 Mandatory Workflow for Agents:
1. **Step 1 (Test First / TDD)**: Write or update the unit, integration, or E2E test specifying the expected behavior before or alongside implementation.
2. **Step 2 (Implementation)**: Implement the change in application or infrastructure code.
3. **Step 3 (Pyramid Verification)**: Run `.venv/bin/pytest tests/unit tests/integration` and `.venv/bin/pytest tests/e2e`. Both must pass with **0 failures and 0 warnings**.
4. **Step 4 (Commit Proof)**: The commit message must cite the automated tests executed and verified.

---

## 1. 🛡️ Security

| Priority | Item | Current State | Decision / Implementation Action | Verification Criteria |
|---|---|---|---|---|
| **🔴 P0** | **HTTP Security Headers** | Missing (No HSTS, CSP, X-Frame-Options in Flask) | Add `@app.after_request` or Traefik middleware setting: `Strict-Transport-Security: max-age=31536000; includeSubDomains`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin`. | SecurityHeaders.com score **A+** |
| **🔴 P0** | **Content Security Policy (CSP)** | AdSense & KaTeX loaded without CSP policy | Define strict CSP whitelist: `default-src 'self'; script-src 'self' 'unsafe-inline' https://accounts.google.com https://pagead2.googlesyndication.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net data:; connect-src 'self' wss://sharphuman.app https://pagead2.googlesyndication.com;` | KaTeX, Google SSO, and AdSense load without console violations |
| **🔴 P0** | **Session Cookie Hardening** | `SESSION_COOKIE_SECURE=True` set only in production | Enforce `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_SAMESITE='Lax'`, `PERMANENT_SESSION_LIFETIME=7 days`. Verify cookie cannot be accessed via JavaScript `document.cookie`. | Inspection via Chrome DevTools Application > Cookies |
| **🔴 P0** | **CSRF & API Exemption Safety** | SeaSurf active; REST blueprint CSRF exempt | Ensure exempt API endpoints (`/api/auth/google`) validate cryptographic token headers (`credential` JWT token with Google servers) and reject untrusted payloads. | Integration tests pass with malformed tokens returning 401 |
| **🟡 P1** | **Vulnerability & Dependency Scanning** | Manual `pip install` | Add automated GitHub Actions step running `pip-audit` or Trivy on every PR to prevent CVE regressions. | Automated CI check fails on critical/high CVEs |
| **🟢 P2** | **Account Deletion / GDPR Self-Service** | Google SSO persists user email & profile without self-delete | Add `/profile/delete` route allowing users to purge their account, high scores, and learning profile data. | End-to-end data erasure verification |

---

## 2. 👥 Usability & Product Experience

| Priority | Item | Current State | Decision / Implementation Action | Verification Criteria |
|---|---|---|---|---|
| **🔴 P0** | **In-App User Feedback Widget** | No feedback collection mechanism | Preview users encounter bugs or UX friction without a way to report them. Embed a lightweight "💡 Give Feedback / Report Bug" floating button or modal linked to a Formspree/GitHub issue webhook. | Form submits directly to team inbox without page reload |
| **🔴 P0** | **Guest to Google SSO Transition** | Google SSO implemented | Ensure guest players who achieve high scores or AI progress do not lose their current streak when they click "Sign in with Google" (link active session progress to newly authenticated account). | Verified in E2E session handoff test |
| **🔴 P0** | **Social Shareability (OpenGraph)** | Basic meta tags | Add rich OpenGraph (`og:image`, `og:title`, `og:description`) and Twitter Card tags. For Startup Challenge, provide a dynamic 1-click share button: *"I reached Level 7 with a $1.2M valuation in Startup Math!"*. | Facebook/Twitter Card Debugger generates clean preview cards |
| **🟡 P1** | **PWA Install (A2HS) Prompt** | Service worker installed, standard browser install | Add a non-intrusive in-game "Install App" banner with `beforeinstallprompt` event listener for mobile Chrome/Safari. | Install banner prompts natively on Android & iOS Safari |
| **🟡 P1** | **Haptic & Audio Polish** | `SoundEngine` with Web Audio API active | Add subtle device vibration on mobile (`navigator.vibrate(50)` on correct, `navigator.vibrate([100, 50, 100])` on wrong) with an explicit Mute/Unmute toggle in the navbar. | Verified on physical iOS & Android devices |
| **🟢 P2** | **Ranked Matchmaking & Ghost Racing** | Manual room sharing only | Allow asynchronous racing against leaderboard records when no live human opponent is in lobby. | Asynchronous progress bar animated via WebSocket stream |

---

## 3. ⚖️ Scalability & Reliability

| Priority | Item | Current State | Decision / Implementation Action | Verification Criteria |
|---|---|---|---|---|
| **🔴 P0** | **PostgreSQL Automated Backups** | 2Gi PersistentVolumeClaim with no backup CronJob | If Hetzner node or PVC corrupts, all user accounts and learning profiles are lost. Deploy a Kubernetes `CronJob` (`k8s/base/backup-cronjob.yaml`) executing `pg_dump` daily and streaming compressed dumps to an offsite S3/Storage Box. | Automated daily `.sql.gz` dump created and tested with restore script |
| **🔴 P0** | **Database Connection Resiliency** | Default SQLAlchemy pool | Configure `pool_pre_ping=True`, `pool_recycle=1800`, and `pool_size=10` in `app.config['SQLALCHEMY_ENGINE_OPTIONS']` to prevent stale connection drops on Hetzner K3s. | No `psycopg2.OperationalError: server closed the connection unexpectedly` under idle recovery |
| **🟡 P1** | **Multiplayer Architecture (Single-Pod vs Redis)** | `replicas: 1`, in-memory Python dictionary (`room_storage.py`) | **Decision for Preview**: Keep `replicas: 1` with 100 threads for Preview Mode (supports up to ~1,500 concurrent players).  <br>**Decision for GA Scale**: Deploy Redis pod in K3s and migrate `room_storage.py` and Flask-SocketIO `message_queue="redis://redis:6379/0"`. | Architecture document signed off; single-pod capacity benchmarks recorded |
| **🟡 P1** | **Cluster-Wide Rate Limiting** | Flask-Limiter uses `memory://` storage | When the web pod restarts, rate limiting counts reset to zero. Point Flask-Limiter to Redis or SQLite storage once Redis is provisioned. | Limits persist across pod restarts |
| **🟢 P2** | **Horizontal Pod Autoscaling (HPA)** | Static 1 replica | Add Kubernetes metrics-server and define HPA (`minReplicas: 2`, `maxReplicas: 10`, CPU threshold 70%). | Verified with `kubectl autoscale` |

---

## 4. 🔭 Observability & Monitoring

| Priority | Item | Current State | Decision / Implementation Action | Verification Criteria |
|---|---|---|---|---|
| **🔴 P0** | **Kubernetes Health Probes** | Missing `livenessProbe` and `readinessProbe` in `app.yaml` | Add `@app.route('/health')` returning `{"status": "ok", "db": true}`. Add HTTP probes in `k8s/base/app.yaml`: initialDelay 10s, period 15s. Traefik will automatically stop routing traffic to unhealthy pods during restarts. | `kubectl describe pod mathpuzzle-web` shows clean probe events |
| **🔴 P0** | **Real-Time Error Tracking (Sentry)** | Standard logging to local file and stdout | Backend and frontend exceptions in production may go unnoticed. Integrate Sentry (`sentry-sdk[flask]`) with environment filtering (`production` only) and release tracking tied to Git SHA. | Test error sent from production triggers instant Slack/email alert |
| **🔴 P0** | **Product & Conversion Analytics (GA4)** | AdSense tag in place, no web telemetry | Add Google Analytics 4 (GA4) or privacy-friendly Plausible/PostHog script to measure: (1) Visitor acquisition, (2) Game start rate, (3) Game completion rate, (4) Sign-in conversion rate. | Live events visible in Analytics Realtime dashboard |
| **🟡 P1** | **Uptime Monitoring & Heartbeat** | No external uptime ping | Set up external uptime probe (BetterStack / UptimeRobot / Uptime Kuma) checking `https://sharphuman.app/health` every 60 seconds with push notifications. | Synthetic downtime test triggers notification within 2 minutes |
| **🟢 P2** | **Prometheus Metrics Exporter** | Standard logging | Add `prometheus-flask-exporter` with `/metrics` endpoint scraped by cluster Prometheus for latency p95/p99 graphs. | Grafana dashboard displays real-time RPS and latency |

---

## 5. ⚡ Performance & Caching

| Priority | Item | Current State | Decision / Implementation Action | Verification Criteria |
|---|---|---|---|---|
| **🔴 P0** | **Global Leaderboard TTL Cache** | Uncached database queries on every `/leaderboard` request | Wrap leaderboard retrieval in a 3-minute in-memory TTL cache (`cachetools.TTLCache`). Frequent visits or automated bots cannot cause PostgreSQL CPU spikes. | Database query count remains 1 per 3 minutes under high traffic |
| **🔴 P0** | **Static Asset Caching & Compression** | Default Flask static file serving | Configure Traefik gzip/brotli middleware or Flask-Compress. Set `Cache-Control: public, max-age=604800` (7 days) for images, CSS, and JS. | Response headers contain `content-encoding: gzip` and `cache-control` |
| **🟡 P1** | **Decimal Precision Standardization** | Floating point inconsistencies in choice generation | Audit question generators to enforce strict rounding: `round(val, 2)` or integer cents for currency. | Zero answers with `.30000000000000004` displayed |
| **🟢 P2** | **CDN / Edge Caching (Cloudflare)** | Direct Hetzner Traefik Ingress | Put Cloudflare free tier in front of `sharphuman.app` for DDoS mitigation, edge caching of static assets, and global DNS resolution. | TTFB < 100ms globally for cached assets |

---

## 📋 Launch Day Execution Runbook (Preview Mode)

### T-Minus 48 Hours:
1. [ ] Apply security headers middleware in [app.py](file:///Users/keshavbindal/IdeaProjects/AIHandsOn/app.py) (HSTS, CSP, X-Frame-Options).
2. [ ] Add `/health` endpoint and configure Kubernetes `livenessProbe` and `readinessProbe` in [k8s/base/app.yaml](file:///Users/keshavbindal/IdeaProjects/AIHandsOn/k8s/base/app.yaml).
3. [ ] Configure PostgreSQL backup CronJob to offsite storage.
4. [ ] Implement Sentry and GA4 measurement ID in production environment.
5. [ ] Implement 3-minute TTL caching on `/leaderboard`.

### T-Minus 2 Hours:
1. [ ] Deploy latest tagged Docker image to Hetzner K3s (`kustomize build k8s/overlays/prod | kubectl apply -f -`).
2. [ ] Verify SSL certificate validity via Let's Encrypt (`curl -Iv https://sharphuman.app`).
3. [ ] Verify Google Sign-In with real production Google credentials on live domain.
4. [ ] Run automated E2E smoke tests against live production domain.
5. [ ] Confirm external uptime monitor is green.

### T-Zero (Go Live):
1. [ ] Announce preview link to initial beta cohort.
2. [ ] Monitor Sentry dashboard for 0 uncaught exceptions.
3. [ ] Monitor Hetzner node CPU and memory utilization.
4. [ ] Collect initial qualitative feedback via the in-app feedback channel.
