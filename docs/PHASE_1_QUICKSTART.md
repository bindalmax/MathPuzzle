# Phase 1: Quick Start Guide

## ✅ Phase 1 Complete!

All REST API endpoints have been implemented and are ready for mobile development.

---

## What Was Built

**8 REST API Endpoints** for MathPuzzle:
- Categories & Difficulties metadata
- Question fetching & answer validation
- Score saving & leaderboard queries
- Multiplayer room creation & joining

**100% backwards compatible** with existing web interface.

---

## File Structure

```
AIHandsOn/
├── app/
│   ├── __init__.py
│   └── api/
│       ├── __init__.py          # Blueprint registration
│       ├── errors.py            # Error handling
│       └── resources.py         # All 8 endpoints (400+ lines)
├── app.py                       # Updated with API blueprint
├── test_api_phase1.py          # Test suite
├── postman_collection.json     # Postman requests
└── docs/
    ├── API_DOCUMENTATION.md    # Full reference (12K+ words)
    ├── PHASE_1_COMPLETION.md   # Completion details
    └── WEB_AND_ANDROID_PLAN.md # Master plan
```

---

## Quick Start

### 1. Install Dependencies
```bash
cd /Users/keshavbindal/IdeaProjects/AIHandsOn
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

### 2. Start Flask Server
```bash
python3 app.py
```
Server: `http://localhost:5000`

### 3. Test the API

**Option A: Run Python Test Script**
```bash
python3 test_api_phase1.py
```

**Option B: Use cURL**
```bash
# Get categories
curl http://localhost:5000/api/categories

# Get a question
curl -X POST http://localhost:5000/api/question \
  -H "Content-Type: application/json" \
  -d '{"category": "basic_arithmetic", "difficulty": "easy"}'
```

**Option C: Use Postman**
1. Import `postman_collection.json`
2. Set `base_url` to `http://localhost:5000`
3. Click "Send"

---

## API Endpoints Reference

### Metadata
```
GET /api/categories      → ["basic_arithmetic", "percentage", ...]
GET /api/difficulties    → ["easy", "medium", "hard"]
```

### Single Player Game Flow
```
POST /api/question       → Get a question
POST /api/answer         → Check if answer is correct
POST /api/score          → Save score to leaderboard
GET  /api/leaderboard    → View high scores
```

### Multiplayer
```
POST /api/multiplayer/create              → Create room, get room_id
GET  /api/multiplayer/join/<room_id>      → Join existing room
```

---

## Example Game Flow

### 1. Get Categories
```bash
curl http://localhost:5000/api/categories
```
Response:
```json
{
  "status": "success",
  "data": {
    "categories": ["basic_arithmetic", "percentage", "profit_loss", ...]
  }
}
```

### 2. Get a Question
```bash
curl -X POST http://localhost:5000/api/question \
  -H "Content-Type: application/json" \
  -d '{"category": "basic_arithmetic", "difficulty": "easy"}'
```
Response:
```json
{
  "status": "success",
  "data": {
    "question": "What is 2 + 3?",
    "choices": null,
    "question_id": "abc-123-def",
    "category": "basic_arithmetic",
    "difficulty": "easy"
  }
}
```

### 3. Submit Answer
```bash
curl -X POST http://localhost:5000/api/answer \
  -H "Content-Type: application/json" \
  -d '{"question_id": "abc-123-def", "answer": 5}'
```
Response:
```json
{
  "status": "success",
  "data": {
    "is_correct": true,
    "correct_answer": 5,
    "score": 10
  }
}
```

### 4. Save Score
```bash
curl -X POST http://localhost:5000/api/score \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "Alice",
    "score": 100,
    "category": "basic_arithmetic",
    "difficulty": "easy",
    "time_taken": 45,
    "questions_attempted": 10
  }'
```
Response:
```json
{
  "status": "success",
  "data": {
    "rank": 5,
    "message": "Score saved successfully"
  }
}
```

