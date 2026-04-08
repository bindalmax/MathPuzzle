import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from flask import Flask
from fractions import Fraction # Import Fraction for DecimalFractionQuestion tests

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from math_game import Game
from questions import QuestionFactory
from questions.basic_arithmetic import BasicArithmeticQuestion
from questions.decimal_fraction import DecimalFractionQuestion
from questions.percentage import PercentageQuestion
from questions.profit_loss import ProfitLossQuestion
from questions.algebra import AlgebraQuestion
from highscore_manager import HighscoreManager
from database import db

class TestHighscoreManager(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
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
        factory = QuestionFactory("basic", "easy")
        self.assertIsInstance(factory.question_class(), BasicArithmeticQuestion)

    def test_invalid_category_raises_error(self):
        factory = QuestionFactory("invalid", "easy")
        with self.assertRaises(ValueError):
            factory.create_question()

# --- Question Type Tests (now all return choices) ---
class TestBasicArithmeticQuestion(unittest.TestCase):
    @patch('questions.basic_arithmetic.random.choice', side_effect=['+', 1, 2, 3]) # Mock random.choice for operator and generate_choices
    @patch('questions.basic_arithmetic.random.randint', side_effect=[10, 5, 1, 2, 3]) # Mock random.randint for numbers and generate_choices
    def test_easy_addition_with_choices(self, mock_randint, mock_choice):
        question, answer, choices = BasicArithmeticQuestion().generate('easy')
        self.assertEqual(question, "What is 10 + 5? ")
        self.assertEqual(answer, 15)
        self.assertIsInstance(choices, list)
        self.assertEqual(len(choices), 4)
        self.assertIn(answer, choices)

class TestDecimalFractionQuestion(unittest.TestCase):
    @patch('questions.decimal_fraction.random.choice', side_effect=['decimal', '+', Fraction(1,2), Fraction(1,4), 1, 2, 3])
    @patch('questions.decimal_fraction.random.uniform', side_effect=[2.5, 3.5, 0.1, 0.2, 0.3])
    def test_easy_decimal_addition_with_choices(self, mock_uniform, mock_choice):
        question, answer, choices = DecimalFractionQuestion().generate('easy')
        self.assertEqual(question, "What is 2.5 + 3.5? ")
        self.assertEqual(answer, 6.0)
        self.assertIsInstance(choices, list)
        self.assertEqual(len(choices), 4)
        self.assertIn(answer, choices)

class TestPercentageQuestion(unittest.TestCase):
    @patch('questions.percentage.random.choice', side_effect=[25, 1, 2, 3]) # Mock random.choice for percent and generate_choices
    @patch('questions.percentage.random.randint', side_effect=[4, 10, 1, 2, 3]) # Mock random.randint for number and generate_choices
    def test_easy_percentage_with_choices(self, mock_randint, mock_choice):
        question, answer, choices = PercentageQuestion().generate('easy')
        self.assertEqual(question, "What is 25% of 40? ")
        self.assertEqual(answer, 10.0)
        self.assertIsInstance(choices, list)
        self.assertEqual(len(choices), 4)
        self.assertIn(answer, choices)

class TestProfitLossQuestion(unittest.TestCase):
    @patch('questions.profit_loss.random.randint', side_effect=[50, 60, 1, 2, 3]) # Mock for prices and generate_choices
    def test_easy_profit_with_choices(self, mock_randint):
        question, answer, choices = ProfitLossQuestion().generate('easy')
        self.assertEqual(question, "A toy is bought for $50 and sold for $60. What is the profit? ")
        self.assertEqual(answer, 10)
        self.assertIsInstance(choices, list)
        self.assertEqual(len(choices), 4)
        self.assertIn(answer, choices)

class TestAlgebraQuestion(unittest.TestCase):
    @patch('questions.algebra.random.randint', side_effect=[5, 8, 1, 2, 3]) # Mock for x, a, and generate_choices
    def test_easy_algebra_with_choices(self, mock_randint):
        question, answer, choices = AlgebraQuestion().generate('easy')
        self.assertEqual(question, "Solve for x: x + 8 = 13")
        self.assertEqual(answer, 5)
        self.assertIsInstance(choices, list)
        self.assertEqual(len(choices), 4)
        self.assertIn(answer, choices)

# --- Game Class Tests (now expects choices) ---
class TestGame(unittest.TestCase):
    @patch('math_game.threading.Thread')
    @patch('builtins.input', side_effect=['15', 'quit'])
    def test_run_game_loop_quit(self, mock_input, mock_thread):
        mock_factory = MagicMock()
        # Mock create_question to return choices
        mock_factory.create_question.side_effect = [("What is 10 + 5? ", 15, [10, 15, 20, 5]), ("What is 2 + 2? ", 4, [2, 4, 6, 8])]
        game = Game("TestPlayer", mock_factory, mode='time', value=20)
        score = game.run()
        self.assertEqual(score, 1)

    @patch('math_game.threading.Thread')
    @patch('builtins.input', side_effect=['15', '10', '10'])
    def test_game_question_count_mode(self, mock_input, mock_thread):
        mock_factory = MagicMock()
        # Mock create_question to return choices
        mock_factory.create_question.side_effect = [
            ("What is 10 + 5? ", 15, [10, 15, 20, 5]),
            ("What is 20 - 10? ", 10, [5, 10, 15, 20]),
            ("What is 2 * 5? ", 10, [5, 10, 15, 20])
        ]
        game = Game("TestPlayer", mock_factory, mode='questions', value=3)
        score = game.run()
        self.assertEqual(score, 3)

if __name__ == '__main__':
    unittest.main()
