import unittest
import os
import sys
from datetime import datetime, timezone, timedelta

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from flask import Flask
from database import db, ProblemAttempt
from learning_analytics_service import LearningAnalyticsService

class TestAnalyticsService(unittest.TestCase):
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

    def test_get_progress_data(self):
        with self.app.app_context():
            # Seed attempts for the last 5 days
            for i in range(5):
                date = datetime.now(timezone.utc) - timedelta(days=i)
                db.session.add(ProblemAttempt(
                    user_name='testuser',
                    problem_id=f'p{i}',
                    category='math',
                    difficulty_level=1.0,
                    is_correct=(i % 2 == 0),
                    created_at=date
                ))
            db.session.commit()
            
            data = LearningAnalyticsService.get_progress_data('testuser', days=7)
            self.assertTrue(len(data) > 0)
            self.assertIn('accuracy', data[0])

if __name__ == '__main__':
    unittest.main()
