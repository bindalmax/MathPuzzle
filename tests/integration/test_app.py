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
        self.app.config['WTF_CSRF_ENABLED'] = False
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
            self.assertEqual(sess['difficulty'], 'medium')

    def test_join_room_duplicate_gamer_id(self):
        """Verify that joining a room with an existing GamerId is blocked."""
        # Pre-populate a room
        room_id = 'test-room'
        rooms[room_id] = {
            'players': ['ExistingGamer'],
            'scores': {'ExistingGamer': 0},
            'is_started': False,
            'category': 'basic',
            'difficulty': 'easy',
            'mode': 'time',
            'mode_value': 20
        }
        
        # Attempt to join with the SAME name
        response = self.client.post('/', data={
            'player_name': 'ExistingGamer',
            'join_room_id': room_id
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"is already taken in this room", response.data)
        
        # Ensure session was NOT updated with room info
        with self.client.session_transaction() as sess:
            self.assertNotIn('room_id', sess)

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

    def test_filter_by_category(self):
        response = self.client.get('/leaderboard?filter_category=percentage')
        # Verify text updated to GamerId
        self.assertIn(b'GamerId', response.data)
        self.assertIn(b'Alice', response.data)

if __name__ == '__main__':
    unittest.main()
