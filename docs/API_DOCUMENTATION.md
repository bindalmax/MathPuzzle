# MathPuzzle REST API Documentation

## Overview

The MathPuzzle REST API provides endpoints for mobile clients and external integrations to interact with the game. All endpoints return JSON responses with a standardized format.

## Base URL

- **Development**: `http://localhost:5000`
- **Production**: `https://your-domain.com`

## API Prefix

All endpoints are prefixed with `/api`

## Response Format

### Success Response
```json
{
  "status": "success",
  "message": "Success message",
  "data": { }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

## HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK - Request successful | GET leaderboard |
| 201 | Created - Resource created | POST score |
| 400 | Bad Request - Invalid input | Missing required fields |
| 404 | Not Found - Resource not found | Invalid question_id |
| 500 | Server Error | Database error |

---

## Endpoints

### 1. GET /api/categories

**Description**: Get list of all available question categories

**Method**: `GET`

**Parameters**: None

**Response**:
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "categories": [
      "basic_arithmetic",
      "decimal_fraction",
      "percentage",
      "profit_loss",
      "algebra"
    ]
  }
}
```

**Example**:
```bash
curl http://localhost:5000/api/categories
```

---

### 2. GET /api/difficulties

**Description**: Get list of all available difficulty levels

**Method**: `GET`

**Parameters**: None

**Response**:
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "difficulties": ["easy", "medium", "hard"]
  }
}
```

**Example**:
```bash
curl http://localhost:5000/api/difficulties
```

---

### 3. POST /api/question

**Description**: Get a new question based on category and difficulty

**Method**: `POST`

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "category": "basic_arithmetic",
  "difficulty": "easy"
}
```

**Required Fields**:
- `category` (string): One of: basic_arithmetic, decimal_fraction, percentage, profit_loss, algebra
- `difficulty` (string): One of: easy, medium, hard

**Response**:
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "question": "What is 2 + 3?",
    "choices": null,
    "question_id": "550e8400-e29b-41d4-a716-446655440000",
    "category": "basic_arithmetic",
    "difficulty": "easy"
  }
}
```

**Note**: `choices` is `null` for easy difficulty (open-ended questions), and contains an array of 4 options for medium/hard difficulties.

**Example**:
```bash
curl -X POST http://localhost:5000/api/question \
  -H "Content-Type: application/json" \
  -d '{
    "category": "basic_arithmetic",
    "difficulty": "easy"
  }'
```

**Error Examples**:

Missing parameters:
```json
{
  "status": "error",
  "message": "Both category and difficulty are required",
  "code": "MISSING_PARAMS"
}
```

Invalid category:
```json
{
  "status": "error",
  "message": "Invalid category. Must be one of: basic_arithmetic, decimal_fraction, ...",
  "code": "INVALID_CATEGORY"
}
```

---

### 4. POST /api/answer

**Description**: Submit an answer and validate it

**Method**: `POST`

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "question_id": "550e8400-e29b-41d4-a716-446655440000",
  "answer": 5
}
```

**Required Fields**:
- `question_id` (string): UUID returned from POST /api/question
- `answer` (number): The player's answer

**Response**:
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "is_correct": true,
    "correct_answer": 5,
    "score": 10
  }
}
```

**Response Fields**:
- `is_correct` (boolean): Whether the answer is correct
- `correct_answer` (number): The actual correct answer
- `score` (number): Points awarded (10 for correct, 0 for incorrect)

**Example**:
```bash
curl -X POST http://localhost:5000/api/answer \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "550e8400-e29b-41d4-a716-446655440000",
    "answer": 5
  }'
```

**Error Examples**:

Question not found:
```json
{
  "status": "error",
  "message": "Question not found. Request a new question first.",
  "code": "QUESTION_NOT_FOUND"
}
```

---

### 5. POST /api/score

**Description**: Save a player's score to the leaderboard

**Method**: `POST`

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "player_name": "Alice",
  "score": 150,
  "category": "basic_arithmetic",
  "difficulty": "hard",
  "time_taken": 45.5,
  "questions_attempted": 15
}
```

