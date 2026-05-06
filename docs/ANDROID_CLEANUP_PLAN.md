# Android App Removal Plan

**Date Created**: May 7, 2026  
**Status**: PENDING EXECUTION  
**Scope**: Remove all native Android app code while preserving API, tests, and PWA compatibility

---

## 📋 Executive Summary

This document outlines the complete removal of the Flutter/Android application from the MathPuzzle project. The focus is on web (PWA) and API-only deployment going forward.

**What's being removed**: ~2.6M of Flutter/Android code  
**What's staying**: Python Flask API, tests, and infrastructure  
**Impact**: API remains fully functional, PWA becomes the primary client

---

## 🗂️ Complete Inventory of Android-Specific Files

### 1. Core Android Directory (PRIMARY REMOVAL)
```
mathpuzzle_app/android/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── kotlin/com/example/mathpuzzle_app_v2/MainActivity.kt
│   │   │   ├── java/io/flutter/plugins/GeneratedPluginRegistrant.java
│   │   │   ├── res/
│   │   │   │   ├── drawable/ (launch_background.xml)
│   │   │   │   ├── drawable-v21/ (launch_background.xml)
│   │   │   │   ├── values/ (styles.xml, colors.xml)
│   │   │   │   ├── values-night/ (styles.xml)
│   │   │   │   ├── mipmap-*/ (launcher icons)
│   │   │   │   └── raw/ (any resources)
│   │   │   └── AndroidManifest.xml
│   │   ├── debug/
│   │   │   └── AndroidManifest.xml
│   │   └── profile/
│   │       └── AndroidManifest.xml
│   ├── build.gradle.kts
│   └── .gitignore
├── gradle/
│   └── wrapper/gradle-wrapper.properties
├── .gradle/ (build cache)
├── build/ (build artifacts)
├── settings.gradle.kts
├── build.gradle.kts (root)
├── gradle.properties
├── local.properties
├── gradlew
├── gradlew.bat
└── .gitignore
```

**Total Size**: 2.6M

### 2. Flutter Configuration Files
```
mathpuzzle_app/
├── pubspec.yaml           # Flutter project config
├── pubspec.lock           # Dependency lock file
├── analysis_options.yaml  # Dart linting config
├── .metadata              # Flutter metadata
├── mathpuzzle_app_v2.iml  # IntelliJ IDEA project file
└── .flutter-plugins-dependencies
```

### 3. Flutter App Source Code
```
mathpuzzle_app/lib/
├── main.dart              # Entry point
├── screens/
│   ├── home_screen.dart
│   ├── game_screen.dart
│   ├── lobby_screen.dart
│   └── *.dart
├── widgets/
│   ├── leaderboard_widget.dart
│   └── *.dart
├── providers/
│   ├── game_provider.dart
│   ├── multiplayer_provider.dart
│   └── *.dart
└── *.dart

mathpuzzle_app/test/
├── widget/
│   ├── home_screen_test.dart
│   ├── game_screen_test.dart
│   ├── lobby_screen_test.dart
│   └── *.dart
├── unit/
│   ├── game_provider_test.dart
│   ├── multiplayer_provider_test.dart
│   └── *.dart
```

### 4. Build Artifacts (Auto-generated, safe to delete)
```
mathpuzzle_app/
├── .dart_tool/            # Dart tooling cache
├── build/                 # Flutter build output
└── .android/ (if exists)  # Gradle cache
```

### 5. Documentation to Remove/Update
```
docs/
├── WEB_AND_ANDROID_PLAN.md          # REMOVE ENTIRELY
└── BACKLOG.md                        # UPDATE: Remove Android tasks

Root:
├── README.md              # UPDATE: Remove Android references
└── mathpuzzle_app/README.md         # REMOVE ENTIRELY (or keep if PWA docs)
```

### 6. Git Branches to Delete
```
Local branches:
- android-multiplayer-support
- feature/android-ux-optimization

Remote branches:
- origin/android-application-basic-setup
- origin/android-hardened-pilot
- origin/feature/android-ux-optimization
```

---

## ✅ Files to KEEP (Do Not Delete)

### API Code (Untouched)
```
src/                        # Python API code
app.py                      # Flask entry point
mathpuzzle_app/ (backend)   # Backend app logic (if exists)
tests/                      # API tests
```

### Infrastructure
```
k8s/                        # Kubernetes manifests
scripts/                    # Deployment scripts
docker-compose.yml          # Docker compose
Dockerfile                  # API container
```

### Documentation
```
docs/
├── HETZNER_K3S_DEPLOYMENT_PLAN.md
├── PHASE_1_COMPLETION.md
├── PHASE_1_QUICKSTART.md
└── (other non-Android docs)
```

### PWA Assets (if any)
```
static/                     # Static assets for web
templates/                  # Flask templates
```

---

## 🔄 Step-by-Step Cleanup Process

