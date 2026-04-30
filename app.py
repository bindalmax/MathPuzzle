import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from flask import Flask, render_template, request, redirect, url_for, session, abort, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms as socket_rooms
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bleach
from questions import QuestionFactory
from highscore_manager import HighscoreManager
from room_storage import rooms
import time
import uuid

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'static'))

# Environment Configuration
FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
# Disable CSRF in non-production environments (makes testing & development easier)
app.config['WTF_CSRF_ENABLED'] = (FLASK_ENV == 'production')

# Security: Hardened Secret Key management
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if FLASK_ENV == 'production':
        raise RuntimeError("SECRET_KEY must be set in production environment")
    SECRET_KEY = 'dev-secret-key-change-in-production'
app.secret_key = SECRET_KEY

# CSRF Protection
csrf = CSRFProtect(app)

# Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
# During automated tests, toggle the limiter off to avoid 429s from E2E/UI test suites
@app.before_request
def _adjust_rate_limiter_for_tests():
    try:
        limiter.enabled = not app.config.get('TESTING', False)
    except Exception:
        # If limiter isn't available for any reason, skip toggling
        pass

# Database Configuration
db_url = os.environ.get('DATABASE_URL', 'sqlite:///math_game.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database manager
highscore_manager = HighscoreManager(app)

# Security: Restrict CORS origins
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*')
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS, async_mode='threading')

# Register REST API Blueprint
from api_blueprint.api import api_bp
app.register_blueprint(api_bp)
# Exempt API blueprint from CSRF protection in non-production/testing environments only
# Allow disabling CSRF for API endpoints via environment variable when running test servers
# This is safer than turning off CSRF globally in production.
if os.environ.get('DISABLE_API_CSRF', '0') == '1' or not app.config.get('WTF_CSRF_ENABLED', True):
    csrf.exempt(api_bp)

# Global rooms dictionary removed, now imported from room_storage


def sanitize_input(text):
    """Sanitize user input to prevent XSS."""
    return bleach.clean(text.strip())

@app.route('/sw.js')
def serve_sw():
    return send_from_directory(app.static_folder, 'sw.js', mimetype='application/javascript')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(app.static_folder, 'manifest.json', mimetype='application/manifest+json')

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def index():
    if request.method == 'POST':
        player_name = sanitize_input(request.form.get('player_name', 'Player'))
        
        if len(player_name) > 20:
            return render_template('index.html', error="GamerId too long (max 20 chars)", active_rooms={k: v for k, v in rooms.items() if not v.get('is_started')})

        join_room_id = request.form.get('join_room_id')
        if join_room_id:
            if join_room_id in rooms:
                if rooms[join_room_id].get('is_started'):
                     return render_template('index.html', error="Game already started", active_rooms={k: v for k, v in rooms.items() if not v.get('is_started')})
                
                if player_name in rooms[join_room_id]['players']:
                    return render_template('index.html', error=f"GamerId '{player_name}' is already taken in this room", active_rooms={k: v for k, v in rooms.items() if not v.get('is_started')})

                session['player_name'] = player_name
                session['multiplayer'] = True
                session['room_id'] = join_room_id
                session['category'] = rooms[join_room_id]['category']
                session['difficulty'] = rooms[join_room_id]['difficulty']
                session['mode'] = rooms[join_room_id]['mode']
                session['mode_value'] = rooms[join_room_id]['mode_value']
                return redirect(url_for('multiplayer_lobby'))
            else:
                return render_template('index.html', error="Room not found", active_rooms={k: v for k, v in rooms.items() if not v.get('is_started')})

        # Set Defaults
        session['player_name'] = player_name
        session['category'] = request.form.get('category', 'percentage')
        session['difficulty'] = request.form.get('difficulty', 'medium')
        session['mode'] = request.form.get('mode', 'time')
        session['mode_value'] = int(request.form.get('mode_value', 20))
        
        game_type = request.form.get('game_type', 'multiplayer')
        
        if game_type == 'startup_challenge':
            session['multiplayer'] = False
            session['is_startup_challenge'] = True
            session['startup_value'] = 10000.0
            session['score'] = 0
            session['questions_answered'] = 0
            session['total_questions'] = 10
            session['start_time'] = time.time()
            session['category'] = 'percentage' # Initial, will alternate
            session['difficulty'] = 'medium'
            session['mode'] = 'questions'
            session['mode_value'] = 10
            return redirect(url_for('game'))

        if game_type == 'multiplayer':
            session['multiplayer'] = True
            room_id = str(uuid.uuid4())[:8]
            session['room_id'] = room_id
            player_name = session['player_name']
            rooms[room_id] = {
                'players': [player_name], 
                'scores': {player_name: 0}, 
                'active_connections': set(),
                'category': session['category'], 
                'difficulty': session['difficulty'],
                'mode': session['mode'],
                'mode_value': session['mode_value'],
                'is_started': False,
                'results': {},
                'creator': player_name,
                'question_pool': [],
                'last_activity': time.time()
            }
            return redirect(url_for('multiplayer_lobby'))
        
        session['score'] = 0
        session['questions_answered'] = 0
        session['start_time'] = time.time()
        session['multiplayer'] = False
        return redirect(url_for('game'))
    
    visible_rooms = {k: v for k, v in rooms.items() if not v.get('is_started')}
    return render_template('index.html', active_rooms=visible_rooms)

