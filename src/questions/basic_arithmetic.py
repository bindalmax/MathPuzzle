import random
from .base import Question

class BasicArithmeticQuestion(Question):
    def generate(self, difficulty):
        operator = random.choice(['+', '-', '*', '/'])
        if operator == '*':
            ranges = {'easy': (1, 10), 'medium': (1, 15), 'hard': (1, 20)}
        elif operator == '/':
            ranges = {'easy': (1, 10), 'medium': (10, 50), 'hard': (50, 100)}
        else:
            ranges = {'easy': (1, 100), 'medium': (100, 1000), 'hard': (1000, 9999)}
        
        low, high = ranges[difficulty]
        num1, num2 = random.randint(low, high), random.randint(low, high)

        question = ""
        answer = 0

        if operator == '+':
            question = f"What is {num1} + {num2}? "
            answer = num1 + num2
        elif operator == '-':
            if num1 < num2: num1, num2 = num2, num1
            question = f"What is {num1} - {num2}? "
            answer = num1 - num2
        elif operator == '*':
            question = f"What is {num1} * {num2}? "
            answer = num1 * num2
        else: # '/'
            num1 = num1 * num2
            question = f"What is {num1} / {num2}? "
            answer = num1 // num2

        # MCQ for all difficulties
        choices = self.generate_choices(answer, is_integer=True)
        return question, answer, choices
