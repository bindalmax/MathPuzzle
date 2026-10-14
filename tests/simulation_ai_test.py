import unittest
import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from flask import Flask
from database import db, ProblemAttempt, UserLearningProfile
from src.attempt_logger import AttemptLogger
from src.difficulty_engine import DifficultyEngine
from src.learning_profile_service import LearningProfileService

class TestAISimulation(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
            LearningProfileService.initialize_profile("SimUser")

    def test_adaptive_cycle(self):
        with self.app.app_context():
            print("\n--- Starting Adaptive Learning Simulation ---")
            category = "percentage"
            
            # Simulate 10 games, failing the first 5 and succeeding the last 5
            for i in range(10):
                is_correct = (i >= 5)
                
                # Get current recommended difficulty
                current_diff = DifficultyEngine.get_recommended_difficulty("SimUser", category)
                
                # Log attempt
                AttemptLogger.log_attempt(
                    user_name="SimUser",
                    problem_id=f"sim_{i}",
                    category=category,
                    difficulty_level=current_diff,
                    user_answer="wrong" if not is_correct else "right",
                    correct_answer="right",
                    is_correct=is_correct
                )
                
                # Trigger profile update
                LearningProfileService.update_skill_level("SimUser", category)
                
                # Print stats
                profile = LearningProfileService.get_or_create_profile("SimUser")
                print(f"Game {i+1}: Result={'PASS' if is_correct else 'FAIL'}, "
                      f"Difficulty Level={current_diff}, "
                      f"Skill={profile.current_skill_level:.3f}")

            # Final verification
            final_stats = DifficultyEngine.get_difficulty_stats("SimUser")
            print("\n--- Final Stats ---")
            print(final_stats)
            self.assertIn(category, final_stats)
            print("--- Simulation Complete ---\n")

if __name__ == '__main__':
    unittest.main()
