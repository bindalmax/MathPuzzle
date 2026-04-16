from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Highscore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    difficulty = db.Column(db.String(80), nullable=False)
    time_taken = db.Column(db.Float, nullable=True)
    questions_attempted = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Highscore {self.name} - {self.score}>'
