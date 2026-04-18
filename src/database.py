from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    display_name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to link highscores
    highscores = db.relationship('Highscore', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.display_name}>'

class Highscore(db.Model):
    __tablename__ = 'highscore'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    difficulty = db.Column(db.String(80), nullable=False)
    time_taken = db.Column(db.Float, nullable=True)
    questions_attempted = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional link to a registered user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f'<Highscore {self.name} - {self.score}>'
