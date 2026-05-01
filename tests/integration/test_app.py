import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import time
from flask import session

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from app import app, HighscoreManager, socketio, rooms
from database import db

class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        # Room setup for multiplayer tests
        rooms['test_room'] = {
            'players': ['ExistingGamer'],
            'scores': {'ExistingGamer': 0},
            'is_started': False,
            'category': 'basic',
            'difficulty': 'easy',
            'mode': 'time',
            'mode_value': 20,
            'creator': 'ExistingGamer'
        }

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Math Game!', response.data)

    def test_index_post_with_new_defaults(self):
        """Verify that server-side defaults (Multiplayer, Percentage, Medium) are applied."""
        response = self.client.post('/', data={
            'player_name': 'DefaultTester'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/multiplayer_lobby', response.headers['Location'])
        
        with self.client.session_transaction() as sess:
            self.assertTrue(sess['multiplayer'])
            self.assertEqual(sess['category'], 'percentage')

    @patch('app.QuestionFactory')
    def test_game_route(self, mock_factory):
        mock_factory.return_value.create_question.return_value = ("What is 5 + 5?", 10, None)
        with self.client.session_transaction() as sess:
            sess['player_name'] = 'TestUser'
            sess['category'] = 'percentage'
            sess['difficulty'] = 'medium'
            sess['mode'] = 'time'
            sess['mode_value'] = 20
            sess['score'] = 0
            sess['questions_answered'] = 0
            sess['start_time'] = time.time()

        response = self.client.get('/game')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'What is 5 + 5?', response.data)

    def test_restart_route(self):
        """Verify the /restart route resets game state and redirects."""
        with self.client.session_transaction() as sess:
            sess['player_name'] = 'TestUser'
            sess['score'] = 10
            sess['questions_answered'] = 5
            sess['start_time'] = time.time() - 10

        response = self.client.get('/restart', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/game'))
        
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['score'], 0)
            self.assertEqual(sess['questions_answered'], 0)

    def test_leaderboard_route(self):
        response = self.client.get('/leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hall of Fame', response.data)

class TestLeaderboardFeatures(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.manager = HighscoreManager()
            self.manager.add_score('Charlie', 8, 'percentage', 'medium', 30, 10)
            self.manager.add_score('Alice', 10, 'percentage', 'medium', 20, 10)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_leaderboard_sorting(self):
        response = self.client.get('/leaderboard')
        # Alice (10) should appear before Charlie (8)
        self.assertLess(response.data.find(b'Alice'), response.data.find(b'Charlie'))

    def test_filter_by_category(self):
        with self.app.app_context():
            self.manager.add_score('Dave', 5, 'basic', 'easy', 15, 5)
        
        response = self.client.get('/leaderboard?filter_category=percentage')
        self.assertIn(b'Alice', response.data)
        self.assertNotIn(b'Dave', response.data)

if __name__ == '__main__':
    unittest.main()
