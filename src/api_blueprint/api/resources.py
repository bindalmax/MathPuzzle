"""
REST API Resources for MathPuzzle.
Implements endpoints for questions, answers, scoring, and multiplayer game management.
"""

from flask import request, session
from flask_restful import Resource, reqparse
from questions import QuestionFactory
from database import db, Highscore
from highscore_manager import HighscoreManager
from sqlalchemy.exc import IntegrityError
import uuid
import time
from .errors import api_success, api_error


class CategoriesResource(Resource):
    """GET /api/categories - List all available question categories"""
    
    def get(self):
        """Return list of available categories"""
        categories = [
            'basic_arithmetic',
            'decimal_fraction',
            'percentage',
            'profit_loss',
            'algebra'
        ]
        return api_success({'categories': categories}), 200


class DifficultiesResource(Resource):
    """GET /api/difficulties - List all difficulty levels"""
    
    def get(self):
        """Return list of available difficulty levels"""
        difficulties = ['easy', 'medium', 'hard']
        return api_success({'difficulties': difficulties}), 200


class QuestionResource(Resource):
    """POST /api/question - Get a new question"""
    
    def post(self):
        """
        Fetch a new question based on category and difficulty.
        
        Request Body:
        {
            "category": "basic_arithmetic",
            "difficulty": "easy"
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "question": "2 + 3 = ?",
                "choices": [4, 5, 6, 7],  # null for easy difficulty
                "question_id": "uuid"
            }
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return api_error('Request body is required', 400, 'INVALID_REQUEST')
            
            category = data.get('category', '').lower()
            difficulty = data.get('difficulty', '').lower()
            
            if not category or not difficulty:
                return api_error('Both category and difficulty are required', 400, 'MISSING_PARAMS')
            
            # Validate inputs
            valid_categories = ['basic_arithmetic', 'decimal_fraction', 'percentage', 'profit_loss', 'algebra']
            valid_difficulties = ['easy', 'medium', 'hard']
            
            if category not in valid_categories:
                return api_error(f'Invalid category. Must be one of: {", ".join(valid_categories)}', 400, 'INVALID_CATEGORY')
            
            if difficulty not in valid_difficulties:
                return api_error(f'Invalid difficulty. Must be one of: {", ".join(valid_difficulties)}', 400, 'INVALID_DIFFICULTY')
            
            # Generate question
            factory = QuestionFactory(category, difficulty)
            question, answer, choices = factory.create_question()
            
            # Store question in session (for validation later)
            if 'current_questions' not in session:
                session['current_questions'] = {}
            
            question_id = str(uuid.uuid4())
            session['current_questions'][question_id] = {
                'question': question,
                'answer': answer,
                'category': category,
                'difficulty': difficulty
            }
            
            return api_success({
                'question': question,
                'choices': choices,
                'answer': answer,
                'question_id': question_id,
                'category': category,
                'difficulty': difficulty
            }), 200
        
        except NotImplementedError as e:
            return api_error(f'Category/difficulty combination not implemented: {str(e)}', 400, 'NOT_IMPLEMENTED')
        except Exception as e:
            return api_error(f'Error generating question: {str(e)}', 500, 'GENERATION_ERROR')


class AnswerResource(Resource):
    """POST /api/answer - Validate an answer"""
    
    def post(self):
        """
        Submit an answer and get feedback.
        
        Request Body:
        {
            "question_id": "uuid",
            "answer": 5
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "is_correct": true,
                "correct_answer": 5,
                "score": 10
            }
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return api_error('Request body is required', 400, 'INVALID_REQUEST')
            
            question_id = data.get('question_id')
            user_answer = data.get('answer')
            
            if not question_id or user_answer is None:
                return api_error('question_id and answer are required', 400, 'MISSING_PARAMS')
            
            # Retrieve question from session
            if 'current_questions' not in session or question_id not in session['current_questions']:
                return api_error('Question not found. Request a new question first.', 404, 'QUESTION_NOT_FOUND')
            
            question_data = session['current_questions'][question_id]
            correct_answer = question_data['answer']
            
            # Validate answer (allowing small floating point differences)
            try:
                user_answer_float = float(user_answer)
                is_correct = abs(user_answer_float - correct_answer) < 0.01
            except (ValueError, TypeError):
                is_correct = False
            
            score = 10 if is_correct else 0
            
            return api_success({
                'is_correct': is_correct,
                'correct_answer': correct_answer,
                'score': score
            }), 200
        
        except Exception as e:
            return api_error(f'Error validating answer: {str(e)}', 500, 'VALIDATION_ERROR')


