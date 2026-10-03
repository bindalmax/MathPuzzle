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
        self.assertIn(b'Master Math, Challenge Friends', response.data)

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

    def test_session_permanent_configuration(self):
        """Verify that session is marked permanent and configuration is properly set."""
        self.assertIsNone(self.app.config.get('WTF_CSRF_TIME_LIMIT'))
        self.assertIsNotNone(self.app.config.get('PERMANENT_SESSION_LIFETIME'))
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertTrue(sess.permanent)

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

    def test_privacy_route(self):
        response = self.client.get('/privacy')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Privacy Policy', response.data)
        self.assertIn(b'Google AdSense', response.data)

    def test_multiplayer_independent_progression(self):
        """Verify that two players in the same room solve the shared pool independently without skipping."""
        room_id = 'test_sync_room'
        pool = [
            ("Q0: What is 5 + 5?", 10.0, [10.0, 20.0, 30.0, 40.0]),
            ("Q1: What is 6 + 6?", 12.0, [12.0, 22.0, 32.0, 42.0]),
            ("Q2: What is 7 + 7?", 14.0, [14.0, 24.0, 34.0, 44.0])
        ]
        rooms[room_id] = {
            'players': ['PlayerA', 'PlayerB'],
            'scores': {'PlayerA': 0, 'PlayerB': 0},
            'is_started': True,
            'category': 'basic',
            'difficulty': 'easy',
            'mode': 'questions',
            'mode_value': 3,
            'creator': 'PlayerA',
            'question_pool': pool,
            'player_progress': {'PlayerA': 0, 'PlayerB': 0}
        }

        client_a = self.app.test_client()
        with client_a.session_transaction() as sess:
            sess['player_name'] = 'PlayerA'
            sess['multiplayer'] = True
            sess['room_id'] = room_id
            sess['question_index'] = 0
            sess['score'] = 0
            sess['questions_answered'] = 0
            sess['start_time'] = time.time()
            sess['mode'] = 'questions'
            sess['mode_value'] = 3

        client_b = self.app.test_client()
        with client_b.session_transaction() as sess:
            sess['player_name'] = 'PlayerB'
            sess['multiplayer'] = True
            sess['room_id'] = room_id
            sess['question_index'] = 0
            sess['score'] = 0
            sess['questions_answered'] = 0
            sess['start_time'] = time.time()
            sess['mode'] = 'questions'
            sess['mode_value'] = 3

        # Both players load /game -> both receive Q0
        resp_a0 = client_a.get('/game')
        self.assertIn(b'Q0: What is 5 + 5?', resp_a0.data)
        resp_b0 = client_b.get('/game')
        self.assertIn(b'Q0: What is 5 + 5?', resp_b0.data)

        # Player A answers Q0 correctly
        client_a.post('/submit_answer', data={'answer': '10.0'})
        
        # Player A is now on Q1
        resp_a1 = client_a.get('/game')
        self.assertIn(b'Q1: What is 6 + 6?', resp_a1.data)

        # CRITICAL TEST: Player B is still on Q0! Player A's answer did NOT advance/skip Player B's question!
        resp_b_still0 = client_b.get('/game')
        self.assertIn(b'Q0: What is 5 + 5?', resp_b_still0.data)

        # Player B answers Q0 correctly
        client_b.post('/submit_answer', data={'answer': '10.0'})

        # Now Player B is on Q1
        resp_b1 = client_b.get('/game')
        self.assertIn(b'Q1: What is 6 + 6?', resp_b1.data)

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
