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
        # Configuration for test environment
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Pre-create tables for the server thread
        with app.app_context():
            db.create_all()

        # Run the Flask app with SocketIO in a separate thread
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
        # Clean up database after each test
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

        category_select = self.driver.find_element(By.NAME, "category")
        selected_category = category_select.find_element(By.CSS_SELECTOR, "option:checked")
        self.assertEqual(selected_category.get_attribute("value"), "percentage")

        difficulty_select = self.driver.find_element(By.NAME, "difficulty")
        selected_difficulty = difficulty_select.find_element(By.CSS_SELECTOR, "option:checked")
        self.assertEqual(selected_difficulty.get_attribute("value"), "medium")

    def test_single_player_flow_explicit_selection(self):
        """Test starting a single player game by explicitly overriding defaults."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)
        
        single_radio = wait.until(EC.element_to_be_clickable((By.ID, "single")))
        single_radio.click()
        
        self.driver.find_element(By.NAME, "player_name").send_keys("SoloPlayer")
        
        start_button = self.driver.find_element(By.ID, "start_btn")
        self.assertEqual(start_button.text, "Start Single Player Game")
        start_button.click()
        
        wait.until(EC.url_contains("game"))
        self.assertIn("game", self.driver.current_url)
        
        question_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".question-box p")))
        self.assertIn("What is", question_element.text)

    def test_navigation_to_hall_of_fame(self):
        """Verify link text for the leaderboard and successful navigation."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 15)
        
        link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Hall of Fame")))
        self.assertEqual(link.text, "View Global Hall of Fame")
        link.click()
        
        h1 = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertEqual(h1.text, "Global Hall of Fame")
        
        self.assertIn("Hall of Fame", self.driver.title)

if __name__ == '__main__':
    unittest.main()
