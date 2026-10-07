"""
Mistake Analyzer Service
Analyzes incorrect attempts to identify recurring misconceptions and patterns.
"""

from database import db, ProblemAttempt, MistakePattern
from datetime import datetime, timezone

class MistakeAnalyzer:
    @staticmethod
    def analyze_mistakes(user_name, limit=50):
        """
        Fetch recent incorrect attempts and categorize them.
        For Phase 2, we use rule-based heuristics.
        """
        incorrect_attempts = ProblemAttempt.query.filter_by(
            user_name=user_name,
            is_correct=False
        ).order_by(ProblemAttempt.created_at.desc()).limit(limit).all()
        
        patterns = []
        for attempt in incorrect_attempts:
            m_type = MistakeAnalyzer._categorize_mistake(attempt)
            if m_type:
                patterns.append({
                    'category': attempt.category,
                    'type': m_type,
                    'user_answer': attempt.user_answer,
                    'correct_answer': attempt.correct_answer
                })
                
        return patterns

    @staticmethod
    def _categorize_mistake(attempt):
        """Rule-based mistake categorization."""
        try:
            u_ans = float(attempt.user_answer)
            c_ans = float(attempt.correct_answer)
            
            # Sign Error
            if u_ans == -c_ans:
                return 'sign_error'
            
            # Small arithmetic/rounding error
            if abs(u_ans - c_ans) < 1.0:
                return 'arithmetic_error'
            
            # Conceptual: Answer is way off (e.g. 10x or 0.1x)
            if abs(u_ans / c_ans) == 10 or abs(c_ans / u_ans) == 10:
                return 'conceptual_decimal_shift'
                
        except (ValueError, ZeroDivisionError, TypeError):
            pass
            
        return 'conceptual_unknown'

    @staticmethod
    def update_mistake_patterns(user_name):
        """Aggregate analysis and update MistakePattern table."""
        raw_mistakes = MistakeAnalyzer.analyze_mistakes(user_name)
        
        for m in raw_mistakes:
            existing = MistakePattern.query.filter_by(
                user_name=user_name,
                category=m['category'],
                mistake_type=m['type']
            ).first()
            
            if existing:
                existing.frequency += 1
                existing.last_occurrence = datetime.now(timezone.utc)
            else:
                new_p = MistakePattern(
                    user_name=user_name,
                    category=m['category'],
                    mistake_type=m['type'],
                    frequency=1,
                    last_occurrence=datetime.now(timezone.utc)
                )
                db.session.add(new_p)
                
        db.session.commit()
