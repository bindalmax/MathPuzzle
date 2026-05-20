import unittest
import os
import sys

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from flask import Flask
from database import db, Highscore
from highscore_manager import HighscoreManager

class TestLeaderboardPagination(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        cls.manager = HighscoreManager(cls.app)
        
    def setUp(self):
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        # Seed 25 scores
        for i in range(25):
            db.session.add(Highscore(
                name=f"Player{i}",
                score=100 + i,
                category="basic" if i < 15 else "startup_challenge",
                difficulty="easy"
            ))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_pagination_count(self):
        # Page 1, 10 per page
        result = self.manager.load(page=1, per_page=10)
        self.assertEqual(len(result['scores']), 10)
        self.assertEqual(result['total_pages'], 3)
        
        # Page 3, 10 per page (last page)
        result = self.manager.load(page=3, per_page=10)
        self.assertEqual(len(result['scores']), 5)

    def test_category_filtering(self):
        # Filter for startup_challenge (10 items total)
        result = self.manager.load(category="startup_challenge", per_page=100)
        self.assertEqual(len(result['scores']), 10)
        for s in result['scores']:
            self.assertEqual(s['category'], "startup_challenge")

if __name__ == '__main__':
    unittest.main()
