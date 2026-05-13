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

class TestGamerIdPersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        with app.app_context():
            db.create_all()

        # Run on a different port than the main UI tests to avoid conflict
        cls.server_thread = threading.Thread(target=socketio.run, args=(app,), kwargs={'port': 5007, 'debug': False, 'allow_unsafe_werkzeug': True})
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
        self.base_url = "http://127.0.0.1:5007/"
        rooms.clear()

    def tearDown(self):
        self.driver.quit()

    def test_gamer_id_auto_generation(self):
        """Verify that a GamerId is automatically generated and populated."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)
        
        player_name_input = wait.until(EC.presence_of_element_located((By.ID, "player_name")))
        generated_id = player_name_input.get_attribute("value")
        
        self.assertTrue(len(generated_id) > 0, "GamerId should not be empty")
        # Check if it matches the pattern (AdjectiveNounNumber)
        # Our adjectives and nouns are 4-8 chars, numbers are 3 digits. 
        # Minimal length should be around 10.
        self.assertTrue(len(generated_id) >= 10, f"Generated ID '{generated_id}' seems too short")

    def test_gamer_id_persistence(self):
        """Verify that a GamerId is persisted in localStorage and survives page reload."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)
        
        player_name_input = wait.until(EC.presence_of_element_located((By.ID, "player_name")))
        
        # Manually set a GamerId
        custom_id = "TestWizard999"
        player_name_input.clear()
        player_name_input.send_keys(custom_id)
        
        # Small delay to ensure localStorage is updated
        time.sleep(1)
        
        # Reload the page
        self.driver.refresh()
        
        # Verify the custom ID is still there
        player_name_input = wait.until(EC.presence_of_element_located((By.ID, "player_name")))
        self.assertEqual(player_name_input.get_attribute("value"), custom_id)

    def click_safe(self, by, value, retries=5):
        """Helper to click an element that might go stale or be temporarily unclickable."""
        for i in range(retries):
            try:
                element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((by, value)))
                try:
                    element.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", element)
                return
            except Exception:
                if i == retries - 1:
                    raise
                time.sleep(1)

    def test_gamer_id_sync_across_inputs(self):
        """Verify that editing one player_name input updates all others on the page."""
        # Manually add a room to the global rooms dict so it shows up on index page
        # This ensures we have at least 2 inputs: the main setup one and the one in the lobby list
        room_id = 'test-sync-room'
        rooms[room_id] = {
            'players': ['TestHost'],
            'scores': {'TestHost': 0},
            'active_connections': set(),
            'category': 'percentage',
            'difficulty': 'medium',
            'mode': 'time',
            'mode_value': 20,
            'is_started': False,
            'creator': 'TestHost',
            'last_activity': time.time()
        }
        
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 15)
        
        # 1. Stay on default tab (Multiplayer) to see both setup form and lobby section
        # This ensures the main player_name input is visible for interaction
        
        # 2. Wait for the room item to appear
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "room-item")))
        
        # 3. Check for multiple inputs (should find: main setup input + lobby room inputs)
        inputs = wait.until(lambda d: d.find_elements(By.NAME, "player_name"))
        self.assertTrue(len(inputs) >= 2, f"Should have at least 2 player_name inputs (setup + lobby join), found {len(inputs)}")
        
        # 4. Edit the main one (which should be visible now)
        new_id = "SyncMaster123"
        main_input = self.driver.find_element(By.ID, "player_name")
        main_input.clear()
        main_input.send_keys(new_id)
        
        # 5. Verify all inputs named player_name are updated (including hidden ones)
        time.sleep(1) # Wait for JS sync
        all_inputs = self.driver.find_elements(By.NAME, "player_name")
        for inp in all_inputs:
            self.assertEqual(inp.get_attribute("value"), new_id, f"Input failed to sync: {inp.get_attribute('outerHTML')}")

if __name__ == '__main__':
    unittest.main()
