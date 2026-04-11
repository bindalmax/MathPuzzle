# MathPuzzle: Web & Android Cross-Platform Plan

## Executive Summary

This plan outlines how to deploy MathPuzzle on both **Web (Flask)** and **Android** platforms with a shared backend API, allowing seamless gameplay across devices.

### Current Status
- ✅ Web version: Fully functional (Flask + Flask-SocketIO)
- ✅ Backend API: Ready for mobile client integration
- ⏳ Android version: To be built

### Architecture Overview
```
┌──────────────────────────────────────────────────────────────┐
│                    Shared PostgreSQL Database                │
│                    (Highscores, User Sessions)               │
└──────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    API (REST + WebSocket)
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │  Web App │  │ Android  │  │  iOS     │
         │ (Flask)  │  │ (Flutter)│  │(Flutter) │
         │ HTML/CSS │  │  Native  │  │ Native   │
         │   JS     │  │          │  │          │
         └──────────┘  └──────────┘  └──────────┘
```

---

## Part 1: Current Web Architecture

### Existing Tech Stack

| Layer | Technology | Status |
|-------|-----------|--------|
| **Backend** | Flask 3.0.0 | ✅ Production-ready |
| **Real-time** | Flask-SocketIO 5.3.6 | ✅ Multiplayer support |
| **Database** | PostgreSQL 15 | ✅ Persistent storage |
| **ORM** | SQLAlchemy 2.0.23 | ✅ Configured |
| **Frontend** | HTML/CSS/JavaScript | ✅ Responsive templates |
| **Deployment** | Docker + Gunicorn | ✅ Containerized |

### Existing API Endpoints

**Game Endpoints:**
- `GET /` - Home/Index page
- `POST /` - Join/Create game
- `POST /play` - Start game session
- `POST /answer` - Submit answer
- `GET /leaderboard` - View highscores

**Multiplayer Endpoints:**
- `POST /multiplayer-lobby` - Create multiplayer room
- `GET /multiplayer-lobby/<room_id>` - Join room
- Socket.IO events:
  - `join_room` - Player joins multiplayer room
  - `game_started` - Game begins
  - `answer_submitted` - Real-time score sync
  - `game_ended` - Results

### Database Schema

**Highscore Model:**
```python
class Highscore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    difficulty = db.Column(db.String(80), nullable=False)
    time_taken = db.Column(db.Float, nullable=True)
    questions_attempted = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## Part 2: Android Development Options

### Option A: Flutter (Recommended for This Project)

**Why Flutter?** Cross-platform (Android + iOS), single codebase, fast development, great WebSocket support.

#### Setup

```bash
# Install Flutter SDK
# macOS:
brew install flutter

# Windows:
# Download from https://flutter.dev/docs/get-started/install/windows

# Verify installation
flutter doctor

# Create new Flutter project
flutter create mathpuzzle_app
cd mathpuzzle_app

# Add dependencies to pubspec.yaml
flutter pub add http socket_io_client provider intl shared_preferences
```

#### pubspec.yaml Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  socket_io_client: ^2.0.0
  provider: ^6.0.0
  intl: ^0.18.0
  shared_preferences: ^2.0.0
  cupertino_icons: ^1.0.2
  connectivity_plus: ^5.0.0
```

#### Project Structure

```
mathpuzzle_app/
├── lib/
│   ├── main.dart
│   ├── models/
│   │   ├── game_model.dart
│   │   ├── highscore_model.dart
│   │   └── player_model.dart
│   ├── screens/
│   │   ├── home_screen.dart
│   │   ├── game_screen.dart
│   │   ├── leaderboard_screen.dart
│   │   ├── multiplayer_lobby_screen.dart
│   │   └── results_screen.dart
│   ├── services/
│   │   ├── api_service.dart
│   │   ├── websocket_service.dart
│   │   └── local_storage_service.dart
│   ├── widgets/
│   │   ├── question_card.dart
│   │   ├── answer_button.dart
│   │   └── score_display.dart
│   └── providers/
│       ├── game_provider.dart
│       ├── leaderboard_provider.dart
│       └── multiplayer_provider.dart
├── pubspec.yaml
├── pubspec.lock
└── android/
    ├── app/
    │   ├── build.gradle
    │   └── src/
    │       ├── main/
    │       │   ├── AndroidManifest.xml
    │       │   └── res/
    │       └── debug/
    └── build.gradle
```

