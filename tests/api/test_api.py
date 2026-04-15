import unittest
import requests
import threading
import time
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app, socketio

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Disable CSRF for API testing
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            from database import db
            db.create_all()

        # Run the Flask app in a separate thread
        cls.port = 5006  # Use a different port than default to avoid collisions
        cls.base_url = f'http://localhost:{cls.port}/api'
        
        cls.server_thread = threading.Thread(
            target=socketio.run, 
            args=(app,), 
            kwargs={'port': cls.port, 'debug': False, 'allow_unsafe_werkzeug': True}
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Wait for server to start
        time.sleep(2)

    def test_1_get_categories(self):
        response = requests.get(f'{self.base_url}/categories')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('basic_arithmetic', data['data']['categories'])

    def test_2_get_difficulties(self):
        response = requests.get(f'{self.base_url}/difficulties')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('easy', data['data']['difficulties'])

    def test_3_post_question_valid(self):
        payload = {'category': 'basic_arithmetic', 'difficulty': 'easy'}
        response = requests.post(f'{self.base_url}/question', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('question', data['data'])
        self.assertIn('question_id', data['data'])

    def test_4_post_question_invalid_category(self):
        payload = {'category': 'invalid', 'difficulty': 'easy'}
        response = requests.post(f'{self.base_url}/question', json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['code'], 'INVALID_CATEGORY')

    def test_5_post_question_missing_params(self):
        response = requests.post(f'{self.base_url}/question', json={})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['code'], 'INVALID_REQUEST')

    def test_6_post_answer_not_found(self):
        payload = {'question_id': 'invalid-id', 'answer': '5'}
        response = requests.post(f'{self.base_url}/answer', json=payload)
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['code'], 'QUESTION_NOT_FOUND')

    def test_7_post_score(self):
        payload = {
            'player_name': 'TestPlayer',
            'score': 100,
            'category': 'basic_arithmetic',
            'difficulty': 'easy',
            'time_taken': 45.5,
            'questions_attempted': 10
        }
        response = requests.post(f'{self.base_url}/score', json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('rank', data['data'])

    def test_8_get_leaderboard(self):
        response = requests.get(f'{self.base_url}/leaderboard')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(len(data['data']['leaderboard']) > 0)

    def test_9_get_leaderboard_filtered(self):
        params = {'category': 'basic_arithmetic', 'difficulty': 'easy', 'limit': 10}
        response = requests.get(f'{self.base_url}/leaderboard', params=params)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['limit'], 10)

    def test_10_post_multiplayer_create(self):
        payload = {
            'player_name': 'Player1',
            'category': 'basic_arithmetic',
            'difficulty': 'easy',
            'mode': 'time',
            'mode_value': 20
        }
        response = requests.post(f'{self.base_url}/multiplayer/create', json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('room_id', data['data'])

if __name__ == '__main__':
    unittest.main()
