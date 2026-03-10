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

    @patch('questions.decimal_fraction.random.choice', side_effect=['decimal', '*'])
    @patch('questions.decimal_fraction.random.uniform', side_effect=[10.0, 5.0])
    def test_medium_decimal_multiplication(self, mock_uniform, mock_choice):
        question, answer = DecimalFractionQuestion().generate('medium')
        self.assertIn("What is 10.0 * 5.0?", question)
        self.assertEqual(answer, 50.0)

class TestPercentageQuestion(unittest.TestCase):
    @patch('questions.percentage.random.choice', return_value=25)
    @patch('questions.percentage.random.randint', return_value=4)
    def test_easy_percentage(self, mock_randint, mock_choice):
        question, answer = PercentageQuestion().generate('easy')
        self.assertEqual(question, "What is 25% of 40? ")
        self.assertEqual(answer, 10.0)

    @patch('questions.percentage.random.choice', side_effect=['percentage_of', 25])
    @patch('questions.percentage.random.randint', return_value=10)
    def test_medium_percentage_of(self, mock_randint, mock_choice):
        question, answer = PercentageQuestion().generate('medium')
        self.assertIn("What is 25% of", question)
        self.assertIsInstance(answer, float)

    @patch('questions.percentage.random.choice', side_effect=['increase_decrease', 20, True])
    @patch('questions.percentage.random.randint', return_value=100)
    def test_hard_percentage_increase(self, mock_randint, mock_choice):
        question, answer = PercentageQuestion().generate('hard')
        self.assertIn("increased by 20%", question)
        self.assertEqual(answer, 120.0)

class TestAlgebraQuestion(unittest.TestCase):
    @patch('questions.algebra.random.randint', side_effect=[5, 8])
    def test_easy_algebra(self, mock_randint):
        question, answer = AlgebraQuestion().generate('easy')
        self.assertEqual(question, "Solve for x: x + 8 = 13")
        self.assertEqual(answer, 5)

    @patch('questions.algebra.random.choice', return_value='multiplication')
    @patch('questions.algebra.random.randint', side_effect=[3, 4])
    def test_medium_algebra_multiplication(self, mock_randint, mock_choice):
        question, answer = AlgebraQuestion().generate('medium')
        self.assertEqual(question, "Solve for x: 4x = 12")
        self.assertEqual(answer, 3)

class TestGame(unittest.TestCase):
    def setUp(self):
        self.mock_highscore_manager = MagicMock()

    @patch('math_game.threading.Thread')
    @patch('builtins.input', side_effect=['15', 'quit'])
    def test_run_game_loop_quit(self, mock_input, mock_thread):
        mock_factory = MagicMock()
        mock_factory.create_question.side_effect = [("What is 10 + 5? ", 15), ("What is 2 + 2? ", 4)]
        game = Game("TestPlayer", mock_factory)
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
        
        game = Game("TestPlayer", mock_factory, duration=20)

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

    @patch('questions.profit_loss.random.randint', side_effect=[200, 300])
    def test_medium_profit_percentage(self, mock_randint):
        question, answer = ProfitLossQuestion().generate('medium')
        self.assertIn("What is the profit percentage?", question)
        self.assertIsInstance(answer, float)

    @patch('questions.profit_loss.random.choice', side_effect=['discount', 20])
    @patch('questions.profit_loss.random.randint', return_value=1000)
    def test_hard_discount(self, mock_randint, mock_choice):
        question, answer = ProfitLossQuestion().generate('hard')
        self.assertIn("After a 20% discount", question)
        self.assertIsInstance(answer, float)

if __name__ == '__main__':
    unittest.main()