#### API Service Example

```dart
// lib/services/api_service.dart

import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'https://your-domain.com'; // or http://IP:5000
  
  // Get a new question
  Future<Map<String, dynamic>> getQuestion({
    required String category,
    required String difficulty,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/question'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'category': category,
          'difficulty': difficulty,
        }),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to fetch question');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }
  
  // Submit answer
  Future<Map<String, dynamic>> submitAnswer({
    required String sessionId,
    required String answer,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/answer'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'session_id': sessionId,
        'answer': answer,
      }),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to submit answer');
    }
  }
  
  // Get leaderboard
  Future<List<Map<String, dynamic>>> getLeaderboard({
    String? category,
    String? difficulty,
  }) async {
    final queryParams = <String, String>{};
    if (category != null) queryParams['category'] = category;
    if (difficulty != null) queryParams['difficulty'] = difficulty;
    
    final uri = Uri.parse('$baseUrl/api/leaderboard').replace(
      queryParameters: queryParams,
    );
    
    final response = await http.get(uri);
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as List;
      return data.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Failed to fetch leaderboard');
    }
  }
}
```

#### WebSocket Service

```dart
// lib/services/websocket_service.dart

import 'package:socket_io_client/socket_io_client.dart' as IO;

class WebSocketService {
  static const String baseUrl = 'https://your-domain.com';
  late IO.Socket socket;
  
  void connect(String playerId) {
    socket = IO.io(
      baseUrl,
      IO.SocketIoClientOption(
        'transports': ['websocket'],
        'autoConnect': true,
      ),
    );
    
    socket.onConnect((_) {
      print('WebSocket connected');
      socket.emit('join_room', {'player_id': playerId});
    });
    
    socket.on('game_started', (data) {
      print('Game started: $data');
    });
    
    socket.on('answer_submitted', (data) {
      print('Answer submitted: $data');
    });
    
    socket.onDisconnect((_) {
      print('WebSocket disconnected');
    });
  }
  
  void disconnect() {
    socket.disconnect();
  }
}
```

#### Building & Deployment

```bash
# Build APK (Android release)
flutter build apk --release

# Build App Bundle (Google Play)
flutter build appbundle --release

# Run on emulator (development)
flutter run

# Run on physical device
flutter run -d <device-id>
```

---

### Option B: Native Android Development (Java/Kotlin)

**Best if:** You want maximum performance, deep OS integration, or large existing Android team.

**Drawback:** Separate codebase from web version.

#### Setup

```bash
# Install Android Studio
# https://developer.android.com/studio

# Create New Project (Kotlin)
# File > New > New Project > Phone and Tablet
# Select "Empty Activity" template
# Language: Kotlin
# Minimum SDK: 24 (Android 7.0)
```

#### Dependencies (build.gradle)

```gradle
dependencies {
    // Networking
    implementation 'com.square.okhttp3:okhttp:4.11.0'
    implementation 'com.google.code.gson:gson:2.10.1'
    
    // WebSocket
    implementation 'io.socket:socket.io-client-java:2.1.0'
    
    // Local Storage
    implementation 'androidx.datastore:datastore-preferences:1.0.0'
    
    // UI
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.10.0'
    
    // Testing
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}
```

---

### Option C: React Native (Alternative)

**Pros:** Code sharing between iOS/Android, JavaScript-based.  
**Cons:** Larger bundle size, performance overhead.

**Choose this if:** Team has React/JavaScript expertise.

---

## Part 3: Backend API Refactoring for Mobile

### Current State: Web-focused
- API endpoints mixed with web UI rendering
- Some endpoints return HTML/forms
- WebSocket tightly coupled to web templates

