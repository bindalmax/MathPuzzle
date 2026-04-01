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

from app import app, rooms

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
        rooms.clear()

    def tearDown(self):
        self.driver.quit()

    def test_defaults_on_page_load(self):
        """Verify that Multiplayer, Percentage, and Medium are selected by default."""
        self.driver.get(self.base_url)
        
        # Check Multiplayer is checked
        multiplayer_radio = self.driver.find_element(By.ID, "multiplayer")
        self.assertTrue(multiplayer_radio.is_selected())
        
        # Check Percentage is selected
        category_select = self.driver.find_element(By.ID, "category")
        selected_category = category_select.find_element(By.XPATH, ".//option[@selected]").get_attribute("value")
        self.assertEqual(selected_category, "percentage")
        
        # Check Medium is selected
        difficulty_select = self.driver.find_element(By.ID, "difficulty")
        selected_difficulty = difficulty_select.find_element(By.XPATH, ".//option[@selected]").get_attribute("value")
        self.assertEqual(selected_difficulty, "medium")
        
        # Check button text
        start_btn = self.driver.find_element(By.ID, "start_btn")
        self.assertEqual(start_btn.text, "Create Multiplayer Lobby")

    def test_single_player_flow_explicit_selection(self):
        """Test starting a single player game by explicitly overriding defaults."""
        self.driver.get(self.base_url)
        
        # Select Single Player
        self.driver.find_element(By.ID, "single").click()
        
        # Fill name
        self.driver.find_element(By.NAME, "player_name").send_keys("SoloPlayer")
        
        # Category and Difficulty are already defaulted to something valid
        
        wait = WebDriverWait(self.driver, 10)
        start_button = wait.until(EC.element_to_be_clickable((By.ID, "start_btn")))
        self.assertEqual(start_button.text, "Start Single Player Game")
        start_button.click()
        
        wait.until(EC.url_contains("game"))
        self.assertIn("game", self.driver.current_url)

if __name__ == '__main__':
    unittest.main()
