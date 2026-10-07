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

def get_free_port():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

class TestMultiplayerE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            from database import db
            db.create_all()
        cls.port = get_free_port()
        # Run the Flask app with SocketIO in a separate thread
        cls.server_thread = threading.Thread(target=socketio.run, args=(app,), kwargs={'port': cls.port, 'debug': False, 'allow_unsafe_werkzeug': True})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)

    def setUp(self):
        self.base_url = f"http://127.0.0.1:{self.port}/"
        self.drivers = []
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        for _ in range(2):
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(5)
            self.drivers.append(driver)
        # Ensure a clean state for each test
        rooms.clear()

    def tearDown(self):
        for driver in self.drivers:
            driver.quit()

    def click_safe(self, driver, by, value, retries=5):
        """Helper to click an element that might go stale during PWA service worker initialization."""
        for i in range(retries):
            try:
                element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((by, value)))
                try:
                    element.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", element)
                return
            except Exception:
                if i == retries - 1:
                    raise
                time.sleep(1)

    def test_multiplayer_sync_and_independence(self):
        """Test question synchronization and individual game end."""
        p1 = self.drivers[0]
        p2 = self.drivers[1]
        
        wait1 = WebDriverWait(p1, 15)
        wait2 = WebDriverWait(p2, 15)

        # 1. Player 1 creates lobby
        p1.get(self.base_url)
        wait1.until(EC.presence_of_element_located((By.ID, "player_name"))).send_keys("Host")
        self.click_safe(p1, By.ID, "start_btn")
        wait1.until(EC.url_contains("multiplayer_lobby"))

        # 2. Player 2 joins
        p2.get(self.base_url)
        room_item = wait2.until(EC.presence_of_element_located((By.CLASS_NAME, "room-item")))
        room_item.find_element(By.NAME, "player_name").send_keys("Guest")
        self.click_safe(p2, By.XPATH, "//button[contains(text(), 'Join')]")
        wait2.until(EC.url_contains("multiplayer_lobby"))

        # 3. Start Game
        self.click_safe(p1, By.XPATH, "//button[contains(text(), 'Start Game')]")
        wait1.until(EC.url_contains("game"))
        wait2.until(EC.url_contains("game"))

        # 4. Verify Sync (Using .question-box p selector)
        q1 = p1.find_element(By.CSS_SELECTOR, ".question-box p").text
        q2 = p2.find_element(By.CSS_SELECTOR, ".question-box p").text
        self.assertEqual(q1, q2, "Questions are not synchronized!")

        # 5. Independence: Player 1 finishes, Player 2 stays
        p1.find_element(By.LINK_TEXT, "QUIT SESSION & SAVE").click()
        wait1.until(EC.url_contains("game_over"))
        
        self.assertIn("game", p2.current_url, "Player 2 was forced out!")

if __name__ == '__main__':
    unittest.main()