### Phase 1: Preparation
```bash
# 1. Create backup branch (SAFETY FIRST)
git checkout -b cleanup/android-removal
git push origin cleanup/android-removal

# 2. Verify current state
ls -lh mathpuzzle_app/
find . -name "*.gradle*" -o -name "AndroidManifest.xml" | wc -l

# 3. List git branches related to Android
git branch -a | grep -i android
```

### Phase 2: Delete Android Code
```bash
# 1. Remove Flutter/Android directory
rm -rf mathpuzzle_app/

# 2. Remove Android documentation
rm docs/WEB_AND_ANDROID_PLAN.md

# 3. Clean up git
git add -A
git commit -m "Remove: Flutter/Android application

- Remove entire mathpuzzle_app/ directory (2.6M)
- Remove Android deployment documentation
- Keep Flask API, tests, and infrastructure intact
- Focus on web (PWA) and API-only architecture

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Phase 3: Update Documentation
```bash
# 1. Update README.md - Remove Android references
# Look for sections mentioning:
#   - Android Studio
#   - Flutter setup
#   - APK builds
#   - Mobile app

# 2. Update docs/BACKLOG.md - Remove Android tasks
# Remove items tagged with:
#   - [Android]
#   - [Flutter]
#   - [Mobile]

# 3. Create/update main README to focus on:
#   - Web/PWA
#   - API
#   - K3s Deployment
```

### Phase 4: Delete Git Branches
```bash
# Delete local branches
git branch -d android-multiplayer-support
git branch -d feature/android-ux-optimization

# Delete remote branches
git push origin --delete android-application-basic-setup
git push origin --delete android-hardened-pilot
git push origin --delete feature/android-ux-optimization
```

### Phase 5: Final Validation
```bash
# 1. Verify no Android references remain
grep -r "android\|Android\|gradle\|AndroidManifest" \
  --exclude-dir=.git \
  --exclude-dir=.idea \
  --exclude="*.iml" \
  . 2>/dev/null | grep -v "ANDROID_CLEANUP_PLAN.md"

# 2. Check project structure
tree -L 2 -I '__pycache__|.git|.venv|node_modules'

# 3. Verify API still works
make test

# 4. Check Docker build
docker build -t mathpuzzle:cleanup-test .
```

### Phase 6: Merge and Deploy
```bash
# 1. Push changes to cleanup branch
git push origin cleanup/android-removal

# 2. Create PR, get review
# (Link to this plan in PR description)

# 3. Merge to main
git checkout main
git merge cleanup/android-removal
git push origin main

# 4. Tag release (optional)
git tag -a v2.0.0-web-only -m "Android app removed, web-only deployment"
git push origin v2.0.0-web-only
```

---

## 📊 Impact Analysis

### Size Reduction
```
Before: ~2.6M (Android code)
After:  ~0M (removed)
Savings: 2.6M
```

### What Continues to Work
- ✅ Flask API (100% functional)
- ✅ REST endpoints
- ✅ WebSocket connections
- ✅ Database operations
- ✅ Authentication
- ✅ K3s deployment

### What Changes
- ❌ No native Android app
- ❌ No APK builds
- ⚠️ Mobile access via PWA only (fallback to web)
- ⚠️ No offline-first native features

### New Architecture
```
Client Layer:
  - Progressive Web App (PWA) - replaces mobile app
  - Responsive design for mobile browsers
  - Install-to-homescreen capability

API Layer:
  - Flask REST API (unchanged)
  - WebSocket for real-time multiplayer
  - PostgreSQL database

Infrastructure:
  - K3s on Hetzner VPS
  - Traefik ingress
  - Cert-Manager for SSL
```

---

## 🚨 Safety Checklist

Before executing cleanup:
- [ ] Backup current state (`git branch cleanup/android-removal`)
- [ ] Verify all tests pass (`make test`)
- [ ] Confirm no uncommitted changes (`git status`)
- [ ] Review this plan with team
- [ ] Document any custom Android code not in mathpuzzle_app/

During cleanup:
- [ ] Delete one section at a time (commit after each phase)
- [ ] Verify API tests still pass after each deletion
- [ ] Check for broken imports/references

After cleanup:
- [ ] Run full test suite
- [ ] Build Docker image successfully
- [ ] Deploy to test environment
- [ ] Verify API endpoints work
- [ ] Test PWA on mobile device

---

## 📝 Related Documentation

- **HETZNER_K3S_DEPLOYMENT_PLAN.md** - Web deployment on K3s
- **PHASE_1_COMPLETION.md** - Historical context
- **BACKLOG.md** - Future tasks (update to remove Android items)

---

## 🔗 Rollback Plan

If issues occur:
```bash
# Revert to before cleanup
git checkout cleanup/android-removal^  # Parent commit

# Or revert entire cleanup commit
git revert <cleanup-commit-hash>

# Or revert branch
git reset --hard origin/main
```

---

**Status**: READY FOR EXECUTION  
**Last Updated**: May 7, 2026  
**Approval**: Pending
