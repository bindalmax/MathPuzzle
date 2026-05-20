import unittest
import os
import sys
from datetime import datetime

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from flask import Flask
from database import db, ProblemAttempt, MistakePattern, UserLearningProfile
from gap_detector import GapDetector
from mistake_analyzer import MistakeAnalyzer
from problem_sequencer import ProblemSequencer
from learning_profile_service import LearningProfileService

class TestPhase2Intelligence(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_gap_detection(self):
        with self.app.app_context():
            # Seed poor performance (30% success)
            for i in range(10):
                db.session.add(ProblemAttempt(
                    user_name='testuser',
                    problem_id=f'p{i}',
                    category='fractions',
                    difficulty_level=1.0,
                    is_correct=(i < 3)
                ))
            db.session.commit()
            
            gaps = GapDetector.detect_learning_gaps('testuser', min_attempts=5)
            self.assertEqual(len(gaps), 1)
            self.assertEqual(gaps[0]['category'], 'fractions')
            self.assertGreater(gaps[0]['severity_score'], 0)

    def test_mistake_categorization(self):
        with self.app.app_context():
            # Seed a sign error
            attempt = ProblemAttempt(
                user_name='testuser',
                problem_id='m1',
                category='math',
                difficulty_level=1.0,
                is_correct=False,
                user_answer='-10',
                correct_answer='10'
            )
            db.session.add(attempt)
            db.session.commit()
            
            mistakes = MistakeAnalyzer.analyze_mistakes('testuser')
            self.assertEqual(mistakes[0]['type'], 'sign_error')

    def test_problem_sequencing(self):
        with self.app.app_context():
            # Initialize profile
            LearningProfileService.initialize_profile('testuser')
            
            # Seed some gaps
            for i in range(10):
                db.session.add(ProblemAttempt(
                    user_name='testuser',
                    problem_id=f'p{i}',
                    category='algebra',
                    difficulty_level=1.0,
                    is_correct=False
                ))
            db.session.commit()
            
            sequence = ProblemSequencer.generate_personalized_sequence('testuser', problem_count=5)
            self.assertEqual(len(sequence), 5)
            # Should prioritize algebra (weak topic)
            types = [s['type'] for s in sequence]
            self.assertIn('targeted_practice', types)

if __name__ == '__main__':
    unittest.main()
