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
                question, answer = self.question_factory.create_question()
                user_input = input(question)
                
                if self.game_over.is_set():
                    break

                if user_input.lower() == 'quit':
                    self.game_over.set()
                    break
                
                user_answer = float(user_input)
                
                if abs(user_answer - answer) < 0.01:
                    print("Correct!")
                    self.score += 1
                else:
                    print(f"Wrong! The correct answer is {answer}")

                questions_answered += 1

                # Check if question count reached
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
        print("6. Quit Game")
        
        choice = input("Enter your choice (1-6): ")

        if choice == '6':
            print("\nThanks for playing!")
            break

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
