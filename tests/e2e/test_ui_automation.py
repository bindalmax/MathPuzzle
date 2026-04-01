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

from app import app

class TestUIAutomation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run the Flask app in a separate thread
        cls.server_thread = threading.Thread(target=app.run, kwargs={'port': 5006, 'debug': False})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)

    def setUp(self):
        try:
            self.driver = webdriver.Chrome()
        except Exception as e:
            self.fail(f"Failed to initialize WebDriver: {e}")

        self.driver.implicitly_wait(5)
        self.base_url = "http://127.0.0.1:5006/"

    def tearDown(self):
        self.driver.quit()

    def test_start_page_loads(self):
        """Test that the start page loads correctly."""
        self.driver.get(self.base_url)
        self.assertEqual("MathPuzzle - Welcome", self.driver.title)
        welcome_text = self.driver.find_element(By.TAG_NAME, "h1").text
        self.assertEqual("Welcome to the Math Game!", welcome_text)

    def test_multiplayer_radio_exists(self):
        """Test that multiplayer radio button exists on start page."""
        self.driver.get(self.base_url)
        multiplayer_radio = self.driver.find_element(By.ID, "multiplayer")
        self.assertTrue(multiplayer_radio.is_enabled())
        single_radio = self.driver.find_element(By.ID, "single")
        self.assertTrue(single_radio.is_enabled())

    def test_single_player_game_flow(self):
        """Test starting a single player game and answering a question."""
        self.driver.get(self.base_url)
        self.driver.find_element(By.NAME, "player_name").send_keys("UITestPlayer")
        
        wait = WebDriverWait(self.driver, 10)
        start_button = wait.until(EC.element_to_be_clickable((By.ID, "start_btn")))
        start_button.click()
        
        wait.until(EC.url_contains("game"))
        self.assertIn("game", self.driver.current_url)
        
        question_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".question p")))
        self.assertIn("What is", question_element.text)

if __name__ == '__main__':
    unittest.main()