**Required Fields**:
- `player_name` (string): Player's name (1-80 characters)
- `score` (integer): Total score (must be non-negative)
- `category` (string): Question category
- `difficulty` (string): Difficulty level

**Optional Fields**:
- `time_taken` (float): Time taken in seconds (default: 0)
- `questions_attempted` (integer): Number of questions attempted (default: 0)

**Response**:
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "rank": 5,
    "message": "Score saved successfully"
  }
}
```

**Response Fields**:
- `rank` (integer): Player's rank on the leaderboard for this category/difficulty combination
- `message` (string): Confirmation message

**Example**:
```bash
curl -X POST http://localhost:5000/api/score \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "Alice",
    "score": 150,
    "category": "basic_arithmetic",
    "difficulty": "hard",
    "time_taken": 45.5,
    "questions_attempted": 15
  }'
```

**Error Examples**:

Invalid player name:
```json
{
  "status": "error",
  "message": "Player name must be 1-80 characters",
  "code": "INVALID_NAME"
}
```

Negative score:
```json
{
  "status": "error",
  "message": "Score cannot be negative",
  "code": "INVALID_SCORE"
}
```

---

### 6. GET /api/leaderboard

**Description**: Get leaderboard scores with optional filtering and pagination

**Method**: `GET`

**Query Parameters**:
| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| category | string | (none) | - | Filter by category (e.g., "basic_arithmetic") |
| difficulty | string | (none) | - | Filter by difficulty (e.g., "easy") |
| limit | integer | 50 | 500 | Number of results to return |
| offset | integer | 0 | - | Starting position for pagination |

**Response**:
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "leaderboard": [
      {
        "rank": 1,
        "name": "Alice",
        "score": 150,
        "category": "basic_arithmetic",
        "difficulty": "hard",
        "time_taken": 45.5,
        "questions_attempted": 15,
        "created_at": "2026-04-10T10:00:00"
      },
      {
        "rank": 2,
        "name": "Bob",
        "score": 140,
        "category": "basic_arithmetic",
        "difficulty": "hard",
        "time_taken": 50.0,
        "questions_attempted": 14,
        "created_at": "2026-04-10T11:00:00"
      }
    ],
    "total_count": 250,
    "limit": 50,
    "offset": 0
  }
}
```

**Examples**:

Get top 50 scores (all categories/difficulties):
```bash
curl "http://localhost:5000/api/leaderboard"
```

Get top 10 scores for basic_arithmetic/easy:
```bash
curl "http://localhost:5000/api/leaderboard?category=basic_arithmetic&difficulty=easy&limit=10"
```

Get scores 51-100 for percentage/medium:
```bash
curl "http://localhost:5000/api/leaderboard?category=percentage&difficulty=medium&limit=50&offset=50"
```

---

### 7. POST /api/multiplayer/create

**Description**: Create a new multiplayer game room

**Method**: `POST`

**Content-Type**: `application/json`

**Request Body**:
```json
{
  "player_name": "Alice",
  "category": "basic_arithmetic",
  "difficulty": "easy",
  "mode": "time",
  "mode_value": 20
}
```

**Required Fields**:
- `player_name` (string): Room creator's name
- `category` (string): Question category
- `difficulty` (string): Difficulty level
- `mode` (string): "time" or "questions"
- `mode_value` (integer): Duration in seconds (if mode="time") or number of questions (if mode="questions")

**Response**:
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "room_id": "abc12345",
    "status": "waiting",
    "players": ["Alice"],
    "category": "basic_arithmetic",
    "difficulty": "easy"
  }
}
```

**Example**:
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

---

### 8. GET /api/multiplayer/join/<room_id>

**Description**: Join an existing multiplayer game room

**Method**: `GET`

**URL Parameters**:
- `room_id` (string): Room ID returned from POST /api/multiplayer/create

**Query Parameters**:
- `player_name` (string, required): Name of the player joining

**Response**:
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "room_id": "abc12345",
    "status": "waiting",
    "players": ["Alice", "Bob"],
    "category": "basic_arithmetic",
    "difficulty": "easy"
  }
}
```

