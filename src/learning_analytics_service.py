"""
Learning Analytics Service
Aggregates performance data and generates insights for the dashboard.
"""

from database import db, ProblemAttempt, MistakePattern, UserLearningProfile
from datetime import datetime, timedelta
from sqlalchemy import func
from gap_detector import GapDetector
from mistake_analyzer import MistakeAnalyzer

class LearningAnalyticsService:
    @staticmethod
    def get_progress_data(user_name, days=30):
        """Aggregate daily performance data for visualization."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        attempts = ProblemAttempt.query.filter(
            ProblemAttempt.user_name == user_name,
            ProblemAttempt.created_at >= cutoff
        ).order_by(ProblemAttempt.created_at.asc()).all()
        
        data = {}
        for a in attempts:
            day = a.created_at.strftime('%Y-%m-%d')
            if day not in data:
                data[day] = {'total': 0, 'correct': 0}
            data[day]['total'] += 1
            if a.is_correct:
                data[day]['correct'] += 1
                
        return [
            {'date': day, 'accuracy': round(v['correct'] / v['total'] * 100, 1)}
            for day, v in sorted(data.items())
        ]

    @staticmethod
    def get_learning_gaps(user_name):
        """Fetch identified learning gaps."""
        return GapDetector.detect_learning_gaps(user_name)

    @staticmethod
    def get_mistake_insights(user_name):
        """Fetch recurring mistake patterns for actionable feedback."""
        # Update patterns before fetching
        MistakeAnalyzer.update_mistake_patterns(user_name)
        mistakes = MistakePattern.query.filter_by(user_name=user_name).order_by(MistakePattern.frequency.desc()).all()
        return [m.to_dict() for m in mistakes]
