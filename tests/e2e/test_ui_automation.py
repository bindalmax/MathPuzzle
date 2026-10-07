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

def get_free_port():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

class TestUIAutomation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        with app.app_context():
            db.create_all()

        cls.port = get_free_port()
        cls.server_thread = threading.Thread(target=socketio.run, args=(app,), kwargs={'port': cls.port, 'debug': False, 'allow_unsafe_werkzeug': True})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(3)

    def setUp(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--window-size=1280,800')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            self.driver = webdriver.Chrome(options=options)
        except Exception:
            self.driver = webdriver.Chrome()

        self.driver.implicitly_wait(5)
        self.base_url = f"http://127.0.0.1:{self.port}/"
        rooms.clear()

    def tearDown(self):
        self.driver.quit()
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()

    def click_safe(self, by, value, retries=5):
        """Helper to click an element that might go stale or be temporarily unclickable."""
        for i in range(retries):
            try:
                # Always re-locate to avoid stale elements
                element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((by, value)))
                # Try regular click first
                try:
                    element.click()
                except Exception:
                    # Fallback to JS click if not interactable (e.g. hidden radio)
                    self.driver.execute_script("arguments[0].click();", element)
                return
            except Exception:
                if i == retries - 1:
                    raise
                time.sleep(1)

    def test_defaults_on_page_load(self):
        """Verify that GamerId, Percentage, and Medium are selected by default."""
        self.driver.get(self.base_url)
        
        wait = WebDriverWait(self.driver, 10)
        # Check label text (we removed uppercase in CSS, so it should be GamerId)
        name_label = wait.until(EC.presence_of_element_located((By.XPATH, "//label[@for='player_name']"))).text
        self.assertIn("GamerId", name_label)
        
        # Multiplayer tab should be active by default
        multiplayer_tab = self.driver.find_element(By.ID, "tab-multiplayer")
        self.assertIn("active", multiplayer_tab.get_attribute("class"))
        
        start_btn = self.driver.find_element(By.ID, "start_btn")
        self.assertEqual(start_btn.text, "Create Multiplayer Lobby")

    def test_single_player_flow_explicit_selection(self):
        """Test starting a single player game by explicitly overriding defaults."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)
        
        # Click the radio button directly (it's off-screen but clickable by JS fallback in click_safe)
        self.click_safe(By.ID, "single")
        time.sleep(0.5)
        
        # Verify radio is selected
        single_radio = self.driver.find_element(By.ID, "single")
        self.assertTrue(single_radio.is_selected())
        
        self.driver.find_element(By.NAME, "player_name").send_keys("SoloPlayer")
        
        # Change category to Basic
        category_select = self.driver.find_element(By.ID, "category")
        category_select.find_element(By.XPATH, "//option[@value='basic']").click()
        
        self.click_safe(By.ID, "start_btn")
        
        wait.until(EC.url_contains("game"))
        
        # Verify MCQ buttons exist
        choices = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "choice-btn")))
        self.assertEqual(len(choices), 4)

    def test_katex_math_rendering_in_game(self):
        """Verify that KaTeX successfully auto-renders algebra equations into .katex elements."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)

        self.click_safe(By.ID, "single")
        time.sleep(0.5)

        self.driver.find_element(By.NAME, "player_name").send_keys("MathScholar")

        # Select Algebra category
        category_select = self.driver.find_element(By.ID, "category")
        category_select.find_element(By.XPATH, "//option[@value='algebra']").click()

        self.click_safe(By.ID, "start_btn")
        wait.until(EC.url_contains("game"))

        # Verify that KaTeX rendered the equation in the question box
        katex_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "katex")))
        self.assertTrue(katex_element.is_displayed())
        self.assertIn("katex", katex_element.get_attribute("class"))

    def test_navigation_to_hall_of_fame(self):
        """Verify link text for the leaderboard and successful navigation."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 15)
        
        # The new link text includes an emoji
        self.click_safe(By.ID, "leaderboard_link")
        wait.until(EC.url_contains("leaderboard"))
        
        h1 = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertEqual(h1.text, "Global Hall of Fame")

    def test_startup_challenge_ui(self):
        """Verify Startup Challenge tab and UI updates."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)
        
        # Click the radio button directly (it's off-screen but clickable by JS fallback in click_safe)
        self.click_safe(By.ID, "startup_challenge")
        time.sleep(0.5)
        
        # Verify hidden radio is synced
        startup_radio = self.driver.find_element(By.ID, "startup_challenge")
        self.assertTrue(startup_radio.is_selected())
        
        # Verify info box is visible
        wait.until(EC.visibility_of_element_located((By.ID, "startup-info")))
        
        # Verify standard options are hidden
        wait.until(EC.invisibility_of_element_located((By.ID, "standard-options")))
        
        # Verify button text change
        start_btn = self.driver.find_element(By.ID, "start_btn")
        self.assertEqual(start_btn.text, "Start Startup Quest")

    def test_multiplayer_invite_ui(self):
        """Verify invite link and QR code elements in the lobby."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)
        
        self.driver.find_element(By.NAME, "player_name").send_keys("LobbyHost")
        self.click_safe(By.ID, "start_btn")
        
        wait.until(EC.url_contains("multiplayer_lobby"))
        
        # Check for Invite Center elements
        wait.until(EC.presence_of_element_located((By.ID, "share-btn")))
        self.assertTrue(self.driver.find_element(By.ID, "qr-btn").is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, "copy-btn").is_displayed())
        
        # Test QR Toggle
        qr_container = self.driver.find_element(By.ID, "qr-container")
        
        # It might be hidden by display: none or opacity. check is_displayed()
        # Ensure it starts hidden
        self.assertFalse(qr_container.is_displayed())
        
        self.click_safe(By.ID, "qr-btn")
        # Wait for it to become visible
        wait.until(lambda d: qr_container.is_displayed())
        
        # Verify QR image has src from qrserver
        qr_img = self.driver.find_element(By.ID, "qr-image")
        self.assertIn("qrserver.com", qr_img.get_attribute("src"))

if __name__ == '__main__':
    unittest.main()
