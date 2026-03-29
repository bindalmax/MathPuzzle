import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
from app import app, socketio

class TestMultiplayerSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run the Flask app with SocketIO in a separate thread
        # Using a fixed port 5002 for the sync test
        cls.server_thread = threading.Thread(target=socketio.run, args=(app,), kwargs={'port': 5002, 'debug': False, 'allow_unsafe_werkzeug': True})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)

    def setUp(self):
        self.base_url = "http://127.0.0.1:5002/"
        self.drivers = []
        
        # Initialize two drivers
        for _ in range(2):
            try:
                driver = webdriver.Chrome()
                driver.implicitly_wait(5)
                self.drivers.append(driver)
            except Exception as e:
                self.fail(f"Failed to initialize Chrome WebDriver. Ensure chromedriver is in PATH. Error: {e}")

    def tearDown(self):
        for driver in self.drivers:
            driver.quit()

    def test_multiplayer_lobby_and_start(self):
        """Test that two players can join the same lobby and start the game."""
        creator = self.drivers[0]
        joiner = self.drivers[1]
        wait_c = WebDriverWait(creator, 10)
        wait_j = WebDriverWait(joiner, 15)

        # 1. Creator sets up a room
        creator.get(self.base_url)
        wait_c.until(EC.element_to_be_clickable((By.ID, "multiplayer"))).click()
        creator.find_element(By.ID, "player_name").send_keys("Creator")
        creator.find_element(By.ID, "start_btn").click()
        
        wait_c.until(EC.url_contains("multiplayer_lobby"))
        
        # 2. Joiner joins the room from the index page
        joiner.get(self.base_url)
        # Find the join form in the active lobbies list
        # We look for the room-item which contains the Join button
        wait_j.until(EC.presence_of_element_located((By.CLASS_NAME, "room-item")))
        
        join_input = joiner.find_element(By.XPATH, "//li[@class='room-item']//input[@name='player_name']")
        join_input.send_keys("Joiner")
        
        join_btn = joiner.find_element(By.XPATH, "//li[@class='room-item']//button[text()='Join']")
        join_btn.click()
        
        wait_j.until(EC.url_contains("multiplayer_lobby"))

        # 3. Verify both players see each other in the lobby
        # Note: We give SocketIO some time to update the list
        wait_c.until(EC.text_to_be_present_in_element((By.ID, "player-list"), "Joiner"))
        wait_j.until(EC.text_to_be_present_in_element((By.ID, "player-list"), "Creator"))

        # 4. Creator starts the game
        start_btn = wait_c.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Game')]")))
        start_btn.click()

        # 5. Both should land on the game page
        wait_c.until(EC.url_contains("game"))
        wait_j.until(EC.url_contains("game"))

        self.assertIn("game", creator.current_url)
        self.assertIn("game", joiner.current_url)

if __name__ == '__main__':
    unittest.main()
