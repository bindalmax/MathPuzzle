import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import time

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from app import app, rooms
from database import db

class TestStartupChallengeIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_startup_challenge_flow(self):
        # 1. Start Challenge
        response = self.client.post('/', data={
            'player_name': 'WebCEO',
            'game_type': 'startup_challenge'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertTrue(sess['is_startup_challenge'])
            self.assertEqual(sess['startup_value'], 10000.0)
            self.assertEqual(sess['questions_answered'], 0)

        # 2. Answer first question correctly
        with self.client.session_transaction() as sess:
            sess['current_answer'] = 100
        
        response = self.client.post('/submit_answer', data={'answer': '100'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['questions_answered'], 1)
            # 10,000 + 20% = 12,000
            self.assertEqual(sess['startup_value'], 12000.0)

        # 3. Answer second question incorrectly
        with self.client.session_transaction() as sess:
            sess['current_answer'] = 50
        
        response = self.client.post('/submit_answer', data={'answer': '0'}, follow_redirects=True)
        
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['questions_answered'], 2)
            # 12,000 - 10% = 10,800
            self.assertEqual(sess['startup_value'], 10800.0)

        # 4. Check Game Over
        response = self.client.get('/game_over')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Startup Challenge Results', response.data)
        self.assertIn(b'10,800', response.data)
        self.assertIn(b'Startup Founder', response.data)

if __name__ == '__main__':
    unittest.main()
