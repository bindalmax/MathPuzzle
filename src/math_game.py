import time
import threading
from questions import QuestionFactory
from highscore_manager import HighscoreManager

# --- Game Logic ---
class Game:
    def __init__(self, player_name, question_factory, mode='time', value=20):
        self.player_name = player_name
        self.question_factory = question_factory
        self.score = 0
        self.mode = mode  # 'time' or 'questions'
        self.value = value  # duration in seconds or number of questions
        self.game_over = threading.Event()
        self.timer_expired = False

    def timer_thread(self):
        time.sleep(self.value)
        if not self.game_over.is_set():
            self.timer_expired = True
            self.game_over.set()
            print("\nTime's up! Press Enter to see your score.")

    def ask_question(self, question, answer, choices):
        print(question)
        user_answer = None
        if choices:
            choice_map = {chr(65 + i): choice for i, choice in enumerate(choices)}
            for label, choice in choice_map.items():
                print(f"{label}) {choice}")
            
            user_input_raw = input("Your choice (A, B, C, D) or answer: ").strip()
            user_input = user_input_raw.upper()
            if user_input_raw.lower() == 'quit':
                return 'quit'
            if user_input in choice_map:
                user_answer = choice_map[user_input]
            else:
                matched = False
                for choice in choices:
                    try:
                        if isinstance(choice, (int, float)):
                            if float(user_input_raw) == float(choice):
                                user_answer = choice
                                matched = True
                                break
                    except ValueError:
                        pass
                    if str(choice).lower() == user_input_raw.lower():
                        user_answer = choice
                        matched = True
                        break
                # if not matched, user_answer remains None
        else:
            user_input = input("Your answer: ")
            if user_input.lower() == 'quit':
                return 'quit'
            try:
                user_answer = float(user_input)
            except ValueError:
                print("Invalid input. Please enter a number.")
                return None
        return user_answer

    def run(self):
        if self.mode == 'time':
            print(f"\nStarting game for {self.player_name}! You have {self.value} seconds.")
            timer = threading.Thread(target=self.timer_thread)
            timer.daemon = True
            timer.start()
        else:
            print(f"\nStarting game for {self.player_name}! Answer {self.value} questions.")

        questions_answered = 0
        while not self.game_over.is_set():
            try:
                question, answer, choices = self.question_factory.create_question()
                
                user_answer = self.ask_question(question, answer, choices)
                
                if user_answer == 'quit':
                    self.game_over.set()
                    break

                if self.game_over.is_set():
                    break
                
                if user_answer is not None and abs(user_answer - answer) < 0.01:
                    print("Correct!")
                    self.score += 1
                else:
                    print(f"Wrong! The correct answer is {answer}")

                questions_answered += 1

                if self.mode == 'questions' and questions_answered >= self.value:
                    self.game_over.set()
                    print(f"\nYou've answered {self.value} questions! Game over.")

            except NotImplementedError as e:
                print(e)
                break
            except (ValueError, EOFError):
                if not self.game_over.is_set():
                    print("Invalid input. Please enter a number or 'quit'.")
                break
        return self.score

