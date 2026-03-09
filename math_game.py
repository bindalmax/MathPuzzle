import json
import os
import time
import threading
from questions import QuestionFactory

# --- Highscore Management ---
class HighscoreManager:
    def __init__(self, filename="highscores.json"):
        self.filename = filename
    def load(self):
        if not os.path.exists(self.filename): return []
        with open(self.filename, 'r') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return []
    def save(self, highscores):
        with open(self.filename, 'w') as f: json.dump(highscores, f, indent=4)
    def add_score(self, name, score):
        highscores = self.load()
        highscores.append({'name': name, 'score': score})
        self.save(highscores)
        return highscores
    def display(self, highscores):
        print("\n--- High Scores ---")
        if not highscores:
            print("No high scores yet.")
            return
        sorted_highscores = sorted(highscores, key=lambda x: x['score'], reverse=True)
        for i, entry in enumerate(sorted_highscores[:5]):
            print(f"{i+1}. {entry['name']}: {entry['score']}")
        print("-------------------\n")

# --- Game Logic ---
class Game:
    def __init__(self, player_name, question_factory, duration=20):
        self.player_name = player_name
        self.question_factory = question_factory
        self.score = 0
        self.duration = duration
        self.game_over = threading.Event()

    def timer_thread(self):
        time.sleep(self.duration)
        self.game_over.set()
        print("\nTime's up!")

    def run(self):
        print(f"\nStarting game for {self.player_name}! You have {self.duration} seconds.")
        
        timer = threading.Thread(target=self.timer_thread)
        timer.daemon = True
        timer.start()

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
            except NotImplementedError as e:
                print(e)
                break
            except (ValueError, EOFError):
                if not self.game_over.is_set():
                    print("Invalid input. Please enter a number or 'quit'.")
                break

        if timer.is_alive():
            timer.join(timeout=1)
            
        return self.score

# --- Main Execution ---
def main():
    player_name = input("Enter your name: ")

    print("Select a question category:")
    print("1. Basic Arithmetic (+, -, *, /)")
    print("2. Decimals and Fractions")
    print("3. Percentages")
    print("4. Profit and Loss")
    print("5. Algebra")
    
    category_map = {"1": "basic", "2": "decimal", "3": "percentage", "4": "profit_loss", "5": "algebra"}
    while True:
        choice = input("Enter your choice (1-5): ")
        if choice in category_map:
            category = category_map[choice]
            break
        else:
            print("Invalid choice. Please select a valid category.")

    while True:
        level = input("Choose a difficulty (Easy, Medium, Hard): ").lower()
        if level in ['easy', 'medium', 'hard']:
            break
        else:
            print("Invalid difficulty.")

    factory = QuestionFactory(category, level)
    game = Game(player_name, factory)
    final_score = game.run()

    print(f"\nGame over, {player_name}! Your final score is {final_score}")

    highscore_manager = HighscoreManager()
    highscores = highscore_manager.add_score(player_name, final_score)
    highscore_manager.display(highscores)

if __name__ == "__main__":
    main()