**Example**:
```bash
curl "http://localhost:5000/api/multiplayer/join/abc12345?player_name=Bob"
```

**Error Examples**:

Room not found:
```json
{
  "status": "error",
  "message": "Room not found",
  "code": "ROOM_NOT_FOUND"
}
```

Game already started:
```json
{
  "status": "error",
  "message": "Game has already started",
  "code": "GAME_STARTED"
}
```

Duplicate player name:
```json
{
  "status": "error",
  "message": "Player \"Bob\" already in this room",
  "code": "DUPLICATE_PLAYER"
}
```

---

## Error Codes Reference

| Error Code | HTTP Status | Meaning |
|------------|-------------|---------|
| INVALID_REQUEST | 400 | Missing or malformed request body |
| MISSING_PARAMS | 400 | Required parameter is missing |
| INVALID_CATEGORY | 400 | Invalid category provided |
| INVALID_DIFFICULTY | 400 | Invalid difficulty provided |
| NOT_IMPLEMENTED | 400 | Category/difficulty combination not yet implemented |
| GENERATION_ERROR | 500 | Error while generating question |
| QUESTION_NOT_FOUND | 404 | Question ID doesn't exist in session |
| VALIDATION_ERROR | 500 | Error while validating answer |
| INVALID_TYPE | 400 | Data type mismatch |
| DATABASE_ERROR | 500 | Database operation failed |
| INVALID_NAME | 400 | Player name is invalid |
| INVALID_SCORE | 400 | Score value is invalid |
| INVALID_MODE | 400 | Game mode is invalid |
| CREATION_ERROR | 500 | Error creating multiplayer room |
| ROOM_NOT_FOUND | 404 | Multiplayer room not found |
| GAME_STARTED | 400 | Game has already started |
| DUPLICATE_PLAYER | 400 | Player name already exists in room |
| JOIN_ERROR | 500 | Error joining multiplayer room |

---

## Authentication & Rate Limiting

Currently, no authentication is required. In future versions, API keys or JWT tokens may be implemented.

No rate limiting is currently enforced. For production deployments, rate limiting should be added.

---

## WebSocket Events (Multiplayer)

In addition to REST endpoints, the API supports WebSocket events for real-time multiplayer gameplay:

### Client → Server Events
- `join`: Join a multiplayer room
- `start_game_request`: Request to start the game (room creator only)

### Server → Client Events
- `game_start_signal`: Game has started
- `score_update`: Player scores updated
- `update_players`: Player list updated

---

## Client Libraries

### Python (requests)
```python
import requests

response = requests.get('http://localhost:5000/api/categories')
print(response.json())
```

### JavaScript (fetch)
```javascript
const response = await fetch('http://localhost:5000/api/categories');
const data = await response.json();
console.log(data);
```

### cURL
```bash
curl http://localhost:5000/api/categories
```

---

## Testing the API

### Using cURL
```bash
# Get categories
curl http://localhost:5000/api/categories

# Get a question
curl -X POST http://localhost:5000/api/question \
  -H "Content-Type: application/json" \
  -d '{"category": "basic_arithmetic", "difficulty": "easy"}'
```

### Using Postman
1. Import the Postman collection: `postman_collection.json`
2. Set environment variable `base_url` to `http://localhost:5000`
3. Click "Send" on any request

### Using Python Test Script
```bash
python3 test_api_phase1.py
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-11 | Initial API with question, answer, score, leaderboard endpoints |

---

## Support

For issues or questions:
1. Check the error codes above
2. Review request/response examples
3. Check Flask server logs
4. Open an issue on GitHub

---

**Last Updated**: 2026-04-11
