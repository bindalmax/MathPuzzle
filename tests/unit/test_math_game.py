import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from flask import Flask

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from math_game import Game
from questions import QuestionFactory
from questions.percentage import PercentageQuestion
from highscore_manager import HighscoreManager
from database import db

class TestHighscoreManager(unittest.TestCase):
    def setUp(self):
        # Create a minimal Flask app for database context
        self.app = Flask(__name__)
        # Ensure unit tests use isolated in-memory DB
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        self.manager = HighscoreManager()
        self.manager.init_app(self.app)
        
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_load_empty(self):
        self.assertEqual(self.manager.load(), [])

    def test_add_and_load_score(self):
        self.manager.add_score('Player1', 10, 'basic', 'easy', time_taken=5.0, questions_attempted=10)
        scores = self.manager.load()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]['name'], 'Player1')
        self.assertEqual(scores[0]['score'], 10)
        self.assertEqual(scores[0]['time_taken'], 5.0)

class TestQuestionFactory(unittest.TestCase):
    def test_creates_basic_arithmetic_question(self):
        from questions.basic_arithmetic import BasicArithmeticQuestion
        factory = QuestionFactory("basic", "easy")
        self.assertIsInstance(factory.question_class(), BasicArithmeticQuestion)

class TestPercentageQuestion(unittest.TestCase):
    @patch('questions.percentage.random.choice', return_value=25)
    @patch('questions.percentage.random.randint', return_value=4)
    def test_easy_percentage(self, mock_randint, mock_choice):
        question, answer, choices = PercentageQuestion().generate('easy')
        self.assertEqual(question, "What is 25% of 40? ")
        self.assertEqual(answer, 10.0)

class TestGame(unittest.TestCase):
    @patch('math_game.threading.Thread')
    @patch('builtins.input', side_effect=['15', 'quit'])
    def test_run_game_loop_quit(self, mock_input, mock_thread):
        mock_factory = MagicMock()
        mock_factory.create_question.side_effect = [("What is 10 + 5? ", 15, None), ("What is 2 + 2? ", 4, None)]
        game = Game("TestPlayer", mock_factory, mode='time', value=20)
        score = game.run()
        self.assertEqual(score, 1)

    @patch('math_game.threading.Thread')
    @patch('builtins.input', side_effect=['15', '10', '10'])
    def test_game_question_count_mode(self, mock_input, mock_thread):
        mock_factory = MagicMock()
        mock_factory.create_question.side_effect = [
            ("What is 10 + 5? ", 15, None),
            ("What is 20 - 10? ", 10, None),
            ("What is 2 * 5? ", 10, None)
        ]
        game = Game("TestPlayer", mock_factory, mode='questions', value=3)
        score = game.run()
        self.assertEqual(score, 3)

if __name__ == '__main__':
    unittest.main()
