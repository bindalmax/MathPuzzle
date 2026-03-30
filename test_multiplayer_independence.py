import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
from app import app, socketio

class TestMultiplayerIndependence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run the Flask app with SocketIO in a separate thread
        cls.server_thread = threading.Thread(target=socketio.run, args=(app,), kwargs={'port': 5003, 'debug': False, 'allow_unsafe_werkzeug': True})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)

    def setUp(self):
        self.base_url = "http://127.0.0.1:5003/"
        self.drivers = []
        for _ in range(2):
            driver = webdriver.Chrome()
            driver.implicitly_wait(5)
            self.drivers.append(driver)

    def tearDown(self):
        for driver in self.drivers:
            driver.quit()

    def test_individual_game_end_independence(self):
        """Test that one player finishing doesn't force the other to quit."""
        player1 = self.drivers[0]
        player2 = self.drivers[1]
        
        wait1 = WebDriverWait(player1, 15)
        wait2 = WebDriverWait(player2, 15)

        # 1. Setup Lobby - Player 1 creates
        player1.get(self.base_url)
        wait1.until(EC.element_to_be_clickable((By.ID, "multiplayer"))).click()
        player1.find_element(By.ID, "player_name").send_keys("Player1")
        # Explicitly select basic/easy
        player1.find_element(By.XPATH, "//option[@value='basic']").click()
        player1.find_element(By.XPATH, "//option[@value='easy']").click()
        player1.find_element(By.ID, "start_btn").click()
        wait1.until(EC.url_contains("multiplayer_lobby"))
        print("Player 1 created lobby.")

        # 2. Player 2 joins
        player2.get(self.base_url)
        wait2.until(EC.presence_of_element_located((By.CLASS_NAME, "room-item")))
        room_item = player2.find_element(By.CLASS_NAME, "room-item")
        room_item.find_element(By.NAME, "player_name").send_keys("Player2")
        room_item.find_element(By.XPATH, ".//button[text()='Join']").click()
        wait2.until(EC.url_contains("multiplayer_lobby"))
        print("Player 2 joined lobby.")

        # 3. Wait for synchronization in lobby
        wait1.until(EC.text_to_be_present_in_element((By.ID, "player-list"), "Player2"))
        print("Lobby synced.")

        # 4. Start Game
        wait1.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Game')]"))).click()
        wait1.until(EC.url_contains("game"))
        wait2.until(EC.url_contains("game"))
        print("Game started for both.")

        # 5. Player 1 finishes early (End Game)
        player1.find_element(By.LINK_TEXT, "End Game").click()
        wait1.until(EC.url_contains("game_over"))
        print("Player 1 finished early.")

        # 6. Verify Player 2 is STILL in the game
        time.sleep(2) 
        self.assertIn("game", player2.current_url, "Player 2 was forced out of the game!")
        
        # 7. Player 2 solves a question
        q_text = player2.find_element(By.CSS_SELECTOR, ".question p").text
        print(f"Player 2 solving: {q_text}")
        try:
            # Better solver: handles +, -, *, //
            clean_q = q_text.replace("What is ", "").replace("?", "")
            parts = clean_q.split()
            n1, op, n2 = int(parts[0]), parts[1], int(parts[2])
            
            if op == '+': ans = n1 + n2
            elif op == '-': ans = n1 - n2
            elif op == '*': ans = n1 * n2
            else: ans = n1 // n2
            
            player2.find_element(By.NAME, "answer").send_keys(str(ans))
            player2.find_element(By.XPATH, "//button[text()='Submit']").click()
            print(f"Player 2 submitted correct answer: {ans}")
        except Exception as e:
            self.fail(f"Solver failed: {e}")

        # 8. Verify Player 1 (on game_over) sees Player 2's new score
        # We wait for the table body to contain "1 pts"
        print("Player 1 waiting for live update...")
        wait1.until(EC.text_to_be_present_in_element((By.ID, "results-body"), "1 pts"))
        results = player1.find_element(By.ID, "results-body").text
        self.assertIn("Player2", results)
        self.assertIn("1 pts", results)
        print("SUCCESS: Player 1 saw live update.")

if __name__ == '__main__':
    unittest.main()