@app.route('/game')
def game():
    if 'start_time' not in session:
        return redirect(url_for('index'))

    elapsed_time = time.time() - session['start_time']
    mode = session.get('mode', 'time')
    mode_value = session.get('mode_value', 20)
    questions_answered = session.get('questions_answered', 0)

    if mode == 'time' and elapsed_time > mode_value:
        return redirect(url_for('game_over'))
    elif mode == 'questions' and questions_answered >= mode_value:
        return redirect(url_for('game_over'))

    if session.get('multiplayer'):
        room_id = session.get('room_id')
        q_idx = session.get('question_index', 0)
        if room_id in rooms and q_idx < len(rooms[room_id]['question_pool']):
            question, answer, choices = rooms[room_id]['question_pool'][q_idx]
            session['current_answer'] = answer
        else:
            return redirect(url_for('game_over'))
    elif session.get('is_startup_challenge'):
        # Alternate between percentage and profit_loss
        category = 'percentage' if questions_answered % 2 == 0 else 'profit_loss'
        session['category'] = category
        factory = QuestionFactory(category, 'medium')
        try:
            question, answer, choices = factory.create_question()
            session['current_answer'] = answer
            # Add narrative prefix
            narrative = "Market Analysis: " if category == 'percentage' else "Financial Planning: "
            question = narrative + question
        except Exception as e:
            app.logger.error(f"Error in startup challenge: {str(e)}")
            return render_template('game_over.html', error="An unexpected error occurred.")
    else:
        factory = QuestionFactory(session.get('category', 'basic'), session.get('difficulty', 'medium'))
        try:
            question, answer, choices = factory.create_question()
            session['current_answer'] = answer
        except (NotImplementedError, ValueError) as e:
            return render_template('game_over.html', error=f"Error generating question: {str(e)}")
        except Exception as e:
            app.logger.error(f"Unexpected error in /game: {str(e)}")
            return render_template('game_over.html', error="An unexpected error occurred. Please try again.")

    context = {
        'question': question,
        'score': session['score'],
        'mode': 'questions' if session.get('is_startup_challenge') else mode,
        'choices': choices,
        'startup_value': session.get('startup_value'),
        'is_startup_challenge': session.get('is_startup_challenge')
    }
    
    if session.get('is_startup_challenge'):
        context['questions_left'] = session.get('total_questions', 10) - questions_answered
    elif mode == 'time':
        context['time_left'] = int(mode_value - elapsed_time)
    else:
        context['questions_left'] = mode_value - questions_answered
        
    return render_template('game.html', **context)

@app.route('/submit_answer', methods=['POST'])
@limiter.limit("2 per second")
def submit_answer():
    if 'start_time' not in session:
        return redirect(url_for('index'))

    try:
        user_answer = float(request.form['answer'])
        correct_answer = session.get('current_answer')

        if abs(user_answer - correct_answer) < 0.01:
            session['score'] += 1
            
            if session.get('is_startup_challenge'):
                growth = session['startup_value'] * 0.2
                session['startup_value'] += growth
            
            if session.get('multiplayer'):
                room_id = session.get('room_id')
                player_name = session.get('player_name')
                if room_id in rooms and player_name in rooms[room_id]['scores']:
                    rooms[room_id]['scores'][player_name] = session['score']
                    rooms[room_id]['last_activity'] = time.time()
                    socketio.emit('score_update', 
                                  {'players': rooms[room_id]['scores']}, 
                                  room=room_id)
        elif session.get('is_startup_challenge'):
            loss = session['startup_value'] * 0.1
            session['startup_value'] -= loss
    except (ValueError, TypeError):
        if session.get('is_startup_challenge'):
             loss = session['startup_value'] * 0.1
             session['startup_value'] -= loss
        pass
    
    session['questions_answered'] = session.get('questions_answered', 0) + 1
    if session.get('multiplayer'):
        session['question_index'] = session.get('question_index', 0) + 1
        
    return redirect(url_for('game'))

