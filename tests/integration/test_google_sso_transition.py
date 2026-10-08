import unittest
import os
import sys
import time

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from app import app, rooms
from database import db, User, Highscore, UserLearningProfile, ProblemAttempt


class TestGoogleSSOTransition(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        os.environ['FLASK_ENV'] = 'development'
        self.client = self.app.test_client()
        rooms.clear()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        rooms.clear()

    def test_guest_highscores_migration_to_google_user(self):
        """Verify that highscores recorded by a guest are transferred to the newly authenticated user."""
        guest_name = "GuestChampion"

        with self.app.app_context():
            score1 = Highscore(
                name=guest_name,
                score=100,
                category="basic_arithmetic",
                difficulty="medium",
                time_taken=15.5,
                questions_attempted=10,
                user_id=None
            )
            score2 = Highscore(
                name=guest_name,
                score=150,
                category="algebra",
                difficulty="hard",
                time_taken=25.0,
                questions_attempted=10,
                user_id=None
            )
            db.session.add_all([score1, score2])
            db.session.commit()

        # Simulate guest session
        with self.client.session_transaction() as sess:
            sess['player_name'] = guest_name

        # Authenticate via Google SSO
        res = self.client.post('/api/auth/google', json={
            'id_token': 'mock-champion-sso',
            'guest_name': guest_name
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')
        new_name = data['data']['display_name']
        user_id = data['data']['user_id']

        # Verify DB records updated
        with self.app.app_context():
            migrated_scores = Highscore.query.filter_by(user_id=user_id).all()
            self.assertEqual(len(migrated_scores), 2)
            for s in migrated_scores:
                self.assertEqual(s.name, new_name)
                self.assertEqual(s.user_id, user_id)

    def test_guest_learning_profile_and_attempts_migration(self):
        """Verify that AI adaptive learning profile and attempt history migrate smoothly."""
        guest_name = "GuestGenius"

        with self.app.app_context():
            profile = UserLearningProfile(
                user_name=guest_name,
                current_skill_level=0.88,
                total_problems_attempted=12,
                total_problems_correct=10,
                topics_mastered=['algebra', 'percentage'],
                weak_topics=['decimal_fraction']
            )
            attempt = ProblemAttempt(
                user_name=guest_name,
                problem_id="p123",
                category="algebra",
                difficulty_level=0.88,
                is_correct=True,
                time_taken_seconds=3.2,
                problem_text="Solve 2x = 8"
            )
            db.session.add_all([profile, attempt])
            db.session.commit()

        # Sign in with Google
        res = self.client.post('/api/auth/google', json={
            'id_token': 'mock-genius-sso',
            'guest_name': guest_name
        })
        self.assertEqual(res.status_code, 200)
        new_name = res.get_json()['data']['display_name']

        with self.app.app_context():
            # Old guest profile should be updated to new name or merged
            old_p = UserLearningProfile.query.filter_by(user_name=guest_name).first()
            self.assertIsNone(old_p)

            new_p = UserLearningProfile.query.filter_by(user_name=new_name).first()
            self.assertIsNotNone(new_p)
            self.assertEqual(new_p.total_problems_attempted, 12)
            self.assertEqual(new_p.total_problems_correct, 10)
            self.assertIn('algebra', new_p.topics_mastered)

            # Attempt history should be reassigned to new name
            updated_attempt = ProblemAttempt.query.filter_by(user_name=new_name).first()
            self.assertIsNotNone(updated_attempt)
            self.assertEqual(updated_attempt.problem_id, "p123")

    def test_session_state_preserved_during_sso(self):
        """Verify active in-flight game session state (score, streak, mode) is not wiped during login."""
        with self.client.session_transaction() as sess:
            sess['player_name'] = 'GuestActive'
            sess['score'] = 77
            sess['questions_answered'] = 8
            sess['category'] = 'percentage'
            sess['difficulty'] = 'hard'
            sess['startup_value'] = 1500000

        res = self.client.post('/api/auth/google', json={
            'id_token': 'mock-active-sso'
        })
        self.assertEqual(res.status_code, 200)

        with self.client.session_transaction() as sess:
            # Active in-flight game session variables must still exist
            self.assertEqual(sess.get('score'), 77)
            self.assertEqual(sess.get('questions_answered'), 8)
            self.assertEqual(sess.get('category'), 'percentage')
            self.assertEqual(sess.get('difficulty'), 'hard')
            self.assertEqual(sess.get('startup_value'), 1500000)
            # Identity updated
            self.assertIsNotNone(sess.get('user_id'))
            self.assertEqual(sess.get('player_name'), 'Mock mock-active-sso')

    def test_multiplayer_room_player_sync(self):
        """Verify that an active multiplayer lobby room player entry is updated to the user's verified name."""
        guest_name = "GuestLobby"
        room_id = "ROOM999"
        rooms[room_id] = {
            'players': [guest_name, 'Opponent1'],
            'scores': {guest_name: 40, 'Opponent1': 20},
            'creator': guest_name,
            'is_started': False
        }

        with self.client.session_transaction() as sess:
            sess['player_name'] = guest_name
            sess['room_id'] = room_id

        res = self.client.post('/api/auth/google', json={
            'id_token': 'mock-lobby-sso'
        })
        self.assertEqual(res.status_code, 200)
        new_name = res.get_json()['data']['display_name']

        # Room should now list the authenticated name
        self.assertIn(new_name, rooms[room_id]['players'])
        self.assertNotIn(guest_name, rooms[room_id]['players'])
        self.assertEqual(rooms[room_id]['scores'][new_name], 40)
        self.assertEqual(rooms[room_id]['creator'], new_name)


if __name__ == '__main__':
    unittest.main()
