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
        cls.server_thread = threading.Thread(target=socketio.run, args=(app,), kwargs={'port': 5002, 'debug': False, 'allow_unsafe_werkzeug': True})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)

    def setUp(self):
        self.base_url = "http://127.0.0.1:5002/"
        self.drivers = []
        for _ in range(2):
            driver = webdriver.Chrome()
            driver.implicitly_wait(5)
            self.drivers.append(driver)

    def tearDown(self):
        for driver in self.drivers:
            driver.quit()

    def test_multiplayer_sync_and_ownership(self):
        """Test question synchronization and creator-only start button."""
        creator = self.drivers[0]
        joiner = self.drivers[1]
        wait_c = WebDriverWait(creator, 10)
        wait_j = WebDriverWait(joiner, 10)

        # 1. Creator sets up a room
        creator.get(self.base_url)
        wait_c.until(EC.element_to_be_clickable((By.ID, "multiplayer"))).click()
        creator.find_element(By.ID, "player_name").send_keys("CreatorUser")
        creator.find_element(By.ID, "start_btn").click()
        wait_c.until(EC.url_contains("multiplayer_lobby"))

        # 2. Joiner joins the room
        joiner.get(self.base_url)
        wait_j.until(EC.presence_of_element_located((By.CLASS_NAME, "room-item")))
        joiner.find_element(By.XPATH, "//li[@class='room-item']//input[@name='player_name']").send_keys("JoinerUser")
        joiner.find_element(By.XPATH, "//li[@class='room-item']//button[text()='Join']").click()
        wait_j.until(EC.url_contains("multiplayer_lobby"))

        # 3. Verify Ownership: Joiner should NOT see 'Start Game' button
        joiner_buttons = joiner.find_elements(By.XPATH, "//button[contains(text(), 'Start Game')]")
        self.assertEqual(len(joiner_buttons), 0, "Joiner should not see the 'Start Game' button!")
        
        waiting_msg = joiner.find_element(By.CLASS_NAME, "waiting-msg").text
        self.assertIn("Waiting for host", waiting_msg)

        # 4. Creator starts the game
        start_btn = wait_c.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Game')]")))
        start_btn.click()

        # 5. Verify Question Synchronization
        wait_c.until(EC.url_contains("game"))
        wait_j.until(EC.url_contains("game"))
        
        q_c = wait_c.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".question p"))).text
        q_j = wait_j.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".question p"))).text
        
        self.assertEqual(q_c, q_j, f"Questions are NOT synchronized! Creator: '{q_c}', Joiner: '{q_j}'")
        print(f"Sync Success: Both players see '{q_c}'")

if __name__ == '__main__':
    unittest.main()