@app.route('/game_over')
def game_over():
    score = session.get('score', 0)
    player_name = session.get('player_name', 'Player')
    
    room_results = None
    startup_data = None
    
    if 'start_time' in session:
        category = session.get('category', 'unknown')
        difficulty = session.get('difficulty', 'unknown')
        
        time_taken = time.time() - session['start_time']
        questions_answered = session.get('questions_answered', 0)
        
        if session.get('is_startup_challenge'):
            final_value = session.get('startup_value', 0)
            ceo_score = int(final_value / 100)
            if ceo_score > 500:
                title = "Unicorn CEO 🦄"
            elif ceo_score > 200:
                title = "Serial Entrepreneur 🚀"
            elif ceo_score > 100:
                title = "Startup Founder 💼"
            else:
                title = "Junior Founder 🌱"
            
            startup_data = {
                'final_value': final_value,
                'ceo_score': ceo_score,
                'title': title
            }
            # Use ceo_score as the main score for highscores
            score = ceo_score
            category = "startup_challenge"

        highscore_manager.add_score(player_name, score, category, difficulty, time_taken, questions_answered)

        if session.get('multiplayer'):
            room_id = session.get('room_id')
            if room_id in rooms:
                rooms[room_id]['scores'][player_name] = score
                rooms[room_id]['results'] = rooms[room_id]['scores'].copy()
                rooms[room_id]['last_activity'] = time.time()
                room_results = rooms[room_id]['results']
                socketio.emit('score_update', {'players': rooms[room_id]['scores']}, room=room_id)

    session.pop('start_time', None)
    session.pop('current_answer', None)
    
    if session.get('multiplayer'):
        room_id = session.get('room_id')
        if not room_results and room_id in rooms:
             room_results = rooms[room_id].get('results', rooms[room_id]['scores'])

    is_startup = session.get('is_startup_challenge', False)
    # Clear startup challenge state after game over
    session.pop('is_startup_challenge', None)
    session.pop('startup_value', None)

    return render_template('game_over.html', score=score, multiplayer_results=room_results, startup_data=startup_data, is_startup_challenge=is_startup)

@app.route('/restart')
def restart():
    """Restart the game with same settings as previous session."""
    if 'player_name' not in session:
        return redirect(url_for('index'))
    
    # Reset game state variables in session
    session['score'] = 0
    session['questions_answered'] = 0
    session['question_index'] = 0
    session['start_time'] = time.time()
    
    # If multiplayer, we return to the lobby (or index if room is gone)
    if session.get('multiplayer'):
        room_id = session.get('room_id')
        if room_id in rooms:
            return redirect(url_for('multiplayer_lobby'))
        return redirect(url_for('index'))
        
    return redirect(url_for('game'))

@app.route('/leaderboard')
def leaderboard():
    scores = highscore_manager.load()
    
    filter_category = request.args.get('filter_category', 'all')
    filter_difficulty = request.args.get('filter_difficulty', 'all')
    
    if filter_category != 'all':
        scores = [s for s in scores if s.get('category') == filter_category]
    if filter_difficulty != 'all':
        scores = [s for s in scores if s.get('difficulty') == filter_difficulty]
        
    sort_by = request.args.get('sort_by', 'score')
    sort_order = request.args.get('sort_order', 'desc')
    
    reverse = sort_order == 'desc'
    
    if sort_by == 'score':
        scores.sort(key=lambda x: x['score'], reverse=reverse)
    elif sort_by == 'time':
        scores.sort(key=lambda x: x.get('time_taken', 0), reverse=reverse)
    elif sort_by == 'name':
        scores.sort(key=lambda x: x.get('name', ''), reverse=reverse)
        
    return render_template('leaderboard.html', 
                           scores=scores,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           filter_category=filter_category,
                           filter_difficulty=filter_difficulty)