### Required Changes: Mobile-first API

#### 1. Create REST API Layer

```python
# app/api/__init__.py

from flask import Blueprint
from flask_restful import Api, Resource

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

class QuestionResource(Resource):
    def post(self):
        """Get a new question"""
        data = request.get_json()
        category = data.get('category')
        difficulty = data.get('difficulty')
        
        # Generate question
        question = QuestionFactory.get_question(category, difficulty)
        
        return {
            'status': 'success',
            'question': question.to_dict(),
            'question_id': str(uuid.uuid4()),
        }, 200

class AnswerResource(Resource):
    def post(self):
        """Submit answer and get feedback"""
        data = request.get_json()
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        # Validate answer
        is_correct = verify_answer(question_id, answer)
        
        return {
            'status': 'success',
            'is_correct': is_correct,
            'score': 10 if is_correct else 0,
        }, 200

class LeaderboardResource(Resource):
    def get(self):
        """Get leaderboard"""
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        limit = request.args.get('limit', 50)
        
        highscores = Highscore.query.filter_by(
            category=category,
            difficulty=difficulty
        ).order_by(Highscore.score.desc()).limit(limit).all()
        
        return {
            'status': 'success',
            'leaderboard': [h.to_dict() for h in highscores],
        }, 200

api.add_resource(QuestionResource, '/question')
api.add_resource(AnswerResource, '/answer')
api.add_resource(LeaderboardResource, '/leaderboard')
```

#### 2. Update app.py to Register API

```python
# In app.py

from app.api import api_bp

app.register_blueprint(api_bp)
```

#### 3. API Endpoints Documentation

```
GET  /api/categories
     Returns: { categories: ['arithmetic', 'percentages', ...] }

GET  /api/difficulties
     Returns: { difficulties: ['easy', 'medium', 'hard'] }

POST /api/question
     Body: { category: 'arithmetic', difficulty: 'easy' }
     Returns: { question: {...}, question_id: '...' }

POST /api/answer
     Body: { question_id: '...', answer: '42' }
     Returns: { is_correct: true/false, score: 10 }

POST /api/score
     Body: { player_name: 'John', score: 100, category: '...', difficulty: '...' }
     Returns: { status: 'success', rank: 5 }

GET  /api/leaderboard?category=arithmetic&difficulty=easy&limit=50
     Returns: { leaderboard: [{name, score, rank, ...}, ...] }

POST /api/multiplayer/create
     Body: { player_name: 'John' }
     Returns: { room_id: '...', status: 'waiting' }

GET  /api/multiplayer/join/<room_id>?player_name=Jane
     Returns: { room_id: '...', players: [...], status: 'ready' }
```

#### 4. Error Handling (Consistent Format)

```python
# app/errors.py

def api_error(message, status_code=400):
    return {
        'status': 'error',
        'message': message,
        'code': status_code,
    }, status_code
```

---

## Part 4: Deployment Architecture

### Option A: Single Backend for Both Web & Android

```
┌─────────────────────────────────────────┐
│        Backend Server (VPS)             │
│  - Flask API (REST + WebSocket)         │
│  - PostgreSQL Database                  │
│  - Gunicorn + Nginx (Reverse Proxy)    │
│  - SSL/TLS (Let's Encrypt)             │
└──────────┬──────────────────────────────┘
           │
     ┌─────┴──────┐
     │            │
     ▼            ▼
┌─────────┐  ┌──────────┐
│ Web App │  │ Android  │
│Browser  │  │App       │
└─────────┘  └──────────┘
```

**Advantages:**
- Single source of truth for game logic
- Shared database (highscores, players)
- Easy to maintain
- Lower infrastructure cost

**Deployment Steps:**
1. Deploy backend on VPS (as per VPS_DEPLOYMENT_PLAN.md)
2. Build Android app with API pointing to backend
3. Build web app using existing Flask setup
4. Distribute Android APK via Google Play or direct download

### Option B: Separate APIs (Advanced)

For large-scale deployments with different requirements:

