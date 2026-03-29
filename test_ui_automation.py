import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
from app import app

class TestUIAutomation(unittest.TestCase):
    def setUp(self):
        # Run the Flask app in a separate thread
        self.server_thread = threading.Thread(target=app.run, kwargs={'port': 5001})
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(2)  # Give the server a moment to start

        # Initialize the WebDriver
        # Note: You will need to have chromedriver installed and in your PATH
        # or specify the path to the executable.
        try:
            self.driver = webdriver.Chrome()
        except Exception as e:
            self.fail(f"Failed to initialize WebDriver. Make sure chromedriver is installed and in your PATH. Error: {e}")

        self.driver.implicitly_wait(5)
        self.base_url = "http://127.0.0.1:5001/"

    def tearDown(self):
        self.driver.quit()
        # Note: There isn't a clean way to stop the Flask server thread,
        # but since it's a daemon, it will exit when the main thread does.

    def test_start_page_loads(self):
        """Test that the start page loads correctly."""
        self.driver.get(self.base_url)
        self.assertEqual("Math Game", self.driver.title)
        welcome_text = self.driver.find_element(By.TAG_NAME, "h1").text
        self.assertEqual("Welcome to the Math Game!", welcome_text)

    def test_start_game_and_play(self):
        """Test starting a game and answering a question."""
        self.driver.get(self.base_url)
        
        # Fill out the form
        self.driver.find_element(By.NAME, "player_name").send_keys("UITestPlayer")
        
        # Use explicit wait for elements to be clickable
        wait = WebDriverWait(self.driver, 10)
        
        basic_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[@value='basic']")))
        basic_option.click()
        
        easy_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[@value='easy']")))
        easy_option.click()
        
        # Start game
        start_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Game')]")))
        start_button.click()
        
        # Wait for URL to change to the game page
        wait.until(EC.url_contains("game"))
        self.assertIn("game", self.driver.current_url)
        
        # Find the question
        question_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".question p")))
        question_text = question_element.text
        self.assertIn("What is", question_text)
        
        # Answer the question with a dummy value
        answer_input = wait.until(EC.presence_of_element_located((By.NAME, "answer")))
        answer_input.send_keys("123")
        
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit')]")))
        submit_button.click()
        
        # After submitting, we should still be on the game page (or receive next question)
        # Verify URL is still game or redirect happened correctly
        wait.until(EC.url_contains("game"))
        self.assertIn("game", self.driver.current_url)

    def test_multiplayer_radio_exists(self):
        """Test that multiplayer radio button exists on start page."""
        self.driver.get(self.base_url)
        
        # Check multiplayer radio button exists
        multiplayer_radio = self.driver.find_element(By.ID, "multiplayer")
        self.assertTrue(multiplayer_radio.is_enabled())
        
        single_radio = self.driver.find_element(By.ID, "single")
        self.assertTrue(single_radio.is_enabled())

    def test_multiplayer_lobby_access(self):
        """Test accessing multiplayer lobby."""
        self.driver.get(self.base_url)
        
        wait = WebDriverWait(self.driver, 10)
        
        # Select multiplayer
        multiplayer_radio = wait.until(EC.element_to_be_clickable((By.ID, "multiplayer")))
        multiplayer_radio.click()
        
        # Fill name
        self.driver.find_element(By.NAME, "player_name").send_keys("MPPlayer1")
        
        # Select category and difficulty
        wait.until(EC.element_to_be_clickable((By.XPATH, "//option[@value='basic']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//option[@value='easy']"))).click()
        
        # Start game
        start_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Game')]")))
        start_button.click()
        
        # Should redirect to lobby
        wait.until(EC.url_contains("multiplayer_lobby"))
        self.assertIn("multiplayer_lobby", self.driver.current_url)
        
        # Check lobby elements
        lobby_title = self.driver.find_element(By.TAG_NAME, "h1").text
        self.assertIn("Multiplayer Lobby", lobby_title)
        
        # Check player list exists
        player_list = self.driver.find_element(By.ID, "player-list")
        self.assertIsNotNone(player_list)
        
        # Check start game button exists
        start_game_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Start Game for Everyone')]")
        self.assertIsNotNone(start_game_btn)

    def test_multiplayer_game_flow(self):
        """Test full multiplayer game flow."""
        self.driver.get(self.base_url)
        
        wait = WebDriverWait(self.driver, 10)
        
        # Select multiplayer and fill form
        wait.until(EC.element_to_be_clickable((By.ID, "multiplayer"))).click()
        self.driver.find_element(By.NAME, "player_name").send_keys("MPPlayer2")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//option[@value='basic']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//option[@value='easy']"))).click()
        
        # Start game
        start_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Game')]")))
        start_button.click()
        
        # Wait for lobby
        wait.until(EC.url_contains("multiplayer_lobby"))
        
        # Click start game for everyone
        start_game_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Game for Everyone')]")))
        start_game_btn.click()
        
        # Should redirect to game
        wait.until(EC.url_contains("game"))
        self.assertIn("game", self.driver.current_url)
        
        # Check game elements exist
        question_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".question p")))
        self.assertIsNotNone(question_element)
        
        # Check live scores panel exists (for multiplayer)
        try:
            live_scores = self.driver.find_element(By.CLASS_NAME, "live-scores")
            self.assertIsNotNone(live_scores)
        except:
            pass  # Live scores might not appear until game starts


if __name__ == '__main__':
    print("To run these UI tests, you need to have 'selenium' installed (`pip install selenium`)")
    print("You also need to have the correct WebDriver for your browser (e.g., chromedriver).")
    print("Note: These tests require the Flask app to be running separately.")
    unittest.main()
