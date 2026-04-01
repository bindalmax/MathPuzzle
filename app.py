from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms as socket_rooms
from questions import QuestionFactory
from highscore_manager import HighscoreManager
import time
import os
import uuid

app = Flask(__name__)

# Security: Enforce a secret key in production
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY and os.environ.get('FLASK_ENV') == 'production':
    raise RuntimeError("SECRET_KEY must be set in production environment")
app.secret_key = SECRET_KEY or 'dev-secret-key-change-in-production'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///math_game.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database manager
highscore_manager = HighscoreManager(app)

# Security: Restrict CORS origins (using * for dev, should be restricted in prod)
# Compatibility: Explicitly use 'threading' for Python 3.13 + Flask-SocketIO
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*')
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS, async_mode='threading')

# rooms[room_id] = { ... }
rooms = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['player_name'] = request.form['player_name']
        
        # Handle joining an existing room
        join_room_id = request.form.get('join_room_id')
        if join_room_id:
            if join_room_id in rooms:
                if rooms[join_room_id].get('is_started'):
                     return render_template('index.html', error="Game already started", active_rooms={k: v for k, v in rooms.items() if not v.get('is_started')})
                
                session['multiplayer'] = True
                session['room_id'] = join_room_id
                session['category'] = rooms[join_room_id]['category']
                session['difficulty'] = rooms[join_room_id]['difficulty']
                session['mode'] = rooms[join_room_id]['mode']
                session['mode_value'] = rooms[join_room_id]['mode_value']
                return redirect(url_for('multiplayer_lobby'))
            else:
                return render_template('index.html', error="Room not found", active_rooms={k: v for k, v in rooms.items() if not v.get('is_started')})

        # Common fields
        session['category'] = request.form['category']
        session['difficulty'] = request.form['difficulty']
        session['mode'] = request.form.get('mode', 'time')
        session['mode_value'] = int(request.form.get('mode_value', 20))
        
        game_type = request.form.get('game_type', 'single')
        
        if game_type == 'multiplayer':
            session['multiplayer'] = True
            room_id = str(uuid.uuid4())[:8]
            session['room_id'] = room_id
            rooms[room_id] = {
                'players': [], 
                'scores': {}, 
                'active_connections': set(),
                'category': session['category'], 
                'difficulty': session['difficulty'],
                'mode': session['mode'],
                'mode_value': session['mode_value'],
                'is_started': False,
                'results': {},
                'creator': session['player_name'],
                'question_pool': [],
                'last_activity': time.time()
            }
            return redirect(url_for('multiplayer_lobby'))
        
        session['score'] = 0
        session['questions_answered'] = 0
        session['start_time'] = time.time()
        session['multiplayer'] = False
        return redirect(url_for('game'))
    
    # Only show rooms that haven't started
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
    else:
        factory = QuestionFactory(session['category'], session['difficulty'])
        try:
            question, answer, choices = factory.create_question()
            session['current_answer'] = answer
        except NotImplementedError:
            return render_template('game_over.html', error=f"The '{session['category']}' category is not implemented for the '{session['difficulty']}' difficulty yet!")

    context = {
        'question': question,
        'score': session['score'],
        'mode': mode,
        'choices': choices
    }
    
    if mode == 'time':
        context['time_left'] = int(mode_value - elapsed_time)
    else:
        context['questions_left'] = mode_value - questions_answered
        
    return render_template('game.html', **context)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'start_time' not in session:
        return redirect(url_for('index'))

    try:
        user_answer = float(request.form['answer'])
        correct_answer = session.get('current_answer')

        if abs(user_answer - correct_answer) < 0.01:
            session['score'] += 1
            
            if session.get('multiplayer'):
                room_id = session.get('room_id')
                player_name = session.get('player_name')
                if room_id in rooms and player_name in rooms[room_id]['scores']:
                    rooms[room_id]['scores'][player_name] = session['score']
                    rooms[room_id]['last_activity'] = time.time()
                    socketio.emit('score_update', 
                                  {'players': rooms[room_id]['scores']}, 
                                  room=room_id)
    except (ValueError, TypeError):
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
    
    if 'start_time' in session:
        category = session.get('category', 'unknown')
        difficulty = session.get('difficulty', 'unknown')
        
        time_taken = time.time() - session['start_time']
        questions_answered = session.get('questions_answered', 0)
        
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

    return render_template('game_over.html', score=score, multiplayer_results=room_results)

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
        # Simple absolute score sorting for now, as DB doesn't automatically store %
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
    name = data.get('name')
    room = data.get('room')
    sid = request.sid
    
    if room and room in rooms:
        join_room(room)
        rooms[room]['active_connections'].add(sid)
        rooms[room]['last_activity'] = time.time()
        if name and name not in rooms[room]['players']:
            rooms[room]['players'].append(name)
            rooms[room]['scores'][name] = 0
        emit('update_players', rooms[room]['players'], room=room)

@socketio.on('start_game_request')
def handle_start_game_request(data=None):
    room_id = session.get('room_id')
    if not room_id and data:
        room_id = data.get('room')
    
    if room_id and room_id in rooms:
        if rooms[room_id]['creator'] == session.get('player_name'):
            factory = QuestionFactory(rooms[room_id]['category'], rooms[room_id]['difficulty'])
            pool = []
            for _ in range(50): 
                try:
                    pool.append(factory.create_question())
                except:
                    break
            rooms[room_id]['question_pool'] = pool
            rooms[room_id]['is_started'] = True
            rooms[room_id]['last_activity'] = time.time()
            emit('game_start_signal', room=room_id, to=room_id)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    for room_id, room_data in rooms.items():
        if sid in room_data['active_connections']:
            room_data['active_connections'].remove(sid)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
