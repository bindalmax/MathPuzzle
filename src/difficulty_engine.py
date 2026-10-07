"""
Dynamic Difficulty Adjustment Engine
Elo-like rating system for adjusting problem difficulty based on user performance.
"""

from database import db, UserLearningProfile, ProblemAttempt
from learning_profile_service import LearningProfileService
from datetime import datetime, timedelta
from logger import get_logger

logger = get_logger('difficulty_engine')


class DifficultyEngine:
    """
    Manages dynamic difficulty adjustment using Elo-like algorithm.
    
    Target success rate: 70-80% (productive struggle zone)
    - >80% success: Problem too easy → increase difficulty
    - 60-70% success: Optimal difficulty → maintain
    - <60% success: Problem too hard → decrease difficulty
    """

    # Difficulty adjustment parameters
    MIN_DIFFICULTY = 0.1
    MAX_DIFFICULTY = 5.0
    OPTIMAL_SUCCESS_RATE = 0.70
    EASY_THRESHOLD = 0.80
    HARD_THRESHOLD = 0.60

    @staticmethod
    def adjust_difficulty(user_name, category, last_n_results, current_difficulty=None):
        """
        Calculate difficulty adjustment based on last N attempts.
        
        Args:
            user_name (str): Username
            category (str): Problem category
            last_n_results (list): List of last N attempts (True/False for correct/incorrect)
            current_difficulty (float): Current difficulty level (optional, fetched if None)
            
        Returns:
            float: Recommended new difficulty (0.1-5.0)
        """
        if not last_n_results or len(last_n_results) == 0:
            return current_difficulty or 1.0
        
        # Calculate success rate
        success_rate = sum(last_n_results) / len(last_n_results)
        
        if current_difficulty is None:
            current_difficulty = DifficultyEngine.get_current_difficulty(user_name, category)
        
        # Apply difficulty adjustment logic
        if success_rate > DifficultyEngine.EASY_THRESHOLD:
            # Too easy: increase difficulty by 15%
            new_difficulty = current_difficulty * 1.15
        elif success_rate < DifficultyEngine.HARD_THRESHOLD:
            # Too hard: decrease difficulty by 15%
            new_difficulty = current_difficulty * 0.85
        else:
            # Optimal range: maintain difficulty
            new_difficulty = current_difficulty
        
        # Clamp to valid range
        clamped_diff = round(max(DifficultyEngine.MIN_DIFFICULTY, 
                        min(new_difficulty, DifficultyEngine.MAX_DIFFICULTY)), 2)
        if clamped_diff != current_difficulty:
            logger.info(f"Adjusted difficulty for user='{user_name}' cat='{category}' from {current_difficulty} to {clamped_diff} (success_rate={success_rate:.2f})")
        return clamped_diff

    @staticmethod
    def get_recommended_difficulty(user_name, category):
        """
        Get recommended difficulty for next problem in a category.
        
        Args:
            user_name (str): Username
            category (str): Problem category
            
        Returns:
            float: Recommended difficulty (0.1-5.0)
        """
        # Get last 10 attempts
        from attempt_logger import AttemptLogger
        last_attempts = AttemptLogger.get_last_n_attempts(user_name, category, n=10)
        
        # Get current difficulty from profile
        profile = LearningProfileService.get_or_create_profile(user_name)
        current = profile.preferred_difficulty
        
        # If not enough history, use default
        if not last_attempts or len(last_attempts) < 3:
            return current
        
        # Adjust based on recent performance
        new_difficulty = DifficultyEngine.adjust_difficulty(
            user_name, category, last_attempts, current
        )
        
        return new_difficulty

    @staticmethod
    def get_current_difficulty(user_name, category, recent_problems=10):
        """
        Get current difficulty for a category (average of recent problems).
        
        Args:
            user_name (str): Username
            category (str): Problem category
            recent_problems (int): Number of recent problems to consider
            
        Returns:
            float: Current average difficulty
        """
        recent = ProblemAttempt.query.filter_by(
            user_name=user_name,
            category=category
        ).order_by(ProblemAttempt.created_at.desc()).limit(recent_problems).all()
        
        if not recent:
            return 1.0  # Default difficulty
        
        avg_difficulty = sum(a.difficulty_level for a in recent) / len(recent)
        return round(avg_difficulty, 2)

    @staticmethod
    def get_success_rate(user_name, category, recent_problems=10):
        """
        Get success rate for a category (last N problems).
        
        Args:
            user_name (str): Username
            category (str): Problem category
            recent_problems (int): Number of recent problems
            
        Returns:
            float: Success rate (0-1)
        """
        recent = ProblemAttempt.query.filter_by(
            user_name=user_name,
            category=category
        ).order_by(ProblemAttempt.created_at.desc()).limit(recent_problems).all()
        
        if not recent:
            return 0.5
        
        correct = sum(1 for a in recent if a.is_correct)
        return round(correct / len(recent), 3)

    @staticmethod
    def update_profile_difficulty(user_name):
        """
        Update the preferred difficulty in user profile based on overall performance.
        
        Args:
            user_name (str): Username
        """
        profile = LearningProfileService.get_or_create_profile(user_name)
        
        # Get overall success rate from all recent attempts
        recent = ProblemAttempt.query.filter_by(
            user_name=user_name
        ).order_by(ProblemAttempt.created_at.desc()).limit(30).all()
        
        if not recent:
            return
        
        overall_success = sum(1 for a in recent if a.is_correct) / len(recent)
        
        # Adjust preferred difficulty based on overall performance
        if overall_success > DifficultyEngine.EASY_THRESHOLD:
            profile.preferred_difficulty *= 1.10
        elif overall_success < DifficultyEngine.HARD_THRESHOLD:
            profile.preferred_difficulty *= 0.90
        
        # Clamp to valid range
        profile.preferred_difficulty = round(max(DifficultyEngine.MIN_DIFFICULTY,
                                                  min(profile.preferred_difficulty,
                                                      DifficultyEngine.MAX_DIFFICULTY)), 2)
        
        profile.last_updated = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def get_difficulty_stats(user_name):
        """
        Get difficulty statistics for all categories.
        
        Args:
            user_name (str): Username
            
        Returns:
            dict: {category: {current_difficulty, success_rate, recommendation}}
        """
        # Get all categories this user has attempted
        attempts = ProblemAttempt.query.filter_by(user_name=user_name).all()
        
        if not attempts:
            return {}
        
        categories = set(a.category for a in attempts)
        stats = {}
        
        for category in categories:
            current = DifficultyEngine.get_current_difficulty(user_name, category)
            success_rate = DifficultyEngine.get_success_rate(user_name, category)
            recommended = DifficultyEngine.get_recommended_difficulty(user_name, category)
            
            stats[category] = {
                'current_difficulty': current,
                'success_rate': success_rate,
                'recommended_difficulty': recommended,
                'status': DifficultyEngine._get_status(success_rate),
            }
        
        return stats

    @staticmethod
    def _get_status(success_rate):
        """Get human-readable difficulty status."""
        if success_rate > DifficultyEngine.EASY_THRESHOLD:
            return 'too_easy'
        elif success_rate < DifficultyEngine.HARD_THRESHOLD:
            return 'too_hard'
        else:
            return 'optimal'

    @staticmethod
    def get_difficulty_trend(user_name, category, days=30):
        """
        Get difficulty trend over time for a category.
        
        Args:
            user_name (str): Username
            category (str): Problem category
            days (int): Number of days to analyze
            
        Returns:
            list: Daily difficulty averages [{date, avg_difficulty, success_rate}]
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        attempts = ProblemAttempt.query.filter_by(
            user_name=user_name,
            category=category
        ).filter(ProblemAttempt.created_at >= cutoff_date).all()
        
        if not attempts:
            return []
        
        # Group by date
        daily_stats = {}
        for attempt in attempts:
            date_key = attempt.created_at.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {'difficulties': [], 'correct': 0, 'total': 0}
            
            daily_stats[date_key]['difficulties'].append(attempt.difficulty_level)
            daily_stats[date_key]['total'] += 1
            if attempt.is_correct:
                daily_stats[date_key]['correct'] += 1
        
        # Calculate daily stats
        result = []
        for date_key in sorted(daily_stats.keys()):
            stats = daily_stats[date_key]
            result.append({
                'date': date_key,
                'avg_difficulty': round(sum(stats['difficulties']) / len(stats['difficulties']), 2),
                'success_rate': round(stats['correct'] / stats['total'], 3),
            })
        
        return result
