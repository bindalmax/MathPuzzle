from flask import Flask, render_template, request, redirect, url_for, session
from questions import QuestionFactory
import time
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Highscore Management (copied from math_game.py) ---
class HighscoreManager:
    def __init__(self, filename="highscores.json"):
        self.filename = filename

    def load(self):
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save(self, highscores):
        with open(self.filename, 'w') as f:
            json.dump(highscores, f, indent=4)

    def add_score(self, name, score):
        highscores = self.load()
        highscores.append({'name': name, 'score': score})
        self.save(highscores)

highscore_manager = HighscoreManager()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['player_name'] = request.form['player_name']
        session['category'] = request.form['category']
        session['difficulty'] = request.form['difficulty']
        session['score'] = 0
        session['start_time'] = time.time()
        return redirect(url_for('game'))
    
    return render_template('index.html')

@app.route('/game')
def game():
    if 'start_time' not in session:
        return redirect(url_for('index'))

    elapsed_time = time.time() - session['start_time']
    if elapsed_time > 20:
        return redirect(url_for('game_over'))

    factory = QuestionFactory(session['category'], session['difficulty'])
    try:
        question, answer = factory.create_question()
        session['current_answer'] = answer
    except NotImplementedError:
        return render_template('game_over.html', error=f"The '{session['category']}' category is not implemented for the '{session['difficulty']}' difficulty yet!")

    return render_template('game.html', 
                           question=question, 
                           score=session['score'],
                           time_left=int(20 - elapsed_time))

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
    
    return redirect(url_for('game'))

@app.route('/game_over')
def game_over():
    score = session.get('score', 0)
    player_name = session.get('player_name', 'Player')
    
    # Save the score
    if 'start_time' in session: # Ensure it's a real game over
        highscore_manager.add_score(player_name, score)

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
