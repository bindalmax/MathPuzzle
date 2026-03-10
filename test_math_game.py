import unittest
import os
from unittest.mock import patch, MagicMock
from fractions import Fraction

from math_game import HighscoreManager, Game
from questions import QuestionFactory
from questions.basic_arithmetic import BasicArithmeticQuestion
from questions.decimal_fraction import DecimalFractionQuestion
from questions.percentage import PercentageQuestion
from questions.profit_loss import ProfitLossQuestion
from questions.algebra import AlgebraQuestion

class TestHighscoreManager(unittest.TestCase):
    # ... (omitted for brevity, no changes)
    def setUp(self):
        self.test_file = "test_highscores.json"
        self.manager = HighscoreManager(filename=self.test_file)
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    def test_load_no_file(self):
        self.assertEqual(self.manager.load(), [])
    def test_save_and_load(self):
        scores = [{'name': 'Player1', 'score': 10}]
        self.manager.save(scores)
        self.assertEqual(self.manager.load(), scores)
    def test_add_score(self):
        self.manager.add_score('Player1', 10)
        scores = self.manager.load()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]['name'], 'Player1')
        self.assertEqual(scores[0]['score'], 10)

class TestQuestionFactory(unittest.TestCase):
    def test_creates_basic_arithmetic_question(self):
        factory = QuestionFactory("basic", "easy")
        self.assertIsInstance(factory.question_class(), BasicArithmeticQuestion)

    def test_invalid_category_raises_error(self):
        factory = QuestionFactory("invalid", "easy")
        with self.assertRaises(ValueError):
            factory.create_question()

class TestBasicArithmeticQuestion(unittest.TestCase):
    @patch('questions.basic_arithmetic.random.choice', return_value='+')
    @patch('questions.basic_arithmetic.random.randint', side_effect=[10, 5])
    def test_addition(self, mock_randint, mock_choice):
        question, answer = BasicArithmeticQuestion().generate('easy')
        self.assertEqual(question, "What is 10 + 5? ")
        self.assertEqual(answer, 15)

class TestDecimalFractionQuestion(unittest.TestCase):
    @patch('questions.decimal_fraction.random.choice', side_effect=['decimal', '+'])
    @patch('questions.decimal_fraction.random.uniform', side_effect=[2.5, 3.5])
    def test_decimal_addition(self, mock_uniform, mock_choice):
        question, answer = DecimalFractionQuestion().generate('easy')
        self.assertEqual(question, "What is 2.5 + 3.5? ")
        self.assertEqual(answer, 6.0)

class TestPercentageQuestion(unittest.TestCase):
    @patch('questions.percentage.random.choice', return_value=25)
    @patch('questions.percentage.random.randint', return_value=4)
    def test_easy_percentage(self, mock_randint, mock_choice):
        question, answer = PercentageQuestion().generate('easy')
        self.assertEqual(question, "What is 25% of 40? ")
        self.assertEqual(answer, 10.0)

class TestAlgebraQuestion(unittest.TestCase):
    @patch('questions.algebra.random.randint', side_effect=[5, 8])
    def test_easy_algebra(self, mock_randint):
        question, answer = AlgebraQuestion().generate('easy')
        self.assertEqual(question, "Solve for x: x + 8 = 13")
        self.assertEqual(answer, 5)

class TestProfitLossQuestion(unittest.TestCase):
    @patch('questions.profit_loss.random.randint', side_effect=[50, 60])
    def test_profit_question(self, mock_randint):
        question, answer = ProfitLossQuestion().generate('easy')
        self.assertEqual(question, "A toy is bought for $50 and sold for $60. What is the profit? ")
        self.assertEqual(answer, 10)

    @patch('questions.profit_loss.random.randint', side_effect=[50, 40])
    def test_loss_question(self, mock_randint):
        question, answer = ProfitLossQuestion().generate('easy')
        self.assertEqual(question, "A toy is bought for $50 and sold for $40. What is the loss? ")
        self.assertEqual(answer, 10)

class TestGame(unittest.TestCase):
    def setUp(self):
        self.mock_highscore_manager = MagicMock()

    @patch('math_game.threading.Thread')
    @patch('builtins.input', side_effect=['15', 'quit'])
    def test_run_game_loop_quit(self, mock_input, mock_thread):
        mock_factory = MagicMock()
        mock_factory.create_question.side_effect = [("What is 10 + 5? ", 15), ("What is 2 + 2? ", 4)]
        game = Game("TestPlayer", mock_factory, self.mock_highscore_manager)
        score = game.run()
        self.assertEqual(score, 1)
        self.assertEqual(mock_input.call_count, 2)
        self.assertEqual(mock_factory.create_question.call_count, 2)

    @patch('math_game.os._exit')
    @patch('math_game.threading.Thread')
    @patch('builtins.input')
    def test_game_ends_after_timer(self, mock_input, mock_thread, mock_exit):
        mock_factory = MagicMock()
        mock_factory.create_question.return_value = ("What is 10 + 5? ", 15)
        
        game = Game("TestPlayer", mock_factory, self.mock_highscore_manager, duration=20)
        
        def input_side_effect(*args):
            if mock_input.call_count == 1:
                return '15'
            elif mock_input.call_count == 2:
                game.game_over.set()
                return '15'
            return '15'
        
        mock_input.side_effect = input_side_effect

        score = game.run()
        self.assertEqual(score, 1)
        self.assertEqual(mock_input.call_count, 2)
        # Ensure os._exit is not called during the test run
        mock_exit.assert_not_called()

if __name__ == '__main__':
    unittest.main()
