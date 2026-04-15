import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app, socketio, rooms

class TestMultiplayerE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            from database import db
            db.create_all()
        # Run the Flask app with SocketIO in a separate thread
        cls.server_thread = threading.Thread(target=socketio.run, args=(app,), kwargs={'port': 5005, 'debug': False, 'allow_unsafe_werkzeug': True})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)

    def setUp(self):
        self.base_url = "http://127.0.0.1:5005/"
        self.drivers = []
        for _ in range(2):
            driver = webdriver.Chrome()
            driver.implicitly_wait(5)
            self.drivers.append(driver)
        # Ensure a clean state for each test
        rooms.clear()

    def tearDown(self):
        for driver in self.drivers:
            driver.quit()

    def test_multiplayer_sync_and_independence(self):
        """Test question synchronization and individual game end."""
        p1 = self.drivers[0]
        p2 = self.drivers[1]
        
        wait1 = WebDriverWait(p1, 15)
        wait2 = WebDriverWait(p2, 15)

        # 1. Player 1 creates lobby
        p1.get(self.base_url)
        # Multiplayer is default now, so just fill name and create
        p1.find_element(By.ID, "player_name").send_keys("Host")
        p1.find_element(By.ID, "start_btn").click()
        wait1.until(EC.url_contains("multiplayer_lobby"))

        # 2. Player 2 joins
        p2.get(self.base_url)
        wait2.until(EC.presence_of_element_located((By.CLASS_NAME, "room-item")))
        room_item = p2.find_element(By.CLASS_NAME, "room-item")
        room_item.find_element(By.NAME, "player_name").send_keys("Guest")
        room_item.find_element(By.XPATH, ".//button[contains(text(), 'Join')]").click()
        wait2.until(EC.url_contains("multiplayer_lobby"))

        # 3. Start Game
        wait1.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Game')]"))).click()
        wait1.until(EC.url_contains("game"))
        wait2.until(EC.url_contains("game"))

        # 4. Verify Sync (Using new .question-box p selector)
        q1 = p1.find_element(By.CSS_SELECTOR, ".question-box p").text
        q2 = p2.find_element(By.CSS_SELECTOR, ".question-box p").text
        self.assertEqual(q1, q2, "Questions are not synchronized!")

        # 5. Independence: Player 1 finishes, Player 2 stays
        p1.find_element(By.LINK_TEXT, "QUIT SESSION & SAVE").click()
        wait1.until(EC.url_contains("game_over"))
        
        self.assertIn("game", p2.current_url, "Player 2 was forced out!")

if __name__ == '__main__':
    unittest.main()
