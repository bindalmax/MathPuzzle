from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from questions import QuestionFactory
from highscore_manager import HighscoreManager
import time
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Removed eventlet async_mode due to Python 3.13 compatibility issues
# SocketIO will default to standard threading
socketio = SocketIO(app, cors_allowed_origins="*")

highscore_manager = HighscoreManager()

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
            session['room_id'] = f"{session['category']}_{session['difficulty']}"
            return redirect(url_for('multiplayer_lobby'))
        
        session['score'] = 0
        session['questions_answered'] = 0
        session['start_time'] = time.time()
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

    if mode == 'time':
        time_left = int(mode_value - elapsed_time)
        return render_template('game.html',
                               question=question,
                               score=session['score'],
                               time_left=time_left,
                               mode=mode,
                               choices=choices) # Pass choices
    else:
        questions_left = mode_value - questions_answered
        return render_template('game.html',
                               question=question,
                               score=session['score'],
                               questions_left=questions_left,
                               mode=mode,
                               choices=choices) # Pass choices

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'start_time' not in session:
        return redirect(url_for('index'))

    try:
        user_answer = float(request.form['answer'])
        correct_answer = session.get('current_answer')

        if abs(user_answer - correct_answer) < 0.01:
            session['score'] += 1
    except (ValueError, TypeError):
        pass
    
    session['questions_answered'] = session.get('questions_answered', 0) + 1
    return redirect(url_for('game'))

@app.route('/game_over')
def game_over():
    score = session.get('score', 0)
    player_name = session.get('player_name', 'Player')
    
    # Save the score
    if 'start_time' in session: # Ensure it's a real game over
        category = session.get('category', 'unknown')
        difficulty = session.get('difficulty', 'unknown')
        
        time_taken = time.time() - session['start_time']
        questions_answered = session.get('questions_answered', 0)
        
        highscore_manager.add_score(player_name, score, category, difficulty, time_taken, questions_answered)

    # Clean up session for the next game
    session.pop('start_time', None)
    session.pop('current_answer', None)
    
    return render_template('game_over.html', score=score)

@app.route('/leaderboard')
def leaderboard():
    scores = highscore_manager.load()
    
    # Filtering
    filter_category = request.args.get('filter_category', 'all')
    filter_difficulty = request.args.get('filter_difficulty', 'all')
    
    if filter_category != 'all':
        scores = [s for s in scores if s.get('category') == filter_category]
    if filter_difficulty != 'all':
        scores = [s for s in scores if s.get('difficulty') == filter_difficulty]
        
    # Sorting
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
        session['room_id'] = f"{session['category']}_{session['difficulty']}"
        session['multiplayer'] = True
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
    print(f"Join event: name={name}, room={room}")
    
    if room:
        join_room(room)
    
    if room not in rooms:
        rooms[room] = {'players': [], 'scores': {}}
    
    if name and name not in rooms[room]['players']:
        rooms[room]['players'].append(name)
        rooms[room]['scores'][name] = 0
    
    print(f"Players in room {room}: {rooms[room]['players']}")
    
    if room:
        emit('update_players', rooms[room]['players'], room=room)

@socketio.on('start_game_request')
def handle_start_game_request(data=None):
    room = session.get('room_id')
    if not room and data:
        room = data.get('room')
    print(f"Start game request: room={room}, rooms={list(rooms.keys())}")
    if room and room in rooms:
        emit('game_start_signal', room=room, to=room)

@socketio.on('answer')
def handle_answer(data):
    room = data.get('room')
    name = data.get('name')
    score = data.get('score')
    
    if room in rooms:
        rooms[room]['scores'][name] = score
        emit('score_update', {'players': rooms[room]['scores']}, room=room, include_self=False)

@socketio.on('disconnect')
def handle_disconnect():
    pass

if __name__ == '__main__':
    # Using socketio.run with debug=True. It will use standard threading without eventlet.
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
