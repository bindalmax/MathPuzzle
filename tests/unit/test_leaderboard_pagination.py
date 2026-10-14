import unittest
import os
import sys
import tempfile
from datetime import datetime

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from highscore_manager import HighscoreManager

class TestLeaderboardPagination(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        from database import db
        self.db = db
        self.db.init_app(self.app)

        with self.app.app_context():
            self.db.create_all()
            from database import Highscore
            # Seed 25 scores
            for i in range(25):
                self.db.session.add(Highscore(
                    name=f"Player{i}",
                    score=100 + i,
                    category="basic" if i < 15 else "startup_challenge",
                    difficulty="easy"
                ))
            self.db.session.commit()

        self.manager = HighscoreManager(self.app)
        self.manager.db = self.db

    def tearDown(self):
        with self.app.app_context():
            self.db.session.remove()
            self.db.drop_all()
    def test_pagination_count(self):
        # Page 1, 10 per page
        with self.app.app_context():
            result = self.manager.load(page=1, per_page=10)
            self.assertEqual(len(result['scores']), 10)
            self.assertEqual(result['total_pages'], 3)
            
            # Page 3, 10 per page (last page)
            result = self.manager.load(page=3, per_page=10)
            self.assertEqual(len(result['scores']), 5)

    def test_category_filtering(self):
        # Filter for startup_challenge (10 items total)
        with self.app.app_context():
            result = self.manager.load(category="startup_challenge", per_page=100)
            self.assertEqual(len(result['scores']), 10)
            for s in result['scores']:
                self.assertEqual(s['category'], "startup_challenge")

if __name__ == '__main__':
    unittest.main()