@app.route('/quit')
def quit_game():
    if session.get('multiplayer'):
        room_id = session.get('room_id')
        player_name = session.get('player_name')
        if room_id in rooms:
            if player_name in rooms[room_id]['players']:
                rooms[room_id]['players'].remove(player_name)
            if player_name in rooms[room_id]['scores']:
                del rooms[room_id]['scores'][player_name]
            if not rooms[room_id]['players']:
                del rooms[room_id]
                
    session.clear()
    return render_template('quit.html')

@app.route('/multiplayer_lobby', methods=['GET', 'POST'])
def multiplayer_lobby():
    room_id = session.get('room_id')
    if not room_id or room_id not in rooms:
        return redirect(url_for('index'))
    
    is_creator = (rooms[room_id]['creator'] == session.get('player_name'))
    return render_template('multiplayer_lobby.html', 
                           player_name=session.get('player_name', ''),
                           is_creator=is_creator)

@app.route('/start_multiplayer_game')
def start_multiplayer_game():
    if 'multiplayer' not in session:
        return redirect(url_for('index'))
    
    session['score'] = 0
    session['questions_answered'] = 0
    session['question_index'] = 0
    session['start_time'] = time.time()
    return redirect(url_for('game'))

@socketio.on('join')
def handle_join(data):
    name = sanitize_input(data.get('name', 'Player'))
    room = data.get('room')
    sid = request.sid
    
    if room and room in rooms:
        join_room(room)
        session['room_id'] = room
        session['player_name'] = name
        rooms[room]['active_connections'].add(sid)
        rooms[room]['last_activity'] = time.time()
        if name and name not in rooms[room]['players']:
            rooms[room]['players'].append(name)
            rooms[room]['scores'][name] = 0
        emit('score_update', {'players': rooms[room]['scores']}, room=room)
        emit('update_players', rooms[room]['players'], room=room)

@socketio.on('update_score')
def handle_update_score(data):
    room = data.get('room')
    name = data.get('name')
    score = data.get('score')
    
    if room and room in rooms and name in rooms[room]['scores']:
        rooms[room]['scores'][name] = score
        rooms[room]['last_activity'] = time.time()
        emit('score_update', {'players': rooms[room]['scores']}, room=room)

@socketio.on('start_game_request')
def handle_start_game_request(data=None):
    room_id = session.get('room_id')
    if not room_id and data:
        room_id = data.get('room')
    
    player_name = session.get('player_name')
    if not player_name and data:
        player_name = data.get('name')

    print(f"Start game request for room {room_id} by {player_name}")
    
    if room_id and room_id in rooms:
        # Check if the requester is the creator
        if rooms[room_id]['creator'] == player_name:
            factory = QuestionFactory(rooms[room_id]['category'], rooms[room_id]['difficulty'])
            pool = []
            for _ in range(50): 
                try:
                    pool.append(factory.create_question())
                except Exception as e:
                    app.logger.error(f"Failed to pre-generate question in pool: {str(e)}")
                    break
            rooms[room_id]['question_pool'] = pool
            rooms[room_id]['is_started'] = True
            rooms[room_id]['last_activity'] = time.time()
            print(f"Emitting game_start_signal to room {room_id}")
            # Use socketio.emit to ensure broadcast to the room
            socketio.emit('game_start_signal', {'room': room_id}, room=room_id)
        else:
            print(f"Unauthorized start request: {player_name} is not {rooms[room_id]['creator']}")

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    for room_id, room_data in rooms.items():
        if sid in room_data['active_connections']:
            room_data['active_connections'].remove(sid)

if __name__ == '__main__':
    with app.app_context():
        from database import db
        db.create_all()
    port = int(os.environ.get('PORT', 5005))
    if FLASK_ENV == 'development':
        cert_file = 'cert.pem'
        key_file = 'key.pem'
        ssl_ctx = (cert_file, key_file) if os.path.exists(cert_file) else 'adhoc'
        socketio.run(app, debug=True, host='0.0.0.0', port=port, ssl_context=ssl_ctx, allow_unsafe_werkzeug=True)
    else:
        socketio.run(app, debug=False, host='0.0.0.0', port=port)
