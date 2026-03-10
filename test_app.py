import unittest
from unittest.mock import patch, MagicMock
import os
import json
import time
from app import app, HighscoreManager

class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        # Use a test highscores file
        self.test_highscores = "test_highscores_web.json"
        self.manager = HighscoreManager(self.test_highscores)
        # Patch the global highscore_manager in app
        self.patcher = patch('app.highscore_manager', self.manager)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.test_highscores):
            os.remove(self.test_highscores)

    def test_index_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Math Game!', response.data)
        self.assertIn(b'Enter your name', response.data)

    def test_index_post_valid(self):
        response = self.client.post('/', data={
            'player_name': 'TestPlayer',
            'category': 'basic',
            'difficulty': 'easy'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Math Game', response.data)  # Should be on game page

    def test_game_without_session(self):
        response = self.client.get('/game', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Math Game!', response.data)  # Redirects to index

    @patch('app.QuestionFactory')
    def test_game_with_session(self, mock_factory):
        mock_question = MagicMock()
        mock_question.generate.return_value = ("What is 2 + 2? ", 4)
        mock_factory.return_value.create_question.return_value = ("What is 2 + 2? ", 4)

        with self.client:
            # Simulate session
            with self.client.session_transaction() as sess:
                sess['player_name'] = 'TestPlayer'
                sess['category'] = 'basic'
                sess['difficulty'] = 'easy'
                sess['score'] = 0
                sess['start_time'] = time.time() - 5  # 5 seconds ago
                sess['current_answer'] = 4

            response = self.client.get('/game')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'What is 2 + 2?', response.data)

    def test_submit_answer_correct(self):
        with self.client:
            with self.client.session_transaction() as sess:
                sess['player_name'] = 'TestPlayer'
                sess['category'] = 'basic'
                sess['difficulty'] = 'easy'
                sess['score'] = 0
                sess['start_time'] = time.time() - 5
                sess['current_answer'] = 4

            response = self.client.post('/submit_answer', data={'answer': '4'}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # Check if score increased, but since it's redirect, hard to check

    def test_game_over(self):
        with self.client:
            with self.client.session_transaction() as sess:
                sess['player_name'] = 'TestPlayer'
                sess['score'] = 5
                sess['start_time'] = 1234567890

            response = self.client.get('/game_over')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Your final score is: <strong>5</strong>', response.data)

    def test_leaderboard(self):
        # Add some test scores
        self.manager.add_score('Player1', 10)
        self.manager.add_score('Player2', 8)

        response = self.client.get('/leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Player1', response.data)
        self.assertIn(b'10', response.data)

    def test_quit(self):
        response = self.client.get('/quit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Game Quit', response.data)

if __name__ == '__main__':
    unittest.main()
