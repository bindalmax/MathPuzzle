import sqlite3
import os
from database import db, Highscore, User

class HighscoreManager:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def add_score(self, name, score, category, difficulty, time_taken=0, questions_attempted=0, user_id=None):
        """Add a new score entry to the database."""
        new_highscore = Highscore(
            name=name,
            score=score,
            category=category,
            difficulty=difficulty,
            time_taken=time_taken,
            questions_attempted=questions_attempted,
            user_id=user_id # Link to persistent user if available
        )
        db.session.add(new_highscore)
        db.session.commit()

    def load(self, limit=100):
        """Fetch highscores, sorted by score (descending) then time_taken (ascending)."""
        scores = Highscore.query.order_by(Highscore.score.desc(), Highscore.time_taken.asc()).limit(limit).all()
        return [
            {
                'name': s.name,
                'score': s.score,
                'category': s.category,
                'difficulty': s.difficulty,
                'time_taken': s.time_taken,
                'questions_attempted': s.questions_attempted,
                'created_at': s.created_at.isoformat()
            }
            for s in scores
        ]