class StartupChallengeGame(Game):
    def __init__(self, player_name):
        self.player_name = player_name
        self.percentage_factory = QuestionFactory("percentage", "medium")
        self.profit_loss_factory = QuestionFactory("profit_loss", "medium")
        self.startup_value = 10000.0
        self.total_questions = 10
        self.score = 0
        self.game_over = threading.Event()

    def run(self):
        print(f"\nWelcome to the Startup Challenge, {self.player_name}!")
        print("You have $10,000 in seed funding. Grow your business by making smart mathematical decisions.")
        
        for i in range(1, self.total_questions + 1):
            if i % 2 == 1:
                factory = self.percentage_factory
                narrative = "Market Analysis: "
            else:
                factory = self.profit_loss_factory
                narrative = "Financial Planning: "
            
            question, answer, choices = factory.create_question()
            print(f"\nQuestion {i}/{self.total_questions}")
            print(f"Current Startup Value: ${self.startup_value:,.2f}")
            print(narrative, end="")
            
            user_answer = self.ask_question(question, answer, choices)
            
            if user_answer == 'quit':
                break
            
            if user_answer is not None and abs(user_answer - answer) < 0.01:
                growth = self.startup_value * 0.2
                self.startup_value += growth
                self.score += 1
                print(f"Correct! Your startup value grew by ${growth:,.2f} to ${self.startup_value:,.2f}")
            else:
                loss = self.startup_value * 0.1
                self.startup_value -= loss
                print(f"Wrong! The correct answer was {answer}. Your startup value fell by ${loss:,.2f} to ${self.startup_value:,.2f}")

        ceo_score = int(self.startup_value / 100)
        print(f"\nChallenge Complete!")
        print(f"Final Startup Value: ${self.startup_value:,.2f}")
        print(f"Your CEO Score: {ceo_score}")
        
        if ceo_score > 500:
            title = "Unicorn CEO 🦄"
        elif ceo_score > 200:
            title = "Serial Entrepreneur 🚀"
        elif ceo_score > 100:
            title = "Startup Founder 💼"
        else:
            title = "Junior Founder 🌱"
        
        print(f"Title: {title}")
        return ceo_score, title

# --- Main Execution ---
def main():
    player_name = input("Enter your name: ")
    highscore_manager = HighscoreManager()

    while True:
        print("\n--- Main Menu ---")
        print("1. Basic Arithmetic")
        print("2. Decimals and Fractions")
        print("3. Percentages")
        print("4. Profit and Loss")
        print("5. Algebra")
        print("6. Startup Challenge (Narrative Mode)")
        print("7. Quit Game")
        
        choice = input("Enter your choice (1-7): ")

        if choice == '7':
            print("\nThanks for playing!")
            break

        if choice == '6':
            game = StartupChallengeGame(player_name)
            final_score, title = game.run()
            highscore_manager.add_score(player_name, final_score, "startup_challenge", "medium")
            highscore_manager.display(highscore_manager.load())
            input("\nPress Enter to return to the main menu...")
            continue

        category_map = {"1": "basic", "2": "decimal", "3": "percentage", "4": "profit_loss", "5": "algebra"}
        if choice not in category_map:
            print("Invalid choice. Please try again.")
            continue
        
        category = category_map[choice]

        print("\nChoose a difficulty:")
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        level_map = {"1": "easy", "2": "medium", "3": "hard"}
        while True:
            level_choice = input("Enter your choice (1-3): ")
            if level_choice in level_map:
                level = level_map[level_choice]
                break
            else:
                print("Invalid choice.")

        print("\nChoose game mode:")
        print("1. Time Mode (answer as many as you can in X seconds)")
        print("2. Question Count Mode (answer exactly X questions)")
        mode_choice = input("Enter your choice (1-2): ")

        if mode_choice == '1':
            mode = 'time'
            while True:
                try:
                    time_value = int(input("Enter time in seconds (min: 5, max: 300): "))
                    if 5 <= time_value <= 300:
                        break
                    else:
                        print("Please enter a value between 5 and 300.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            value = time_value
        elif mode_choice == '2':
            mode = 'questions'
            while True:
                try:
                    question_count = int(input("Enter number of questions (min: 1, max: 100): "))
                    if 1 <= question_count <= 100:
                        break
                    else:
                        print("Please enter a value between 1 and 100.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            value = question_count
        else:
            print("Invalid choice. Defaulting to time mode with 20 seconds.")
            mode = 'time'
            value = 20

        factory = QuestionFactory(category, level)
        game = Game(player_name, factory, mode=mode, value=value)
        final_score = game.run()

        print(f"\nRound over, {player_name}! Your score for this round is {final_score}")
        highscore_manager.add_score(player_name, final_score, category, level)
        highscore_manager.display(highscore_manager.load())
        
        input("\nPress Enter to return to the main menu...")

if __name__ == "__main__":
    main()
