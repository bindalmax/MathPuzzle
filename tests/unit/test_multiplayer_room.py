import unittest
import time
import os
import sys

# Add project root and src to path for imports
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from room_storage import rooms

class TestMultiplayerRoomLogic(unittest.TestCase):
    def setUp(self):
        rooms.clear()

    def test_room_initialization_with_player_progress(self):
        room_id = 'test1234'
        rooms[room_id] = {
            'players': ['Player1'],
            'scores': {'Player1': 0},
            'active_connections': set(),
            'category': 'basic',
            'difficulty': 'easy',
            'mode': 'questions',
            'mode_value': 10,
            'is_started': False,
            'results': {},
            'creator': 'Player1',
            'question_pool': [
                ("Question 1", 10, [10, 20, 30, 40]),
                ("Question 2", 20, [10, 20, 30, 40]),
                ("Question 3", 30, [10, 20, 30, 40])
            ],
            'player_progress': {'Player1': 0},
            'last_activity': time.time()
        }

        # Player 2 joins
        rooms[room_id]['players'].append('Player2')
        rooms[room_id]['scores']['Player2'] = 0
        rooms[room_id]['player_progress']['Player2'] = 0

        self.assertEqual(len(rooms[room_id]['players']), 2)
        self.assertEqual(rooms[room_id]['player_progress']['Player1'], 0)
        self.assertEqual(rooms[room_id]['player_progress']['Player2'], 0)

    def test_independent_question_progression_in_pool(self):
        room_id = 'race123'
        pool = [
            ("Q0: What is 1+1?", 2, [1, 2, 3, 4]),
            ("Q1: What is 2+2?", 4, [2, 4, 6, 8]),
            ("Q2: What is 3+3?", 6, [3, 6, 9, 12]),
        ]
        rooms[room_id] = {
            'players': ['Alice', 'Bob'],
            'scores': {'Alice': 0, 'Bob': 0},
            'question_pool': pool,
            'player_progress': {'Alice': 0, 'Bob': 0},
            'is_started': True
        }

        # Both start at Q0
        alice_idx = rooms[room_id]['player_progress']['Alice']
        bob_idx = rooms[room_id]['player_progress']['Bob']
        self.assertEqual(pool[alice_idx][0], pool[bob_idx][0])
        self.assertEqual(pool[alice_idx][0], "Q0: What is 1+1?")

        # Alice answers Q0 and advances to Q1
        rooms[room_id]['player_progress']['Alice'] += 1
        rooms[room_id]['scores']['Alice'] += 1

        # Bob is still on Q0! Alice answering did NOT skip Bob's question
        self.assertEqual(rooms[room_id]['player_progress']['Bob'], 0)
        self.assertEqual(pool[rooms[room_id]['player_progress']['Bob']][0], "Q0: What is 1+1?")
        self.assertEqual(pool[rooms[room_id]['player_progress']['Alice']][0], "Q1: What is 2+2?")

        # Bob answers Q0 and advances to Q1
        rooms[room_id]['player_progress']['Bob'] += 1
        rooms[room_id]['scores']['Bob'] += 1
        self.assertEqual(pool[rooms[room_id]['player_progress']['Bob']][0], "Q1: What is 2+2?")

        # Both have now seen Q0 and are both on Q1
        self.assertEqual(rooms[room_id]['player_progress']['Alice'], 1)
        self.assertEqual(rooms[room_id]['player_progress']['Bob'], 1)

if __name__ == '__main__':
    unittest.main()