```
┌────────────────────────────────────────────┐
│        Backend Server 1 (VPS - Web)        │
│  - Flask (HTML/CSS rendering)              │
│  - PostgreSQL Replica                      │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│      Backend Server 2 (VPS - Mobile)       │
│  - REST API (JSON only)                    │
│  - PostgreSQL Replica                      │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│      Shared Database (Cloud: AWS RDS)      │
│  - PostgreSQL Master                       │
└────────────────────────────────────────────┘
```

---

## Part 5: Development Workflow

### Setup Local Development

```bash
# Clone repository
git clone <repo-url>
cd AIHandsOn

# Setup Python backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup Flutter app (if using Flutter)
cd ../mathpuzzle_app
flutter pub get

# Run backend
cd ../AIHandsOn
python app.py

# Run Flutter app (in separate terminal)
cd ../mathpuzzle_app
flutter run
```

### Development Environment (.env)

```bash
# Backend (.env)
FLASK_ENV=development
SECRET_KEY=dev-key-for-testing
DATABASE_URL=postgresql://user:password@localhost:5432/mathpuzzle_dev
ALLOWED_ORIGINS=localhost:3000,localhost:8080,127.0.0.1:5000

# Android/iOS (.env in Flutter app)
API_BASE_URL=http://192.168.1.100:5000  # Your machine IP on local network
WEBSOCKET_URL=http://192.168.1.100:5000  # For hot reload testing
```

### Testing Both Platforms

```bash
# Test web on localhost
open http://localhost:5000

# Test Android app
flutter run -d emulator-id

# Test on physical Android device
# 1. Connect device via USB
# 2. adb devices (verify connection)
# 3. flutter run

# Test WebSocket (from Android)
# Update API_BASE_URL to your machine's local IP:
API_BASE_URL=http://192.168.x.x:5000
```

---

## Part 6: Implementation Roadmap

### Phase 1: API Refactoring (Week 1-2)

- [ ] Extract REST endpoints from existing Flask routes
- [ ] Create `/api` blueprint with REST resources
- [ ] Update error handling to return JSON
- [ ] Document API with examples
- [ ] Create Postman collection for testing

**Tasks:**
```
1. Create api/__init__.py with Flask-RESTful
2. Create api/resources.py for all endpoints
3. Update app.py to register API blueprint
4. Test all endpoints with curl/Postman
5. Create API documentation
```

### Phase 2: Flutter App Development (Week 3-6)

- [ ] Setup Flutter project structure
- [ ] Create models for Question, Player, Highscore
- [ ] Implement API service layer
- [ ] Build screens (Home, Game, Leaderboard, Multiplayer)
- [ ] Implement local storage (player preferences)
- [ ] Add WebSocket support for multiplayer
- [ ] Build and test APK

**Tasks:**
```
1. flutter create mathpuzzle_app
2. Design app screens (Figma)
3. Implement models (question, player, score)
4. Create API service with error handling
5. Build UI screens
6. Integrate WebSocket for multiplayer
7. Local storage for offline mode
8. Testing & debugging
9. Build APK for distribution
```

### Phase 3: Backend Enhancements (Week 4-6, parallel with Phase 2)

- [ ] Add user authentication (optional)
- [ ] Session management for mobile
- [ ] Rate limiting for API
- [ ] Logging & monitoring
- [ ] Performance optimization

**Tasks:**
```
1. Add rate limiting middleware
2. Improve error messages
3. Add request validation
4. Performance testing
5. Add monitoring/alerting
```

### Phase 4: Testing & QA (Week 7)

- [ ] Unit tests (Flask backend)
- [ ] Integration tests (API)
- [ ] UI tests (Flutter)
- [ ] End-to-end tests (Web + Android)
- [ ] Performance testing
- [ ] Security testing

### Phase 5: Deployment (Week 8)

- [ ] Deploy backend on VPS (Docker)
- [ ] Publish Android app on Google Play
- [ ] Deploy web version
- [ ] Setup monitoring & backups
- [ ] Documentation & user guides

---

## Part 7: File Structure for Multi-Platform

