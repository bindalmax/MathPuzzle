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


# ============================================================================
# AI-POWERED ADAPTIVE LEARNING MODELS (Phase 0)
# ============================================================================

class UserLearningProfile(db.Model):
    """Tracks user skill levels, learning velocity, and topic mastery."""
    __tablename__ = 'user_learning_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    current_skill_level = db.Column(db.Float, default=0.5)  # 0-1 normalized
    learning_velocity = db.Column(db.Float, default=0.02)  # speed of improvement
    preferred_difficulty = db.Column(db.Float, default=0.5)  # 0.1-5.0 scale
    topics_mastered = db.Column(db.JSON, default=list)  # array of topic names
    weak_topics = db.Column(db.JSON, default=list)  # array of weak topic names
    learning_style = db.Column(db.String(50), default='mixed')  # visual, analytical, kinesthetic, mixed
    total_problems_attempted = db.Column(db.Integer, default=0)
    total_problems_correct = db.Column(db.Integer, default=0)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<UserLearningProfile {self.user_name} (skill={self.current_skill_level:.2f})>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'current_skill_level': self.current_skill_level,
            'learning_velocity': self.learning_velocity,
            'preferred_difficulty': self.preferred_difficulty,
            'topics_mastered': self.topics_mastered,
            'weak_topics': self.weak_topics,
            'learning_style': self.learning_style,
            'total_problems_attempted': self.total_problems_attempted,
            'total_problems_correct': self.total_problems_correct,
        }


class ProblemAttempt(db.Model):
    """Logs every problem attempt with detailed metadata for analytics."""
    __tablename__ = 'problem_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False, index=True)
    problem_id = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    difficulty_level = db.Column(db.Float, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, index=True)
    time_taken_seconds = db.Column(db.Float, nullable=True)
    user_answer = db.Column(db.String(500))
    correct_answer = db.Column(db.String(500))
    problem_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        db.Index('idx_problem_user_category', 'user_name', 'category'),
        db.Index('idx_user_created', 'user_name', 'created_at'),
        db.Index('idx_category_correct', 'category', 'is_correct'),
    )

    def __repr__(self):
        result = '✓' if self.is_correct else '✗'
        return f'<ProblemAttempt {self.user_name} {result} ({self.category})>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'problem_id': self.problem_id,
            'category': self.category,
            'difficulty_level': self.difficulty_level,
            'is_correct': self.is_correct,
            'time_taken_seconds': self.time_taken_seconds,
            'user_answer': self.user_answer,
            'correct_answer': self.correct_answer,
            'problem_text': self.problem_text,
            'created_at': self.created_at.isoformat(),
        }


class MistakePattern(db.Model):
    """Identifies recurring error patterns and misconceptions."""
    __tablename__ = 'mistake_patterns'
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False)
    mistake_type = db.Column(db.String(200), nullable=False)  # e.g., "sign_error", "arithmetic_error"
    frequency = db.Column(db.Integer, default=1)
    severity_score = db.Column(db.Float, default=0.5)  # 0-1 how serious
    last_occurrence = db.Column(db.DateTime, default=datetime.utcnow)
    misconception_description = db.Column(db.Text)
    recommended_strategy = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_mistake_user_category', 'user_name', 'category'),
        db.Index('idx_user_type', 'user_name', 'mistake_type'),
    )

    def __repr__(self):
        return f'<MistakePattern {self.user_name} {self.mistake_type} (freq={self.frequency})>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'category': self.category,
            'mistake_type': self.mistake_type,
            'frequency': self.frequency,
            'severity_score': self.severity_score,
            'last_occurrence': self.last_occurrence.isoformat(),
            'misconception_description': self.misconception_description,
            'recommended_strategy': self.recommended_strategy,
        }


class LearningSession(db.Model):
    """Tracks user learning sessions for engagement and consistency metrics."""
    __tablename__ = 'learning_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False, index=True)
    session_start = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    session_end = db.Column(db.DateTime, nullable=True)
    problems_attempted = db.Column(db.Integer, default=0)
    problems_correct = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Float, nullable=True)
    focus_category = db.Column(db.String(100))  # which category was focused

    def __repr__(self):
        accuracy = (self.problems_correct / self.problems_attempted * 100) if self.problems_attempted > 0 else 0
        return f'<LearningSession {self.user_name} {accuracy:.0f}% ({self.problems_attempted} problems)>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'session_start': self.session_start.isoformat(),
            'session_end': self.session_end.isoformat() if self.session_end else None,
            'problems_attempted': self.problems_attempted,
            'problems_correct': self.problems_correct,
            'duration_minutes': self.duration_minutes,
            'focus_category': self.focus_category,
        }
