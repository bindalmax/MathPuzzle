import random
from .base import Question

class AlgebraQuestion(Question):
    def generate(self, difficulty):
        if difficulty == 'easy':
            x = random.randint(1, 10)
            a = random.randint(1, 10)
            b = x + a
            return f"Solve for x: x + {a} = {b}", x
        else:
            raise NotImplementedError(f"Algebra questions for {difficulty} difficulty are not yet implemented.")
