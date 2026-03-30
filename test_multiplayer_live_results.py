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
        player1.find_element(By.ID, "start_btn").click()
        wait1.until(EC.url_contains("multiplayer_lobby"))

        # 2. Player 2 joins
        player2.get(self.base_url)
        wait2.until(EC.presence_of_element_located((By.CLASS_NAME, "room-item")))
        player2.find_element(By.XPATH, "//li[@class='room-item']//input[@name='player_name']").send_keys("Player2")
        player2.find_element(By.XPATH, "//li[@class='room-item']//button[text()='Join']").click()
        wait2.until(EC.url_contains("multiplayer_lobby"))

        # 3. Start Game
        wait1.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Game')]"))).click()
        wait1.until(EC.url_contains("game"))
        wait2.until(EC.url_contains("game"))

        # 4. Player 1 finishes early (End Game)
        player1.find_element(By.LINK_TEXT, "End Game").click()
        wait1.until(EC.url_contains("game_over"))
        print("Player 1 finished the game.")

        # 5. Verify Player 2 is STILL in the game
        time.sleep(2) # Wait a moment to ensure no delayed redirect
        self.assertIn("game", player2.current_url, "Player 2 was forced out of the game when Player 1 finished!")
        
        # 6. Verify Player 2 can still score
        # (Simple solver)
        q_text = player2.find_element(By.CSS_SELECTOR, ".question p").text
        parts = q_text.replace("What is ", "").replace("?", "").split()
        ans = int(parts[0]) + int(parts[2]) if parts[1] == '+' else int(parts[0]) - int(parts[2])
        
        player2.find_element(By.NAME, "answer").send_keys(str(ans))
        player2.find_element(By.XPATH, "//button[text()='Submit']").click()
        print("Player 2 successfully submitted an answer after Player 1 finished.")

        # 7. Verify Player 1 (on game_over) sees Player 2's new score
        wait1.until(EC.text_to_be_present_in_element((By.ID, "results-body"), "1 pts"))
        results = player1.find_element(By.ID, "results-body").text
        self.assertIn("Player2", results)
        self.assertIn("1 pts", results)
        print("SUCCESS: Player 1 saw Player 2's score update in real-time from the Game Over page.")

if __name__ == '__main__':
    unittest.main()
