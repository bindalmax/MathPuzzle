from flask import Flask, render_template, request, redirect, url_for, session
from questions import QuestionFactory
from highscore_manager import HighscoreManager
import time
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

highscore_manager = HighscoreManager()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['player_name'] = request.form['player_name']
        session['category'] = request.form['category']
        session['difficulty'] = request.form['difficulty']
        session['mode'] = request.form.get('mode', 'time')
        session['mode_value'] = int(request.form.get('mode_value', 20))
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
        question, answer = factory.create_question()
        session['current_answer'] = answer
    except NotImplementedError:
        return render_template('game_over.html', error=f"The '{session['category']}' category is not implemented for the '{session['difficulty']}' difficulty yet!")

    if mode == 'time':
        time_left = int(mode_value - elapsed_time)
        return render_template('game.html',
                               question=question,
                               score=session['score'],
                               time_left=time_left,
                               mode=mode)
    else:
        questions_left = mode_value - questions_answered
        return render_template('game.html',
                               question=question,
                               score=session['score'],
                               questions_left=questions_left,
                               mode=mode)

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
        highscore_manager.add_score(player_name, score, category, difficulty)

    # Clean up session for the next game
    session.pop('start_time', None)
    session.pop('current_answer', None)
    
    return render_template('game_over.html', score=score)

@app.route('/leaderboard')
def leaderboard():
    scores = highscore_manager.load()
    sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    return render_template('leaderboard.html', scores=sorted_scores[:10]) # Show top 10

@app.route('/quit')
def quit_game():
    # Clear all session data
    session.clear()
    return render_template('quit.html')

if __name__ == '__main__':
    app.run(debug=True)
