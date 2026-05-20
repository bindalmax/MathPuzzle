from database import db, Highscore

class HighscoreManager:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        if 'sqlalchemy' not in app.extensions:
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

    def load(self, category=None, difficulty=None, sort_by='score', page=1, per_page=10):
        """Loads paginated highscores based on filters."""
        query = Highscore.query
        
        if category and category != 'all':
            query = query.filter_by(category=category)
        if difficulty and difficulty != 'all':
            query = query.filter_by(difficulty=difficulty)
        
        if sort_by == 'time':
            query = query.order_by(Highscore.time_taken.asc())
        elif sort_by == 'name':
            query = query.order_by(Highscore.name.asc())
        else:
            query = query.order_by(Highscore.score.desc())
            
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        scores = pagination.items
        
        return {
            'scores': [
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
            ],
            'total_pages': pagination.pages,
            'current_page': pagination.page
        }

    def save(self, scores):
        """Legacy method for backward compatibility, though no longer needed for DB."""
        pass
