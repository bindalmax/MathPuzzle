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
from database import db

class TestUIAutomation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        with app.app_context():
            db.create_all()

        cls.server_thread = threading.Thread(target=socketio.run, args=(app,), kwargs={'port': 5006, 'debug': False, 'allow_unsafe_werkzeug': True})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(3)

    def setUp(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            self.driver = webdriver.Chrome(options=options)
        except Exception:
            self.driver = webdriver.Chrome()

        self.driver.implicitly_wait(5)
        self.base_url = "http://127.0.0.1:5006/"
        rooms.clear()

    def tearDown(self):
        self.driver.quit()
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()

    def test_defaults_on_page_load(self):
        """Verify that GamerId, Percentage, and Medium are selected by default."""
        self.driver.get(self.base_url)
        
        wait = WebDriverWait(self.driver, 10)
        name_label = wait.until(EC.presence_of_element_located((By.XPATH, "//label[@for='player_name']"))).text
        self.assertIn("GamerId", name_label)
        
        multiplayer_radio = self.driver.find_element(By.ID, "multiplayer")
        self.assertTrue(multiplayer_radio.is_selected())
        
        start_btn = self.driver.find_element(By.ID, "start_btn")
        self.assertEqual(start_btn.text, "Create Multiplayer Lobby")

    def test_single_player_flow_explicit_selection(self):
        """Test starting a single player game by explicitly overriding defaults."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)
        
        # Select Single Player
        single_radio = wait.until(EC.element_to_be_clickable((By.ID, "single")))
        single_radio.click()
        
        self.driver.find_element(By.NAME, "player_name").send_keys("SoloPlayer")
        
        # Change category to Basic to ensure simple answer parsing if needed, 
        # though here we just want to verify MCQ buttons exist.
        category_select = self.driver.find_element(By.ID, "category")
        category_select.find_element(By.XPATH, "//option[@value='basic']").click()
        
        start_button = self.driver.find_element(By.ID, "start_btn")
        start_button.click()
        
        wait.until(EC.url_contains("game"))
        
        # Verify MCQ buttons exist even in easy/medium mode
        # (The default difficulty is Medium, but Basic easy would also have buttons now)
        choices = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "choice-btn")))
        self.assertEqual(len(choices), 4, "Should have 4 MCQ buttons in Easy/Medium mode.")

    def test_navigation_to_hall_of_fame(self):
        """Verify link text for the leaderboard and successful navigation."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 15)
        
        link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Hall of Fame")))
        link.click()
        
        h1 = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertEqual(h1.text, "Global Hall of Fame")

    def test_startup_challenge_ui(self):
        """Verify Startup Challenge radio button and UI updates."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)
        
        startup_radio = wait.until(EC.element_to_be_clickable((By.ID, "startup_challenge")))
        startup_radio.click()
        
        # Verify info box is visible
        startup_info = self.driver.find_element(By.ID, "startup-info")
        self.assertTrue(startup_info.is_displayed())
        
        # Verify standard options are hidden
        standard_options = self.driver.find_element(By.ID, "standard-options")
        self.assertFalse(standard_options.is_displayed())
        
        # Verify button text change
        start_btn = self.driver.find_element(By.ID, "start_btn")
        self.assertEqual(start_btn.text, "Start Startup Challenge")

if __name__ == '__main__':
    unittest.main()
