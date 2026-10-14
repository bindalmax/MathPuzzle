import sqlite3
import os
from database import db, Highscore, User
from logger import get_logger

logger = get_logger('highscore_manager')

class HighscoreManager:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app, create_tables=False):
        if 'sqlalchemy' not in app.extensions:
            db.init_app(app)
        if create_tables:
            with app.app_context():
                db.create_all()

    def add_score(self, name, score, category, difficulty, time_taken=0, questions_attempted=0, user_id=None):
        """Add a new score entry to the database with safe fallback and rollback."""
        try:
            # Validate user_id exists if provided to prevent foreign key errors
            valid_user_id = None
            if user_id is not None:
                try:
                    user_record = db.session.get(User, user_id)
                    if user_record:
                        valid_user_id = user_id
                except Exception as e:
                    logger.debug(f"User check for user_id={user_id} bypassed: {e}")

            new_highscore = Highscore(
                name=str(name),
                score=int(score),
                category=str(category),
                difficulty=str(difficulty),
                time_taken=float(time_taken),
                questions_attempted=int(questions_attempted),
                user_id=valid_user_id
            )
            db.session.add(new_highscore)
            db.session.commit()
            logger.info(f"Recorded highscore for {name}: {score} pts in category='{category}' ({difficulty})")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to record highscore for '{name}': {str(e)}", exc_info=True)
            return False

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
