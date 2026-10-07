"""
Attempt Logger Service
Handles logging of problem attempts with all relevant metadata for analytics.
"""

from database import db, ProblemAttempt, UserLearningProfile, LearningSession
from datetime import datetime
from logger import get_logger

logger = get_logger('attempt_logger')


class AttemptLogger:
    """Logs problem attempts and maintains learning profile statistics."""

    @staticmethod
    def log_attempt(user_name, problem_id, category, difficulty_level, 
                   user_answer, correct_answer, is_correct, time_taken_seconds=None,
                   problem_text=None):
        """
        Log a single problem attempt.
        
        Args:
            user_name (str): Username attempting the problem
            problem_id (str): Unique identifier for the problem
            category (str): Problem category (e.g., 'fractions', 'algebra')
            difficulty_level (float): Difficulty of the problem (0.1-5.0)
            user_answer (str): User's submitted answer
            correct_answer (str): Correct answer
            is_correct (bool): Whether answer is correct
            time_taken_seconds (float): Time spent on problem
            problem_text (str): Full problem text for reference
            
        Returns:
            ProblemAttempt: The logged attempt object
        """
        try:
            attempt = ProblemAttempt(
                user_name=user_name,
                problem_id=problem_id,
                category=category,
                difficulty_level=difficulty_level,
                user_answer=user_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
                time_taken_seconds=time_taken_seconds,
                problem_text=problem_text,
            )
            
            db.session.add(attempt)
            
            # Update user's learning profile statistics
            profile = UserLearningProfile.query.filter_by(user_name=user_name).first()
            if profile:
                profile.total_problems_attempted += 1
                if is_correct:
                    profile.total_problems_correct += 1
                profile.last_activity = datetime.utcnow()
                profile.last_updated = datetime.utcnow()
            
            db.session.commit()
            logger.debug(f"Logged attempt for {user_name} on {category} (correct={is_correct})")
            return attempt
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to log attempt for {user_name}: {e}", exc_info=True)
            return None

    @staticmethod
    def get_user_performance_by_category(user_name, days=None):
        """
        Get aggregated performance statistics per category for a user.
        
        Args:
            user_name (str): Username
            days (int): Limit to last N days (None = all time)
            
        Returns:
            dict: {category: {success_rate, attempts, avg_time, difficulty_avg}}
        """
        query = ProblemAttempt.query.filter_by(user_name=user_name)
        
        if days:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(ProblemAttempt.created_at >= cutoff_date)
        
        attempts = query.all()
        
        if not attempts:
            return {}
        
        # Group by category
        categories = {}
        for attempt in attempts:
            if attempt.category not in categories:
                categories[attempt.category] = {
                    'attempts': 0,
                    'correct': 0,
                    'total_time': 0,
                    'difficulties': [],
                }
            
            categories[attempt.category]['attempts'] += 1
            if attempt.is_correct:
                categories[attempt.category]['correct'] += 1
            if attempt.time_taken_seconds:
                categories[attempt.category]['total_time'] += attempt.time_taken_seconds
            categories[attempt.category]['difficulties'].append(attempt.difficulty_level)
        
        # Calculate stats
        stats = {}
        for category, data in categories.items():
            stats[category] = {
                'attempts': data['attempts'],
                'correct': data['correct'],
                'success_rate': round(data['correct'] / data['attempts'], 3),
                'avg_time_seconds': round(data['total_time'] / data['attempts'], 2) if data['total_time'] > 0 else 0,
                'avg_difficulty': round(sum(data['difficulties']) / len(data['difficulties']), 2),
            }
        
        return stats

    @staticmethod
    def get_recent_attempts(user_name, category=None, limit=50):
        """
        Get recent problem attempts for a user.
        
        Args:
            user_name (str): Username
            category (str): Filter by category (optional)
            limit (int): Maximum number of attempts to return
            
        Returns:
            list: List of ProblemAttempt objects
        """
        query = ProblemAttempt.query.filter_by(user_name=user_name)
        
        if category:
            query = query.filter_by(category=category)
        
        return query.order_by(ProblemAttempt.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_category_history(user_name, category, limit=100):
        """
        Get detailed attempt history for a specific category.
        
        Args:
            user_name (str): Username
            category (str): Category name
            limit (int): Max attempts to fetch
            
        Returns:
            list: List of attempts for that category
        """
        return ProblemAttempt.query.filter_by(
            user_name=user_name, 
            category=category
        ).order_by(ProblemAttempt.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_last_n_attempts(user_name, category, n=10):
        """
        Get last N attempts for difficulty calculation (Elo-like algorithm).
        
        Args:
            user_name (str): Username
            category (str): Category name
            n (int): Number of attempts
            
        Returns:
            list: List of most recent attempts (bools indicating correctness)
        """
        attempts = ProblemAttempt.query.filter_by(
            user_name=user_name,
            category=category
        ).order_by(ProblemAttempt.created_at.desc()).limit(n).all()
        
        # Return in chronological order (oldest first)
        return [attempt.is_correct for attempt in reversed(attempts)]
