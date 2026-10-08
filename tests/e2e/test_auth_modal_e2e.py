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
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'src'))

from app import app, socketio, rooms
from database import db


def get_free_port():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


class TestAuthModalE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        os.environ['FLASK_ENV'] = 'development'

        with app.app_context():
            db.create_all()

        cls.port = get_free_port()
        cls.server_thread = threading.Thread(
            target=socketio.run,
            args=(app,),
            kwargs={'port': cls.port, 'debug': False, 'allow_unsafe_werkzeug': True}
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)

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
        """Helper to safely click elements across potential PWA/ServiceWorker reloads."""
        for i in range(retries):
            try:
                el = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((by, value)))
                try:
                    el.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", el)
                return
            except Exception:
                if i == retries - 1:
                    raise
                time.sleep(0.5)

    def test_open_auth_modal_shows_popular_options(self):
        """Verify clicking Sign In opens the modal with Google, Apple, and GitHub options."""
        self.driver.get(self.base_url)
        time.sleep(0.5)

        # 1. Click the passport Sign In / Register trigger button
        self.click_safe(By.ID, "passport-auth-btn")

        # 2. Assert modal is visible
        wait = WebDriverWait(self.driver, 10)
        modal = wait.until(EC.visibility_of_element_located((By.ID, "authModalBackdrop")))
        self.assertTrue(modal.is_displayed())

        # 3. Assert title and options
        modal_title = self.driver.find_element(By.ID, "authModalTitle")
        self.assertIn("Sign In / Register", modal_title.text)

        # Check for Google button
        google_btn = self.driver.find_element(By.ID, "btn-google-login")
        self.assertIn("Continue with Google", google_btn.text)

        # Check for Coming Soon chips on Apple & GitHub
        page_text = self.driver.page_source
        self.assertIn("Continue with Apple", page_text)
        self.assertIn("Continue with GitHub", page_text)
        self.assertIn("Coming Soon", page_text)

        # 4. Check guest progress auto-sync reassurance
        guest_banner = self.driver.find_element(By.ID, "guestTransitionAlert")
        self.assertTrue(guest_banner.is_displayed())
        self.assertIn("Guest Progress Auto-Sync", guest_banner.text)

    def test_auth_modal_close_via_escape_or_button(self):
        """Verify modal closes when clicking close button or pressing Escape."""
        self.driver.get(self.base_url)
        time.sleep(0.5)

        # Open modal via nav button
        self.click_safe(By.ID, "nav-signin-btn")

        wait = WebDriverWait(self.driver, 10)
        modal = wait.until(EC.visibility_of_element_located((By.ID, "authModalBackdrop")))
        self.assertTrue(modal.is_displayed())

        # Close via button
        self.click_safe(By.CSS_SELECTOR, ".auth-modal-close")
        time.sleep(0.4)

        self.assertFalse(modal.is_displayed())

    def test_google_login_transitions_guest_to_verified(self):
        """Verify signing in with Google transitions UI to verified Google Synced status."""
        self.driver.get(self.base_url)
        time.sleep(0.5)

        # Open modal
        self.click_safe(By.ID, "passport-auth-btn")

        # Click Google Sign In button (in dev mode this uses signInWithGoogleMock)
        self.click_safe(By.ID, "btn-google-login")

        # Wait for page reload to complete and assert verified status
        wait = WebDriverWait(self.driver, 10)
        verified_badge = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".auth-badge.verified")))
        self.assertIn("Google Synced", verified_badge.text)

        # Navbar should now show user profile and logout
        nav_user = self.driver.find_element(By.ID, "nav-user-profile")
        self.assertTrue(nav_user.is_displayed())


if __name__ == '__main__':
    unittest.main()
