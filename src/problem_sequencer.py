"""
Problem Sequencer Service
Generates personalized problem sequences based on learning gaps and topic mastery.
"""

import numpy as np
from learning_profile_service import LearningProfileService
from gap_detector import GapDetector

class ProblemSequencer:
    @staticmethod
    def generate_personalized_sequence(user_name, problem_count=10):
        """
        Algorithm:
        1. Identify weak topics (70% of problems)
        2. Mix in strength topics (20% for confidence)
        3. Include 1-2 new topics (10% for exploration)
        """
        profile = LearningProfileService.get_or_create_profile(user_name)
        gaps = GapDetector.detect_learning_gaps(user_name)
        
        # Topic selection weights
        weak_topics = [g['category'] for g in gaps]
        mastered_topics = profile.topics_mastered if profile.topics_mastered else []
        
        sequence = []
        
        # 1. Weak topics (70%)
        if weak_topics:
            num_weak = int(problem_count * 0.7)
            for _ in range(num_weak):
                sequence.append({
                    'category': np.random.choice(weak_topics),
                    'type': 'targeted_practice'
                })
        
        # 2. Mastered topics (20%)
        if mastered_topics:
            num_mastered = int(problem_count * 0.2)
            for _ in range(num_mastered):
                sequence.append({
                    'category': np.random.choice(mastered_topics),
                    'type': 'confidence_booster'
                })
        
        # 3. Fill remaining with exploration/fallback
        remaining = problem_count - len(sequence)
        all_categories = ['basic', 'decimal', 'percentage', 'profit', 'algebra']
        for _ in range(remaining):
            sequence.append({
                'category': np.random.choice(all_categories),
                'type': 'exploration'
            })
            
        # Shuffle for interleaving effect
        np.random.shuffle(sequence)
        return sequence