class ScoreResource(Resource):
    """POST /api/score - Save a score to leaderboard"""
    
    def post(self):
        """
        Save player score to database.
        
        Request Body:
        {
            "player_name": "John",
            "score": 100,
            "category": "basic_arithmetic",
            "difficulty": "easy",
            "time_taken": 45.5,
            "questions_attempted": 10
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "rank": 5,
                "message": "Score saved successfully"
            }
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return api_error('Request body is required', 400, 'INVALID_REQUEST')
            
            # Validate required fields
            required_fields = ['player_name', 'score', 'category', 'difficulty']
            for field in required_fields:
                if field not in data:
                    return api_error(f'Missing required field: {field}', 400, 'MISSING_FIELD')
            
            player_name = str(data['player_name']).strip()
            score = int(data['score'])
            category = str(data['category']).lower()
            difficulty = str(data['difficulty']).lower()
            time_taken = float(data.get('time_taken', 0))
            questions_attempted = int(data.get('questions_attempted', 0))
            
            # Validate inputs
            if not player_name or len(player_name) > 80:
                return api_error('Player name must be 1-80 characters', 400, 'INVALID_NAME')
            
            if score < 0:
                return api_error('Score cannot be negative', 400, 'INVALID_SCORE')
            
            # Create and save highscore
            highscore = Highscore(
                name=player_name,
                score=score,
                category=category,
                difficulty=difficulty,
                time_taken=time_taken,
                questions_attempted=questions_attempted
            )
            
            db.session.add(highscore)
            db.session.commit()
            
            # Get rank
            rank = db.session.query(Highscore).filter(
                Highscore.category == category,
                Highscore.difficulty == difficulty,
                Highscore.score > score
            ).count() + 1
            
            return api_success({
                'rank': rank,
                'message': 'Score saved successfully'
            }), 201
        
        except ValueError as e:
            return api_error(f'Invalid data type: {str(e)}', 400, 'INVALID_TYPE')
        except IntegrityError as e:
            db.session.rollback()
            return api_error(f'Database integrity error: {str(e)}', 400, 'INTEGRITY_ERROR')
        except Exception as e:
            db.session.rollback()
            return api_error(f'Error saving score: {str(e)}', 500, 'DATABASE_ERROR')


class LeaderboardResource(Resource):
    """GET /api/leaderboard - Get leaderboard scores"""
    
    def get(self):
        """
        Retrieve leaderboard with optional filtering.
        
        Query Parameters:
        - category: Filter by category (optional)
        - difficulty: Filter by difficulty (optional)
        - limit: Maximum number of results (default: 50, max: 500)
        - offset: Pagination offset (default: 0)
        
        Response:
        {
            "status": "success",
            "data": {
                "leaderboard": [
                    {
                        "rank": 1,
                        "name": "Alice",
                        "score": 150,
                        "category": "basic_arithmetic",
                        "difficulty": "hard",
                        "time_taken": 20.5,
                        "questions_attempted": 15,
                        "created_at": "2026-04-10T10:00:00"
                    },
                    ...
                ],
                "total_count": 1250
            }
        }
        """
        try:
            # Parse query parameters
            category = request.args.get('category', '').lower()
            difficulty = request.args.get('difficulty', '').lower()
            
            try:
                limit = int(request.args.get('limit', 50))
                offset = int(request.args.get('offset', 0))
                
                # Validate pagination
                if limit < 1 or limit > 500:
                    limit = 50
                if offset < 0:
                    offset = 0
            except ValueError:
                return api_error('limit and offset must be integers', 400, 'INVALID_PARAMS')
            
            # Build query
            query = Highscore.query
            
            if category:
                query = query.filter_by(category=category)
            
            if difficulty:
                query = query.filter_by(difficulty=difficulty)
            
            # Get total count
            total_count = query.count()
            
            # Sort by score descending, then by date
            scores = query.order_by(
                Highscore.score.desc(),
                Highscore.created_at.asc()
            ).limit(limit).offset(offset).all()
            
            # Format leaderboard with ranks
            leaderboard = []
            for idx, score in enumerate(scores, start=offset + 1):
                leaderboard.append({
                    'rank': idx,
                    'name': score.name,
                    'score': score.score,
                    'category': score.category,
                    'difficulty': score.difficulty,
                    'time_taken': score.time_taken,
                    'questions_attempted': score.questions_attempted,
                    'created_at': score.created_at.isoformat() if score.created_at else None
                })
            
            return api_success({
                'leaderboard': leaderboard,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }), 200
        
        except Exception as e:
            return api_error(f'Error fetching leaderboard: {str(e)}', 500, 'DATABASE_ERROR')


class MultiplaryCreateResource(Resource):
    """POST /api/multiplayer/create - Create a multiplayer game room"""
    
    def post(self):
        """
        Create a new multiplayer game room.
        
        Request Body:
        {
            "player_name": "John",
            "category": "basic_arithmetic",
            "difficulty": "easy",
            "mode": "time",
            "mode_value": 20
        }
        
        Response:
        {
            "status": "success",
            "data": {
                "room_id": "abc12345",
                "status": "waiting",
                "players": ["John"],
                "category": "basic_arithmetic",
                "difficulty": "easy"
            }
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return api_error('Request body is required', 400, 'INVALID_REQUEST')
            
            player_name = str(data.get('player_name', '')).strip()
            category = str(data.get('category', 'basic_arithmetic')).lower()
            difficulty = str(data.get('difficulty', 'easy')).lower()
            mode = str(data.get('mode', 'time')).lower()
            mode_value = int(data.get('mode_value', 20))
            
            if not player_name or len(player_name) > 80:
                return api_error('Valid player_name required (1-80 chars)', 400, 'INVALID_NAME')
            
            if mode not in ['time', 'questions']:
                return api_error('mode must be "time" or "questions"', 400, 'INVALID_MODE')
            
            # Generate room ID
            room_id = str(uuid.uuid4())[:8]
            
            # Store in session (TODO: move to Redis for scalability)
            if 'multiplayer_rooms' not in session:
                session['multiplayer_rooms'] = {}
            
            session['multiplayer_rooms'][room_id] = {
                'players': [player_name],
                'scores': {player_name: 0},
                'category': category,
                'difficulty': difficulty,
                'mode': mode,
                'mode_value': mode_value,
                'is_started': False,
                'creator': player_name,
                'created_at': time.time()
            }
            
            return api_success({
                'room_id': room_id,
                'status': 'waiting',
                'players': [player_name],
                'category': category,
                'difficulty': difficulty
            }), 201
        
        except Exception as e:
            return api_error(f'Error creating room: {str(e)}', 500, 'CREATION_ERROR')


class MultiplayerJoinResource(Resource):
    """GET /api/multiplayer/join/<room_id> - Join a multiplayer room"""
    
    def get(self, room_id):
        """
        Join an existing multiplayer room.
        
        Query Parameters:
        - player_name: Name of the player (required)
        
        Response:
        {
            "status": "success",
            "data": {
                "room_id": "abc12345",
                "status": "waiting",
                "players": ["John", "Jane"],
                "category": "basic_arithmetic",
                "difficulty": "easy"
            }
        }
        """
        try:
            player_name = request.args.get('player_name', '').strip()
            
            if not player_name or len(player_name) > 80:
                return api_error('Valid player_name required (1-80 chars)', 400, 'INVALID_NAME')
            
            if 'multiplayer_rooms' not in session or room_id not in session['multiplayer_rooms']:
                return api_error('Room not found', 404, 'ROOM_NOT_FOUND')
            
            room = session['multiplayer_rooms'][room_id]
            
            if room['is_started']:
                return api_error('Game has already started', 400, 'GAME_STARTED')
            
            if player_name in room['players']:
                return api_error(f'Player "{player_name}" already in this room', 400, 'DUPLICATE_PLAYER')
            
            # Add player to room
            room['players'].append(player_name)
            room['scores'][player_name] = 0
            
            return api_success({
                'room_id': room_id,
                'status': 'waiting',
                'players': room['players'],
                'category': room['category'],
                'difficulty': room['difficulty']
            }), 200
        
        except Exception as e:
            return api_error(f'Error joining room: {str(e)}', 500, 'JOIN_ERROR')
