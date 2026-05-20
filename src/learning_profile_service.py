"""
Learning Profile Service
Manages user learning profiles, skill tracking, and topic mastery.
"""

from database import db, UserLearningProfile, ProblemAttempt
from datetime import datetime, timedelta


class LearningProfileService:
    """Manages user learning profiles for adaptive learning."""

    @staticmethod
    def initialize_profile(user_name, learning_style='mixed'):
        """
        Initialize a new learning profile for a user.
        
        Args:
            user_name (str): Username
            learning_style (str): 'visual', 'analytical', 'kinesthetic', or 'mixed'
            
        Returns:
            UserLearningProfile: Newly created profile
        """
        existing = UserLearningProfile.query.filter_by(user_name=user_name).first()
        if existing:
            return existing
        
        profile = UserLearningProfile(
            user_name=user_name,
            current_skill_level=0.5,
            learning_velocity=0.02,
            preferred_difficulty=0.5,
            learning_style=learning_style,
            topics_mastered=[],
            weak_topics=[],
        )
        
        db.session.add(profile)
        db.session.commit()
        return profile

    @staticmethod
    def get_or_create_profile(user_name):
        """Get existing profile or create new one."""
        profile = UserLearningProfile.query.filter_by(user_name=user_name).first()
        if not profile:
            profile = LearningProfileService.initialize_profile(user_name)
        return profile

    @staticmethod
    def update_skill_level(user_name, category):
        """
        Update overall skill level based on recent performance across all categories.
        
        Args:
            user_name (str): Username
            category (str): Category being updated (tracked for updates)
        """
        profile = LearningProfileService.get_or_create_profile(user_name)
        
        # Get all recent attempts (last 50 across all categories)
        recent_attempts = ProblemAttempt.query.filter_by(
            user_name=user_name
        ).order_by(ProblemAttempt.created_at.desc()).limit(50).all()
        
        if not recent_attempts:
            return profile
        
        # Calculate success rate
        total = len(recent_attempts)
        correct = sum(1 for a in recent_attempts if a.is_correct)
        success_rate = correct / total if total > 0 else 0
        
        # Update skill level gradually (exponential smoothing)
        # New skill = 0.7 * old skill + 0.3 * recent performance
        old_skill = profile.current_skill_level
        new_skill = (0.7 * old_skill) + (0.3 * success_rate)
        profile.current_skill_level = round(new_skill, 3)
        
        # Calculate learning velocity (rate of improvement)
        week_ago = datetime.utcnow() - timedelta(days=7)
        week_attempts = ProblemAttempt.query.filter_by(
            user_name=user_name
        ).filter(ProblemAttempt.created_at >= week_ago).all()
        
        if week_attempts:
            week_success = sum(1 for a in week_attempts if a.is_correct) / len(week_attempts)
            # Velocity = change per week
            velocity = (new_skill - old_skill)
            profile.learning_velocity = round(velocity, 4)
        
        profile.last_updated = datetime.utcnow()
        db.session.commit()
        
        return profile

    @staticmethod
    def get_weak_topics(user_name, success_threshold=0.70, min_attempts=5):
        """
        Identify weak topics (success rate < threshold).
        
        Args:
            user_name (str): Username
            success_threshold (float): Max success rate to be considered weak
            min_attempts (int): Minimum attempts required in topic
            
        Returns:
            dict: {topic: success_rate} sorted by worst first
        """
        attempts = ProblemAttempt.query.filter_by(user_name=user_name).all()
        
        if not attempts:
            return {}
        
        # Group by category
        categories = {}
        for attempt in attempts:
            if attempt.category not in categories:
                categories[attempt.category] = {'total': 0, 'correct': 0}
            categories[attempt.category]['total'] += 1
            if attempt.is_correct:
                categories[attempt.category]['correct'] += 1
        
        # Find weak topics
        weak_topics = {}
        for category, stats in categories.items():
            if stats['total'] >= min_attempts:
                success_rate = stats['correct'] / stats['total']
                if success_rate < success_threshold:
                    weak_topics[category] = success_rate
        
        # Sort by worst first
        return dict(sorted(weak_topics.items(), key=lambda x: x[1]))

    @staticmethod
    def get_mastered_topics(user_name, mastery_threshold=0.80, min_attempts=5):
        """
        Identify mastered topics (success rate > threshold).
        
        Args:
            user_name (str): Username
            mastery_threshold (float): Min success rate to be considered mastered
            min_attempts (int): Minimum attempts required
            
        Returns:
            dict: {topic: success_rate}
        """
        attempts = ProblemAttempt.query.filter_by(user_name=user_name).all()
        
        if not attempts:
            return {}
        
        # Group by category
        categories = {}
        for attempt in attempts:
            if attempt.category not in categories:
                categories[attempt.category] = {'total': 0, 'correct': 0}
            categories[attempt.category]['total'] += 1
            if attempt.is_correct:
                categories[attempt.category]['correct'] += 1
        
        # Find mastered topics
        mastered = {}
        for category, stats in categories.items():
            if stats['total'] >= min_attempts:
                success_rate = stats['correct'] / stats['total']
                if success_rate >= mastery_threshold:
                    mastered[category] = success_rate
        
        return mastered

    @staticmethod
    def calculate_learning_velocity(user_name, days=7):
        """
        Calculate learning velocity (improvement rate per day).
        
        Args:
            user_name (str): Username
            days (int): Number of days to analyze
            
        Returns:
            float: Learning velocity score (0-1)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        attempts = ProblemAttempt.query.filter_by(
            user_name=user_name
        ).filter(ProblemAttempt.created_at >= cutoff_date).all()
        
        if not attempts:
            return 0.0
        
        # Split into first half and second half
        mid_point = len(attempts) // 2
        first_half = attempts[:mid_point]
        second_half = attempts[mid_point:]
        
        if not first_half or not second_half:
            return 0.0
        
        first_success = sum(1 for a in first_half if a.is_correct) / len(first_half)
        second_success = sum(1 for a in second_half if a.is_correct) / len(second_half)
        
        velocity = (second_success - first_success) / days
        return round(max(velocity, 0), 4)  # Clamp to 0

    @staticmethod
    def update_topics(user_name):
        """
        Update topic mastery lists in profile based on performance.
        
        Args:
            user_name (str): Username
        """
        profile = LearningProfileService.get_or_create_profile(user_name)
        
        mastered = LearningProfileService.get_mastered_topics(user_name)
        weak = LearningProfileService.get_weak_topics(user_name)
        
        profile.topics_mastered = list(mastered.keys())
        profile.weak_topics = list(weak.keys())
        profile.last_updated = datetime.utcnow()
        
        db.session.commit()
        return profile

    @staticmethod
    def get_profile_summary(user_name):
        """
        Get complete profile summary for dashboard.
        
        Args:
            user_name (str): Username
            
        Returns:
            dict: Complete profile information
        """
        profile = LearningProfileService.get_or_create_profile(user_name)
        
        weak_topics = LearningProfileService.get_weak_topics(user_name)
        mastered_topics = LearningProfileService.get_mastered_topics(user_name)
        velocity = LearningProfileService.calculate_learning_velocity(user_name)
        
        return {
            'user_name': user_name,
            'skill_level': round(profile.current_skill_level * 100, 1),  # 0-100%
            'learning_velocity': velocity,
            'learning_style': profile.learning_style,
            'problems_attempted': profile.total_problems_attempted,
            'problems_correct': profile.total_problems_correct,
            'accuracy': round((profile.total_problems_correct / profile.total_problems_attempted * 100), 1) if profile.total_problems_attempted > 0 else 0,
            'weak_topics': weak_topics,
            'mastered_topics': mastered_topics,
            'last_activity': profile.last_activity.isoformat() if profile.last_activity else None,
        }
