from flask import Flask, render_template, request, redirect, url_for, session
from questions import QuestionFactory
import time
import os

app = Flask(__name__)
# A secret key is required for using sessions
app.secret_key = os.urandom(24)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Store player info and game settings in the session
        session['player_name'] = request.form['player_name']
        session['category'] = request.form['category']
        session['difficulty'] = request.form['difficulty']
        
        # Initialize game state
        session['score'] = 0
        session['start_time'] = time.time()
        
        return redirect(url_for('game'))
    
    return render_template('index.html')

@app.route('/game')
def game():
    # Check if the game has started
    if 'start_time' not in session:
        return redirect(url_for('index'))

    # Check if time is up
    elapsed_time = time.time() - session['start_time']
    if elapsed_time > 20:
        return redirect(url_for('game_over'))

    # Generate a new question
    factory = QuestionFactory(session['category'], session['difficulty'])
    try:
        question, answer = factory.create_question()
        session['current_answer'] = answer
    except NotImplementedError:
        return render_template('game_over.html', error="This category isn't implemented yet!")

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
        # Ignore invalid answers
        pass
    
    return redirect(url_for('game'))

@app.route('/game_over')
def game_over():
    score = session.pop('score', 0)
    # You could add high score logic here if desired
    return render_template('game_over.html', score=score)

if __name__ == '__main__':
    app.run(debug=True)