### 5. View Leaderboard
```bash
curl "http://localhost:5000/api/leaderboard?category=basic_arithmetic&difficulty=easy&limit=10"
```
Response:
```json
{
  "status": "success",
  "data": {
    "leaderboard": [
      {
        "rank": 1,
        "name": "Alice",
        "score": 150,
        "category": "basic_arithmetic",
        "difficulty": "easy",
        ...
      }
    ],
    "total_count": 250,
    "limit": 10,
    "offset": 0
  }
}
```

---

## Multiplayer Example

### 1. Create Room
```bash
curl -X POST http://localhost:5000/api/multiplayer/create \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "Alice",
    "category": "basic_arithmetic",
    "difficulty": "easy",
    "mode": "time",
    "mode_value": 20
  }'
```
Response:
```json
{
  "status": "success",
  "data": {
    "room_id": "abc12345",
    "status": "waiting",
    "players": ["Alice"],
    "category": "basic_arithmetic",
    "difficulty": "easy"
  }
}
```

### 2. Join Room
```bash
curl "http://localhost:5000/api/multiplayer/join/abc12345?player_name=Bob"
```
Response:
```json
{
  "status": "success",
  "data": {
    "room_id": "abc12345",
    "status": "waiting",
    "players": ["Alice", "Bob"],
    "category": "basic_arithmetic",
    "difficulty": "easy"
  }
}
```

---

## Documentation

- **Full API Docs**: `docs/API_DOCUMENTATION.md` (12,700+ words)
- **Error Codes**: See API_DOCUMENTATION.md for all 17 error codes
- **Phase 1 Details**: `docs/PHASE_1_COMPLETION.md`

---

## Error Handling

All errors return consistent format:
```json
{
  "status": "error",
  "message": "Human-readable error message",
  "code": "ERROR_CODE"
}
```

Common error codes:
- `INVALID_CATEGORY` - Category not found
- `INVALID_DIFFICULTY` - Difficulty not found
- `QUESTION_NOT_FOUND` - Question ID invalid
- `INVALID_NAME` - Player name invalid
- `ROOM_NOT_FOUND` - Multiplayer room not found

---

## Next Steps

### For Mobile Developers
1. Review `docs/API_DOCUMENTATION.md`
2. Import `postman_collection.json` into Postman
3. Test endpoints manually
4. Start Phase 2: Flutter app development
5. Use API endpoints in mobile app

### For Backend Developers
1. Monitor API usage in production
2. Implement caching for leaderboard (optional)
3. Add rate limiting (optional)
4. Move multiplayer to Redis (when scaling)

---

## Integration with Existing Web App

✅ **Both work simultaneously:**
```
Web UI:   http://localhost:5000/          (HTML pages, WebSockets)
API:      http://localhost:5000/api/...   (JSON responses)
```

No changes needed to existing web routes.

---

## Troubleshooting

### "Connection refused"
```
Check: Is Flask server running?
Fix:   python3 app.py
```

### "Not Found" (404)
```
Check: Is endpoint URL correct? (include /api/ prefix)
Example: ✅ http://localhost:5000/api/categories
Example: ❌ http://localhost:5000/categories
```

### "Invalid JSON"
```
Check: Is Content-Type header set to "application/json"?
Check: Is JSON body valid? (use JSON validator)
```

### "Question not found"
```
Check: Did you call POST /api/question first?
Check: Is question_id correct?
```

---

## Status

| Component | Status |
|-----------|--------|
| ✅ API Blueprint | Complete |
| ✅ 8 REST Endpoints | Complete |
| ✅ Error Handling | Complete |
| ✅ Database Integration | Complete |
| ✅ Documentation | Complete |
| ✅ Postman Collection | Complete |
| ✅ Test Script | Complete |
| ✅ Backwards Compatibility | Complete |

---

## What's Next?

**Phase 2: Flutter App Development** (Week 3-6)
- Flutter project setup
- API service integration
- UI screens
- WebSocket multiplayer
- APK build & testing

Check `docs/WEB_AND_ANDROID_PLAN.md` for full roadmap.

---

**API is production-ready! 🚀**

Questions? Check the full documentation or run the test script.