### Updated Project Structure

```
AIHandsOn/
├── backend/
│   ├── app.py                    # Main Flask app
│   ├── database.py              # SQLAlchemy models
│   ├── highscore_manager.py
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py      # API blueprint
│   │   │   ├── resources.py     # REST resources
│   │   │   └── errors.py        # Error handling
│   │   ├── models/
│   │   │   ├── highscore.py
│   │   │   ├── player.py
│   │   │   └── game.py
│   │   ├── services/
│   │   │   ├── question_service.py
│   │   │   ├── scoring_service.py
│   │   │   └── multiplayer_service.py
│   │   └── utils/
│   │       ├── validators.py
│   │       └── constants.py
│   ├── questions/               # Question generation
│   ├── templates/               # Web UI (HTML/CSS/JS)
│   ├── static/                  # Web assets
│   ├── tests/                   # Backend tests
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
│
├── mathpuzzle_app/              # Flutter Android app
│   ├── lib/
│   │   ├── main.dart
│   │   ├── models/
│   │   ├── screens/
│   │   ├── services/
│   │   │   ├── api_service.dart
│   │   │   ├── websocket_service.dart
│   │   │   └── local_storage_service.dart
│   │   ├── providers/
│   │   ├── widgets/
│   │   └── utils/
│   ├── android/                 # Android native code
│   ├── pubspec.yaml
│   ├── pubspec.lock
│   ├── test/
│   ├── README.md
│   └── .env                     # API configuration
│
├── docs/
│   ├── VPS_DEPLOYMENT_PLAN.md
│   ├── WEB_AND_ANDROID_PLAN.md  # This file
│   ├── API_DOCUMENTATION.md     # New
│   ├── FLUTTER_SETUP_GUIDE.md   # New
│   └── ARCHITECTURE.md          # New
│
└── README.md
```

---

## Part 8: API Documentation Template

Create `docs/API_DOCUMENTATION.md`:

```markdown
# MathPuzzle API Documentation

## Base URL
- **Development:** `http://localhost:5000`
- **Production:** `https://your-domain.com`

## Authentication
Currently no authentication. Will add user sessions if needed.

## Response Format

All responses are JSON:

```json
{
  "status": "success|error",
  "data": {...},
  "message": "Error message if status=error"
}
```

## Endpoints

### Questions
- `POST /api/question` - Get new question
- `POST /api/answer` - Submit answer

### Leaderboard
- `GET /api/leaderboard` - Get high scores
- `POST /api/score` - Save score

### Multiplayer
- `POST /api/multiplayer/create` - Create room
- `GET /api/multiplayer/join/<room_id>` - Join room
```

---

## Part 9: Android Build & Distribution

### Building Release APK

```bash
# Navigate to Flutter project
cd mathpuzzle_app

# Build APK (release version)
flutter build apk --release

# Output location:
# build/app/outputs/flutter-apk/app-release.apk

# File size: ~50-100 MB typically
```

### Google Play Store Distribution

1. **Create Google Play Developer Account** (€25 one-time fee)
2. **Create App Bundle:**
   ```bash
   flutter build appbundle --release
   # Output: build/app/outputs/bundle/release/app-release.aab
   ```
3. **Sign APK/Bundle** (Keystore generation)
4. **Upload to Google Play Console**
5. **Set up store listing, pricing, screenshots**
6. **Submit for review** (24-48 hours)

### Direct Distribution

```bash
# Share APK directly
# https://your-domain.com/downloads/mathpuzzle.apk

