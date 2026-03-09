import random
from .base import Question

class PercentageQuestion(Question):
    def generate(self, difficulty):
        if difficulty == 'easy':
            percent = random.choice([10, 20, 25, 50, 75])
            number = random.randint(1, 20) * 10
            answer = (percent / 100) * number
            return f"What is {percent}% of {number}? ", answer
        else:
            raise NotImplementedError(f"Percentage questions for {difficulty} difficulty are not yet implemented.")
