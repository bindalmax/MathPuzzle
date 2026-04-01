from database import db, Highscore

class HighscoreManager:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def add_score(self, name, score, category, difficulty, time_taken=None, questions_attempted=None):
        new_score = Highscore(
            name=name,
            score=score,
            category=category,
            difficulty=difficulty,
            time_taken=time_taken,
            questions_attempted=questions_attempted
        )
        db.session.add(new_score)
        db.session.commit()

    def load(self):
        """Loads all highscores and returns them as a list of dictionaries for compatibility."""
        scores = Highscore.query.order_by(Highscore.score.desc()).all()
        return [
            {
                'name': s.name,
                'score': s.score,
                'category': s.category,
                'difficulty': s.difficulty,
                'time_taken': s.time_taken,
                'questions_attempted': s.questions_attempted,
                'created_at': s.created_at
            }
            for s in scores
        ]

    def save(self, scores):
        """Legacy method for backward compatibility, though no longer needed for DB."""
        pass
