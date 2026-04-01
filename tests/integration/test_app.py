import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import time

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app, HighscoreManager, socketio, rooms
from database import db

class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        # Force in-memory database for integration tests to ensure isolation from Postgres/Local DB
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        # Ensure a clean state for each test
        with self.app.app_context():
            db.create_all()
        rooms.clear()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Math Game!', response.data)

    def test_index_post_single_player(self):
        response = self.client.post('/', data={
            'player_name': 'TestPlayer',
            'category': 'basic',
            'difficulty': 'easy',
            'mode': 'time',
            'mode_value': '20',
            'game_type': 'single'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Math Game', response.data)

    def test_index_post_multiplayer(self):
        response = self.client.post('/', data={
            'player_name': 'MultiPlayer',
            'category': 'basic',
            'difficulty': 'easy',
            'mode': 'time',
            'mode_value': '20',
            'game_type': 'multiplayer'
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/multiplayer_lobby', response.headers['Location'])
        
        with self.client.session_transaction() as sess:
            self.assertTrue(sess['multiplayer'])
            self.assertEqual(len(sess['room_id']), 8)

    @patch('app.QuestionFactory')
    def test_game_route(self, mock_factory):
        mock_factory.return_value.create_question.return_value = ("What is 5 + 5?", 10, None)
        with self.client.session_transaction() as sess:
            sess['player_name'] = 'TestUser'
            sess['category'] = 'basic'
            sess['difficulty'] = 'easy'
            sess['mode'] = 'time'
            sess['mode_value'] = 20
            sess['score'] = 0
            sess['questions_answered'] = 0
            sess['start_time'] = time.time()

        response = self.client.get('/game')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'What is 5 + 5?', response.data)

class TestLeaderboardFeatures(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # Initialize manager logic
            self.manager = HighscoreManager()
            # Populate with test data
            self.manager.add_score('Charlie', 8, 'basic', 'hard', 30, 10)
            self.manager.add_score('Alice', 10, 'basic', 'easy', 20, 10)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_filter_by_category(self):
        response = self.client.get('/leaderboard?filter_category=basic')
        self.assertIn(b'Alice', response.data)
        self.assertIn(b'Charlie', response.data)

if __name__ == '__main__':
    unittest.main()
