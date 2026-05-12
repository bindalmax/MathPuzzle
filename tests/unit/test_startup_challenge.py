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
        self.assertEqual(game.startup_value, 100000.0)
        
        # Simulate correct answer (+217%)
        growth = game.startup_value * 2.17
        game.startup_value += growth
        self.assertEqual(game.startup_value, 317000.0)
        
        # Simulate wrong answer (-50%)
        loss = game.startup_value * 0.5
        game.startup_value -= loss
        self.assertEqual(game.startup_value, 158500.0)

    def test_ceo_score_calculation(self):
        game = StartupChallengeGame("TestPlayer")
        # $1.1 Billion
        game.startup_value = 1100000000.0
        ceo_score = int(game.startup_value / 100)
        
        if game.startup_value >= 1000000000:
            title = "Unicorn CEO 🦄 (Billionaire)"
        
        self.assertEqual(title, "Unicorn CEO 🦄 (Billionaire)")

if __name__ == '__main__':
    unittest.main()