# Users can install with:
# adb install mathpuzzle.apk
# Or download from browser and tap to install
```

---

## Part 10: Cross-Platform Testing Strategy

### Test Matrix

| Platform | Device | Browser/OS | Test Type | Status |
|----------|--------|-----------|-----------|--------|
| Web | Desktop | Chrome | Manual + Automated | ✅ |
| Web | Mobile | Safari/Chrome | Manual | ✅ |
| Android | Emulator | Android 11+ | Manual + Automated | ⏳ |
| Android | Physical | Android 7+ | Manual | ⏳ |
| iOS | Simulator | iOS 13+ | Manual | 🔄 Future |
| iOS | Physical | iOS 13+ | Manual | 🔄 Future |

### Test Checklist

#### Web (Browser)
- [ ] Single player game flow
- [ ] Multiplayer game flow
- [ ] Leaderboard display
- [ ] Score persistence
- [ ] WebSocket connection

#### Android App
- [ ] API connectivity (HTTP requests)
- [ ] Question rendering
- [ ] Answer submission
- [ ] Score calculation
- [ ] Leaderboard loading
- [ ] Multiplayer via WebSocket
- [ ] Offline mode (if implemented)
- [ ] Crash handling
- [ ] Battery/data usage
- [ ] Network disconnection handling

---

## Part 11: Troubleshooting Guide

### Common Issues

#### Flutter App Can't Connect to Backend

```bash
# Problem: API_BASE_URL not reachable
# Solution: 
# 1. Check VPS/backend is running
# 2. Check firewall allows port 5000
# 3. Update API_BASE_URL in .env
# 4. Test with curl first

curl http://your-vps-ip:5000/
```

#### WebSocket Connection Fails on Android

```dart
// Ensure CORS headers are set in Flask
# In app.py:
socketio = SocketIO(
    app, 
    cors_allowed_origins='*',  # or specific domain
    async_mode='threading'
)
```

#### APK Installation Fails

```bash
# Check Android version compatibility
flutter build apk --verbose

# Verify target SDK version in android/app/build.gradle
# Minimum SDK should be 21 or higher
```

---

## Part 12: Performance Optimization

### Backend Optimization

```python
# Use connection pooling
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

# Cache leaderboard (5 min TTL)
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/leaderboard')
@cache.cached(timeout=300)
def get_leaderboard():
    # ...
```

### Flutter App Optimization

```dart
// Use lazy loading for leaderboard
ListView.builder(
  itemCount: leaderboard.length,
  itemBuilder: (context, index) {
    return LeaderboardItem(leaderboard[index]);
  },
)

// Cache images locally
CachedNetworkImage(
  imageUrl: 'https://...',
  placeholder: (context, url) => CircularProgressIndicator(),
  cacheManager: DefaultCacheManager(),
)
```

---

## Part 13: Security Considerations

### For Both Web & Android

1. **Input Validation:** Sanitize all user inputs
2. **Rate Limiting:** Prevent brute force on API
3. **CORS Configuration:** Restrict origins
4. **HTTPS:** Always use SSL/TLS in production
5. **Session Management:** Secure session storage
6. **API Keys:** If added later, use secure storage

### Android Specific

```kotlin
// Use SharedPreferences with encryption
val encryptedSharedPreferences = EncryptedSharedPreferences.create(
    context,
    "secret_shared_prefs",
    MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```

---

## Part 14: CI/CD Pipeline for Multi-Platform

### GitHub Actions Workflow

```yaml
# .github/workflows/build.yml
name: Build Web & Android

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt
      - run: pytest tests/

  flutter-build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.x'
      - run: flutter pub get
      - run: flutter test
      - run: flutter build apk --release

  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: docker/build-push-action@v2
        with:
          context: .
          push: false
```

---

## References

- **Flutter Docs:** https://flutter.dev/docs
- **Socket.IO Dart:** https://pub.dev/packages/socket_io_client
- **Flask-RESTful:** https://flask-restful.readthedocs.io/
- **Android Development:** https://developer.android.com/docs
- **Google Play Console:** https://play.google.com/console
- **Firebase (for analytics):** https://firebase.google.com/

---

**Plan Created:** 2026-04-10  
**Status:** Ready for Phase 1 (API Refactoring)  
**Estimated Timeline:** 8 weeks for full implementation  

**Next Steps:**
1. Start with Phase 1: Refactor backend API
2. Create REST endpoints for mobile clients
3. Write API documentation
4. Setup Flutter project for Phase 2
5. Execute in parallel: Backend enhancements + Flutter development
