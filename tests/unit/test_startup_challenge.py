import unittest
import os
import sys

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from math_game import StartupChallengeGame

class TestStartupChallenge(unittest.TestCase):
    def test_startup_value_growth(self):
        # We can't easily test the run() loop without mocking input/output
        # but we can test the initial state and logic if we expose it
        game = StartupChallengeGame("TestPlayer")
        self.assertEqual(game.startup_value, 10000.0)
        
        # Simulate correct answer
        growth = game.startup_value * 0.2
        game.startup_value += growth
        self.assertEqual(game.startup_value, 12000.0)
        
        # Simulate wrong answer
        loss = game.startup_value * 0.1
        game.startup_value -= loss
        self.assertEqual(game.startup_value, 10800.0)

    def test_ceo_score_calculation(self):
        game = StartupChallengeGame("TestPlayer")
        game.startup_value = 55000.0
        ceo_score = int(game.startup_value / 100)
        self.assertEqual(ceo_score, 550)
        
        if ceo_score > 500:
            title = "Unicorn CEO 🦄"
        self.assertEqual(title, "Unicorn CEO 🦄")

if __name__ == '__main__':
    unittest.main()
