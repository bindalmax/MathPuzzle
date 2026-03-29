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
        self.test_highscores = "test_highscores_web.json"
        self.manager = HighscoreManager(self.test_highscores)
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

    def test_multiplayer_lobby_access(self):
        with self.client.session_transaction() as sess:
            sess['player_name'] = 'TestUser'
        response = self.client.get('/multiplayer_lobby')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Multiplayer Lobby', response.data)

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

    def test_submit_answer_correct(self):
        with self.client.session_transaction() as sess:
            sess['start_time'] = time.time()
            sess['current_answer'] = 10
            sess['score'] = 0
            sess['questions_answered'] = 0
            sess['category'] = 'basic'
            sess['difficulty'] = 'easy'

        response = self.client.post('/submit_answer', data={'answer': '10'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['score'], 1)
            self.assertEqual(sess['questions_answered'], 1)

    def test_game_over(self):
        with self.client.session_transaction() as sess:
            sess['player_name'] = 'TestPlayer'
            sess['score'] = 5
            sess['start_time'] = time.time() - 10
            sess['questions_answered'] = 5
            sess['category'] = 'basic'
            sess['difficulty'] = 'easy'

        response = self.client.get('/game_over')
        self.assertEqual(response.status_code, 200)
        
        scores = self.manager.load()
        self.assertEqual(len(scores), 1)
        self.assertAlmostEqual(scores[0]['time_taken'], 10, delta=1)

class TestLeaderboardFeatures(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.test_highscores = "test_highscores_features.json"
        self.manager = HighscoreManager(self.test_highscores)
        self.patcher = patch('app.highscore_manager', self.manager)
        self.patcher.start()

        # Populate with test data
        self.manager.add_score('Charlie', 8, 'basic', 'hard', 30, 10) # 80%
        self.manager.add_score('Alice', 10, 'basic', 'easy', 20, 10) # 100%
        self.manager.add_score('Bob', 9, 'decimal', 'medium', 25, 10) # 90%
        self.manager.add_score('Dave', 5, 'basic', 'easy', 15, 10) # 50%

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.test_highscores):
            os.remove(self.test_highscores)

    def test_filter_by_category(self):
        response = self.client.get('/leaderboard?filter_category=decimal')
        self.assertIn(b'Bob', response.data)
        self.assertNotIn(b'Alice', response.data)

    def test_sort_by_score_desc(self):
        # Default sort is score desc
        response = self.client.get('/leaderboard?sort_by=score&sort_order=desc')
        names = [b'Alice', b'Bob', b'Charlie', b'Dave']
        positions = [response.data.find(n) for n in names]
        self.assertTrue(all(p != -1 for p in positions))
        self.assertEqual(positions, sorted(positions))

    def test_sort_by_name_asc(self):
        response = self.client.get('/leaderboard?sort_by=name&sort_order=asc')
        names = [b'Alice', b'Bob', b'Charlie', b'Dave']
        positions = [response.data.find(n) for n in names]
        self.assertTrue(all(p != -1 for p in positions))
        self.assertEqual(positions, sorted(positions))

    def test_sort_by_time_desc(self):
        response = self.client.get('/leaderboard?sort_by=time&sort_order=desc')
        times = [b'30.0 s', b'25.0 s', b'20.0 s', b'15.0 s']
        positions = [response.data.find(t) for t in times]
        self.assertTrue(all(p != -1 for p in positions))
        self.assertEqual(positions, sorted(positions))

if __name__ == '__main__':
    unittest.main()
