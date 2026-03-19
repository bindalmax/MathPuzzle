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
        mock_question.generate.return_value = ("What is 2 + 2? ", 4, None)
        mock_factory.return_value.create_question.return_value = ("What is 2 + 2? ", 4, None)

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
                sess['start_time'] = time.time() - 10
                sess['questions_answered'] = 5
                sess['category'] = 'basic'
                sess['difficulty'] = 'easy'

            response = self.client.get('/game_over')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Your final score is: <strong>5</strong>', response.data)
            
            # Check if score is saved with details
            scores = self.manager.load()
            self.assertEqual(len(scores), 1)
            self.assertEqual(scores[0]['score'], 5)
            self.assertAlmostEqual(scores[0]['time_taken'], 10, delta=1)
            self.assertEqual(scores[0]['questions_attempted'], 5)

    def test_leaderboard(self):
        # Add some test scores with details
        self.manager.add_score('Player1', 10, 'basic', 'easy', time_taken=20.5, questions_attempted=10)
        
        response = self.client.get('/leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Player1', response.data)
        self.assertIn(b'100.0%', response.data) # 10/10 = 100%
        self.assertIn(b'20.5 s', response.data)

    def test_quit(self):
        response = self.client.get('/quit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Game Quit', response.data)

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
        self.assertNotIn(b'Charlie', response.data)

    def test_filter_by_difficulty(self):
        response = self.client.get('/leaderboard?filter_difficulty=hard')
        self.assertIn(b'Charlie', response.data)
        self.assertNotIn(b'Alice', response.data)
        self.assertNotIn(b'Bob', response.data)

    def test_filter_combined(self):
        response = self.client.get('/leaderboard?filter_category=basic&filter_difficulty=easy')
        # Expect Alice and Dave
        self.assertIn(b'Alice', response.data)
        self.assertIn(b'Dave', response.data)
        self.assertNotIn(b'Bob', response.data)
        self.assertNotIn(b'Charlie', response.data)

    def test_sort_by_name_asc(self):
        response = self.client.get('/leaderboard?sort_by=name&sort_order=asc')
        names = [b'Alice', b'Bob', b'Charlie', b'Dave']
        positions = [response.data.find(n) for n in names]
        self.assertTrue(all(p != -1 for p in positions))
        self.assertEqual(positions, sorted(positions))

    def test_sort_by_time_desc(self):
        response = self.client.get('/leaderboard?sort_by=time&sort_order=desc')
        # Expected order: Charlie (30s), Bob (25s), Alice (20s), Dave (15s)
        times = [b'30.0 s', b'25.0 s', b'20.0 s', b'15.0 s']
        positions = [response.data.find(t) for t in times]
        self.assertTrue(all(p != -1 for p in positions))
        self.assertEqual(positions, sorted(positions))

    def test_sort_by_score_default(self):
        # Default sort should be by score desc (or percentage desc)
        response = self.client.get('/leaderboard')
        # Order: Alice (100%), Bob (90%), Charlie (80%), Dave (50%)
        names = [b'Alice', b'Bob', b'Charlie', b'Dave']
        positions = [response.data.find(n) for n in names]
        self.assertTrue(all(p != -1 for p in positions))
        self.assertEqual(positions, sorted(positions))

    def test_sort_by_score_asc(self):
        response = self.client.get('/leaderboard?sort_by=score&sort_order=asc')
        # Order: Dave (50%), Charlie (80%), Bob (90%), Alice (100%)
        names = [b'Dave', b'Charlie', b'Bob', b'Alice']
        positions = [response.data.find(n) for n in names]
        self.assertTrue(all(p != -1 for p in positions))
        self.assertEqual(positions, sorted(positions))

if __name__ == '__main__':
    unittest.main()
