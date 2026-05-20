"""
Unit Tests for Phase 0: Database Models and Core Services
Tests dynamic difficulty adjustment, learning profiles, and attempt logging.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask
from database import db, UserLearningProfile, ProblemAttempt, MistakePattern, LearningSession
from attempt_logger import AttemptLogger
from learning_profile_service import LearningProfileService
from difficulty_engine import DifficultyEngine


class Phase0TestCase(unittest.TestCase):
    """Test suite for Phase 0 implementation."""

    def setUp(self):
        """Set up test database and app."""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        
        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()
            self.client = self.app.test_client()

    def tearDown(self):
        """Clean up test database."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ========== Database Model Tests ==========

    def test_user_learning_profile_creation(self):
        """Test UserLearningProfile model creation."""
        with self.app.app_context():
            profile = UserLearningProfile(
                user_name='testuser',
                current_skill_level=0.5,
                learning_style='analytical'
            )
            db.session.add(profile)
            db.session.commit()
            
            fetched = UserLearningProfile.query.filter_by(user_name='testuser').first()
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.current_skill_level, 0.5)
            self.assertEqual(fetched.learning_style, 'analytical')

    def test_problem_attempt_logging(self):
        """Test ProblemAttempt model and logging."""
        with self.app.app_context():
            attempt = ProblemAttempt(
                user_name='testuser',
                problem_id='prob_123',
                category='fractions',
                difficulty_level=1.5,
                is_correct=True,
                user_answer='3/4',
                correct_answer='3/4',
                time_taken_seconds=45.2
            )
            db.session.add(attempt)
            db.session.commit()
            
            fetched = ProblemAttempt.query.filter_by(problem_id='prob_123').first()
            self.assertIsNotNone(fetched)
            self.assertTrue(fetched.is_correct)
            self.assertEqual(fetched.category, 'fractions')

    # ========== Attempt Logger Tests ==========

    def test_attempt_logger_log_attempt(self):
        """Test AttemptLogger.log_attempt()."""
        with self.app.app_context():
            # Initialize profile first
            LearningProfileService.initialize_profile('testuser')
            
            # Log an attempt
            attempt = AttemptLogger.log_attempt(
                user_name='testuser',
                problem_id='prob_1',
                category='fractions',
                difficulty_level=1.0,
                user_answer='1/2',
                correct_answer='1/2',
                is_correct=True,
                time_taken_seconds=30.0
            )
            
            self.assertIsNotNone(attempt.id)
            self.assertTrue(attempt.is_correct)
            
            # Verify profile was updated
            profile = UserLearningProfile.query.filter_by(user_name='testuser').first()
            self.assertEqual(profile.total_problems_attempted, 1)
            self.assertEqual(profile.total_problems_correct, 1)

    def test_attempt_logger_performance_stats(self):
        """Test AttemptLogger.get_user_performance_by_category()."""
        with self.app.app_context():
            LearningProfileService.initialize_profile('testuser')
            
            # Log multiple attempts
            for i in range(10):
                is_correct = i < 7  # 70% success
                AttemptLogger.log_attempt(
                    user_name='testuser',
                    problem_id=f'prob_{i}',
                    category='fractions',
                    difficulty_level=1.0,
                    user_answer=f'answer_{i}',
                    correct_answer=f'correct_{i}',
                    is_correct=is_correct
                )
            
            stats = AttemptLogger.get_user_performance_by_category('testuser')
            
            self.assertIn('fractions', stats)
            self.assertEqual(stats['fractions']['attempts'], 10)
            self.assertEqual(stats['fractions']['correct'], 7)
            self.assertAlmostEqual(stats['fractions']['success_rate'], 0.7, places=2)

    def test_attempt_logger_recent_attempts(self):
        """Test AttemptLogger.get_recent_attempts()."""
        with self.app.app_context():
            LearningProfileService.initialize_profile('testuser')
            
            # Log attempts
            for i in range(5):
                AttemptLogger.log_attempt(
                    user_name='testuser',
                    problem_id=f'prob_{i}',
                    category='fractions',
                    difficulty_level=1.0,
                    user_answer=f'a_{i}',
                    correct_answer=f'c_{i}',
                    is_correct=True
                )
            
            recent = AttemptLogger.get_recent_attempts('testuser', limit=3)
            self.assertEqual(len(recent), 3)

    # ========== Learning Profile Service Tests ==========

    def test_learning_profile_initialization(self):
        """Test LearningProfileService.initialize_profile()."""
        with self.app.app_context():
            profile = LearningProfileService.initialize_profile('newuser', learning_style='visual')
            
            self.assertIsNotNone(profile.id)
            self.assertEqual(profile.user_name, 'newuser')
            self.assertEqual(profile.learning_style, 'visual')
            self.assertEqual(profile.current_skill_level, 0.5)

    def test_learning_profile_weak_topics(self):
        """Test LearningProfileService.get_weak_topics()."""
        with self.app.app_context():
            LearningProfileService.initialize_profile('testuser')
            
            # Log attempts with <70% success in fractions
            for i in range(10):
                AttemptLogger.log_attempt(
                    user_name='testuser',
                    problem_id=f'frac_{i}',
                    category='fractions',
                    difficulty_level=1.0,
                    user_answer=f'a_{i}',
                    correct_answer=f'c_{i}',
                    is_correct=(i < 5)  # 50% success
                )
            
            # Log attempts with >80% success in algebra
            for i in range(10):
                AttemptLogger.log_attempt(
                    user_name='testuser',
                    problem_id=f'alg_{i}',
                    category='algebra',
                    difficulty_level=1.0,
                    user_answer=f'a_{i}',
                    correct_answer=f'c_{i}',
                    is_correct=(i < 9)  # 90% success
                )
            
            weak = LearningProfileService.get_weak_topics('testuser')
            mastered = LearningProfileService.get_mastered_topics('testuser')
            
            self.assertIn('fractions', weak)
            self.assertIn('algebra', mastered)
            self.assertNotIn('fractions', mastered)

    def test_learning_profile_skill_level_update(self):
        """Test LearningProfileService.update_skill_level()."""
        with self.app.app_context():
            profile = LearningProfileService.initialize_profile('testuser')
            original_skill = profile.current_skill_level
            
            # Log attempts with high success rate
            for i in range(10):
                AttemptLogger.log_attempt(
                    user_name='testuser',
                    problem_id=f'prob_{i}',
                    category='fractions',
                    difficulty_level=1.0,
                    user_answer=f'a_{i}',
                    correct_answer=f'c_{i}',
                    is_correct=True  # 100% success
                )
            
            # Update skill level
            LearningProfileService.update_skill_level('testuser', 'fractions')
            
            updated_profile = UserLearningProfile.query.filter_by(user_name='testuser').first()
            self.assertGreater(updated_profile.current_skill_level, original_skill)

    # ========== Difficulty Engine Tests ==========

    def test_difficulty_adjustment_too_easy(self):
        """Test DifficultyEngine adjusts up when success rate > 80%."""
        with self.app.app_context():
            # Simulate 90% success (too easy)
            results = [True] * 9 + [False]  # 90% success
            
            original = 1.0
            adjusted = DifficultyEngine.adjust_difficulty(
                'testuser', 'fractions', results, original
            )
            
            # Should increase by 15%
            expected = 1.15
            self.assertAlmostEqual(adjusted, expected, places=2)

    def test_difficulty_adjustment_too_hard(self):
        """Test DifficultyEngine adjusts down when success rate < 60%."""
        with self.app.app_context():
            # Simulate 40% success (too hard)
            results = [True] * 4 + [False] * 6  # 40% success
            
            original = 1.0
            adjusted = DifficultyEngine.adjust_difficulty(
                'testuser', 'fractions', results, original
            )
            
            # Should decrease by 15%
            expected = 0.85
            self.assertAlmostEqual(adjusted, expected, places=2)

    def test_difficulty_adjustment_optimal(self):
        """Test DifficultyEngine maintains difficulty when success rate is 70-80%."""
        with self.app.app_context():
            # Simulate 75% success (optimal)
            results = [True] * 7 + [False] * 3  # 70% success
            
            original = 1.0
            adjusted = DifficultyEngine.adjust_difficulty(
                'testuser', 'fractions', results, original
            )
            
            # Should remain the same
            self.assertEqual(adjusted, original)

    def test_difficulty_clamping(self):
        """Test DifficultyEngine clamps difficulty to valid range."""
        with self.app.app_context():
            # Test minimum clamp
            results = [False] * 10  # 0% success
            adjusted = DifficultyEngine.adjust_difficulty(
                'testuser', 'fractions', results, 0.15
            )
            self.assertGreaterEqual(adjusted, DifficultyEngine.MIN_DIFFICULTY)
            
            # Test maximum clamp
            results = [True] * 10  # 100% success
            adjusted = DifficultyEngine.adjust_difficulty(
                'testuser', 'fractions', results, 4.5
            )
            self.assertLessEqual(adjusted, DifficultyEngine.MAX_DIFFICULTY)

    def test_difficulty_success_rate_calculation(self):
        """Test DifficultyEngine.get_success_rate()."""
        with self.app.app_context():
            LearningProfileService.initialize_profile('testuser')
            
            # Log attempts with known success rate
            for i in range(10):
                AttemptLogger.log_attempt(
                    user_name='testuser',
                    problem_id=f'prob_{i}',
                    category='fractions',
                    difficulty_level=1.0,
                    user_answer=f'a_{i}',
                    correct_answer=f'c_{i}',
                    is_correct=(i < 7)  # 70% success
                )
            
            success_rate = DifficultyEngine.get_success_rate('testuser', 'fractions')
            self.assertAlmostEqual(success_rate, 0.7, places=1)

    def test_recommended_difficulty_with_history(self):
        """Test DifficultyEngine gets recommended difficulty after history."""
        with self.app.app_context():
            profile = LearningProfileService.initialize_profile('testuser')
            profile.preferred_difficulty = 1.0
            db.session.commit()
            
            # Log attempts
            for i in range(10):
                AttemptLogger.log_attempt(
                    user_name='testuser',
                    problem_id=f'prob_{i}',
                    category='fractions',
                    difficulty_level=1.0,
                    user_answer=f'a_{i}',
                    correct_answer=f'c_{i}',
                    is_correct=(i < 7)  # 70% success (maintain)
                )
            
            recommended = DifficultyEngine.get_recommended_difficulty('testuser', 'fractions')
            self.assertIsNotNone(recommended)
            self.assertGreaterEqual(recommended, DifficultyEngine.MIN_DIFFICULTY)
            self.assertLessEqual(recommended, DifficultyEngine.MAX_DIFFICULTY)


if __name__ == '__main__':
    unittest.main()
