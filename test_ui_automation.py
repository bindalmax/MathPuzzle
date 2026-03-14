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

if __name__ == '__main__':
    print("To run these UI tests, you need to have 'selenium' installed (`pip install selenium`)")
    print("You also need to have the correct WebDriver for your browser (e.g., chromedriver).")
    unittest.main()
