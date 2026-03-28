from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from questions import QuestionFactory
from highscore_manager import HighscoreManager
import time
import os
import eventlet

# Use eventlet for high-concurrency support
eventlet.monkey_patch()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, async_mode='eventlet')

highscore_manager = HighscoreManager()

# --- Multiplayer State ---
players = {} # { 'name': score }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['player_name'] = request.form['player_name']
        session['category'] = request.form['category']
        session['difficulty'] = request.form['difficulty']
        session['mode'] = request.form.get('mode', 'time')
        session['mode_value'] = int(request.form.get('mode_value', 20))
        
        if request.form.get('multiplayer') == 'on':
            session['is_multiplayer'] = True
            return redirect(url_for('multiplayer_lobby'))
            
        session['is_multiplayer'] = False
        session['score'] = 0
        session['questions_answered'] = 0
        session['start_time'] = time.time()
        return redirect(url_for('game'))
    
    return render_template('index.html')

@app.route('/multiplayer_lobby')
def multiplayer_lobby():
    if 'player_name' not in session:
        return redirect(url_for('index'))
    return render_template('multiplayer_lobby.html', player_name=session['player_name'])

@app.route('/start_multiplayer_game')
def start_multiplayer_game():
    if 'player_name' not in session:
        return redirect(url_for('index'))
    
    session['score'] = 0
    session['questions_answered'] = 0
    session['start_time'] = time.time()
    return redirect(url_for('game'))

@app.route('/game')
def game():
    if 'start_time' not in session:
        return redirect(url_for('index'))

    elapsed_time = time.time() - session['start_time']
    mode = session.get('mode', 'time')
    mode_value = session.get('mode_value', 20)
    questions_answered = session.get('questions_answered', 0)

    # Check if game should end
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

    is_multiplayer = session.get('is_multiplayer', False)

    if mode == 'time':
        time_left = int(mode_value - elapsed_time)
        return render_template('game.html',
                               question=question,
                               score=session['score'],
                               time_left=time_left,
                               mode=mode,
                               choices=choices,
                               is_multiplayer=is_multiplayer)
    else:
        questions_left = mode_value - questions_answered
        return render_template('game.html',
                               question=question,
                               score=session['score'],
                               questions_left=questions_left,
                               mode=mode,
                               choices=choices,
                               is_multiplayer=is_multiplayer)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'start_time' not in session:
        return redirect(url_for('index'))

    try:
        user_answer = float(request.form['answer'])
        correct_answer = session.get('current_answer')

        if abs(user_answer - correct_answer) < 0.01:
            session['score'] += 1
            if session.get('is_multiplayer'):
                socketio.emit('score_update', {
                    'name': session['player_name'],
                    'score': session['score']
                }, to='lobby', namespace='/multiplayer')
    except (ValueError, TypeError):
        pass
    
    session['questions_answered'] = session.get('questions_answered', 0) + 1
    return redirect(url_for('game'))

@app.route('/game_over')
def game_over():
    score = session.get('score', 0)
    player_name = session.get('player_name', 'Player')
    
    if 'start_time' in session:
        category = session.get('category', 'unknown')
        difficulty = session.get('difficulty', 'unknown')
        time_taken = time.time() - session['start_time']
        questions_answered = session.get('questions_answered', 0)
        highscore_manager.add_score(player_name, score, category, difficulty, time_taken, questions_answered)

    session.pop('start_time', None)
    session.pop('current_answer', None)
    session.pop('is_multiplayer', None)
    
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
        
    return render_template('leaderboard.html', scores=scores, sort_by=sort_by, sort_order=sort_order, filter_category=filter_category, filter_difficulty=filter_difficulty)

@app.route('/quit')
def quit_game():
    session.clear()
    return render_template('quit.html')

# --- SocketIO Events ---
@socketio.on('join', namespace='/multiplayer')
def on_join(data):
    name = data['name']
    join_room('lobby')
    players[name] = 0
    emit('update_players', list(players.keys()), to='lobby')

@socketio.on('start_game_request', namespace='/multiplayer')
def on_start_game_request():
    # Signal all players to start
    emit('game_start_signal', to='lobby')

@socketio.on('disconnect', namespace='/multiplayer')
def on_disconnect():
    # Find and remove player by name (not ideal but works for simple case)
    # In a real app we'd map sid to name
    pass

if __name__ == '__main__':
    socketio.run(app, debug=True)
