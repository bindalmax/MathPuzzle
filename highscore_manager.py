import json
import os
import time

class HighscoreManager:
    def __init__(self, filename="highscores.json"):
        self.filename = filename

    def load(self):
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save(self, highscores):
        with open(self.filename, 'w') as f:
            json.dump(highscores, f, indent=4)

    def add_score(self, name, score, category="unknown", difficulty="unknown"):
        highscores = self.load()
        highscores.append({
            'name': name,
            'score': score,
            'category': category,
            'difficulty': difficulty,
            'timestamp': time.time()
        })
        self.save(highscores)
        return highscores

    def display(self, highscores):
        print("\n--- High Scores ---")
        if not highscores:
            print("No high scores yet.")
            return
        sorted_highscores = sorted(highscores, key=lambda x: x['score'], reverse=True)
        for i, entry in enumerate(sorted_highscores[:5]):
            category = entry.get('category', 'unknown').replace('_', ' ').title()
            difficulty = entry.get('difficulty', 'unknown').title()
            print(f"{i+1}. {entry['name']}: {entry['score']} ({category}, {difficulty})")
        print("-------------------\n")
