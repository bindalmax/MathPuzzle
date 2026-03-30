import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from math_game import HighscoreManager, Game
from questions import QuestionFactory
from questions.basic_arithmetic import BasicArithmeticQuestion
from questions.decimal_fraction import DecimalFractionQuestion
from questions.percentage import PercentageQuestion
from questions.profit_loss import ProfitLossQuestion
from questions.algebra import AlgebraQuestion

class TestHighscoreManager(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_highscores.json"
        self.manager = HighscoreManager(filename=self.test_file)
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    def test_load_no_file(self):
        self.assertEqual(self.manager.load(), [])
    def test_add_score_with_details(self):
        self.manager.add_score('Player2', 20, 'decimal', 'medium', time_taken=15.5, questions_attempted=25)
        scores = self.manager.load()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]['name'], 'Player2')
        self.assertEqual(scores[0]['score'], 20)

class TestQuestionFactory(unittest.TestCase):
    def test_creates_basic_arithmetic_question(self):
        factory = QuestionFactory("basic", "easy")
        self.assertIsInstance(factory.question_class(), BasicArithmeticQuestion)

class TestPercentageQuestion(unittest.TestCase):
    @patch('questions.percentage.random.choice', return_value=25)
    @patch('questions.percentage.random.randint', return_value=4)
    def test_easy_percentage(self, mock_randint, mock_choice):
        question, answer, choices = PercentageQuestion().generate('easy')
        self.assertEqual(question, "What is 25% of 40? ")
        self.assertEqual(answer, 10.0)

    @patch('questions.percentage.random.choice', side_effect=['percentage_of', 25, 1, 1, 1])
    @patch('questions.percentage.random.randint', side_effect=[10, 1, 2, 3])
    def test_medium_percentage_of(self, mock_randint, mock_choice):
        question, answer, choices = PercentageQuestion().generate('medium')
        self.assertIn("What is 25% of", question)
        self.assertIsInstance(choices, list)

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
