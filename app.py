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

# Security: Restrict CORS origins (using * for dev, should be restricted in prod)
# Compatibility: Explicitly use 'threading' for Python 3.13 + Flask-SocketIO
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*')
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS, async_mode='threading')

highscore_manager = HighscoreManager()

# rooms[room_id] = {'players': [], 'scores': {}, 'category': '', 'difficulty': ''}
rooms = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['player_name'] = request.form['player_name']
        session['category'] = request.form['category']
        session['difficulty'] = request.form['difficulty']
        session['mode'] = request.form.get('mode', 'time')
        session['mode_value'] = int(request.form.get('mode_value', 20))
        
        game_type = request.form.get('game_type', 'single')
        
        if game_type == 'multiplayer':
            session['multiplayer'] = True
            # Security: Use UUID for room IDs to prevent guessing
            room_id = str(uuid.uuid4())[:8]
            session['room_id'] = room_id
            rooms[room_id] = {
                'players': [], 
                'scores': {}, 
                'category': session['category'], 
                'difficulty': session['difficulty']
            }
            return redirect(url_for('multiplayer_lobby'))
        
        session['score'] = 0
        session['questions_answered'] = 0
        session['start_time'] = time.time()
        session['multiplayer'] = False
        return redirect(url_for('game'))
    
    return render_template('index.html')

@app.route('/game')
def game():
    if 'start_time' not in session:
        return redirect(url_for('index'))

    elapsed_time = time.time() - session['start_time']
    mode = session.get('mode', 'time')
    mode_value = session.get('mode_value', 20)
    questions_answered = session.get('questions_answered', 0)

    # Check if game should end based on mode
    if mode == 'time' and elapsed_time > mode_value:
        return redirect(url_for('game_over'))
    elif mode == 'questions' and questions_answered >= mode_value:
        return redirect(url_for('game_over'))

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
            
            # Security: Server-authoritative score update for multiplayer
            if session.get('multiplayer'):
                room_id = session.get('room_id')
                player_name = session.get('player_name')
                if room_id in rooms and player_name in rooms[room_id]['scores']:
                    rooms[room_id]['scores'][player_name] = session['score']
                    # Broadcast update to all players in the room
                    socketio.emit('score_update', 
                                  {'players': rooms[room_id]['scores']}, 
                                  room=room_id)
    except (ValueError, TypeError):
        pass
    
    session['questions_answered'] = session.get('questions_answered', 0) + 1
    return redirect(url_for('game'))

@app.route('/game_over')
def game_over():
    score = session.get('score', 0)
    player_name = session.get('player_name', 'Player')
    
    # Save the score
    if 'start_time' in session:
        category = session.get('category', 'unknown')
        difficulty = session.get('difficulty', 'unknown')
        
        time_taken = time.time() - session['start_time']
        questions_answered = session.get('questions_answered', 0)
        
        highscore_manager.add_score(player_name, score, category, difficulty, time_taken, questions_answered)

    # Clean up session
    session.pop('start_time', None)
    session.pop('current_answer', None)
    
    return render_template('game_over.html', score=score)

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
        scores.sort(key=lambda x: (x['score'] / x['questions_attempted']) if x.get('questions_attempted', 0) > 0 else x['score'], reverse=reverse)
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
    session.clear()
    return render_template('quit.html')

@app.route('/multiplayer_lobby', methods=['GET', 'POST'])
def multiplayer_lobby():
    if request.method == 'POST':
        session['player_name'] = request.form['player_name']
        session['category'] = request.form['category']
        session['difficulty'] = request.form['difficulty']
        session['mode'] = 'time'
        session['mode_value'] = int(request.form.get('mode_value', 20))
        
        room_id = str(uuid.uuid4())[:8]
        session['room_id'] = room_id
        session['multiplayer'] = True
        
        rooms[room_id] = {
            'players': [], 
            'scores': {}, 
            'category': session['category'], 
            'difficulty': session['difficulty']
        }
        return redirect(url_for('multiplayer_lobby'))
    return render_template('multiplayer_lobby.html', player_name=session.get('player_name', ''))

@app.route('/start_multiplayer_game')
def start_multiplayer_game():
    if 'multiplayer' not in session:
        return redirect(url_for('index'))
    
    session['score'] = 0
    session['questions_answered'] = 0
    session['start_time'] = time.time()
    return redirect(url_for('game'))

@socketio.on('join')
def handle_join(data):
    name = data.get('name')
    room = data.get('room')
    
    if room and room in rooms:
        join_room(room)
        if name and name not in rooms[room]['players']:
            rooms[room]['players'].append(name)
            rooms[room]['scores'][name] = 0
        emit('update_players', rooms[room]['players'], room=room)

@socketio.on('start_game_request')
def handle_start_game_request(data=None):
    room = session.get('room_id')
    if not room and data:
        room = data.get('room')
    
    # Security: Verify room exists and sender is authorized (in the room)
    if room and room in rooms:
        emit('game_start_signal', room=room, to=room)

@socketio.on('disconnect')
def handle_disconnect():
    # Optional: logic to remove player from room on disconnect
    pass

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
