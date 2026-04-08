import random
from .base import Question
from fractions import Fraction

class AlgebraQuestion(Question):
    def generate(self, difficulty):
        question = ""
        answer = 0

        if difficulty == 'easy':
            x = random.randint(1, 10)
            a = random.randint(1, 10)
            b = x + a
            question = f"Solve for x: x + {a} = {b}"
            answer = x

        elif difficulty == 'medium':
            eq_type = random.choice(['subtraction', 'multiplication', 'division'])

            if eq_type == 'subtraction':
                x = random.randint(5, 20)
                a = random.randint(1, 10)
                b = x - a
                question = f"Solve for x: x - {a} = {b}"
                answer = x
            elif eq_type == 'multiplication':
                x = random.randint(2, 10)
                a = random.randint(2, 5)
                b = x * a
                question = f"Solve for x: {a}x = {b}"
                answer = x
            else: # division
                b = random.randint(2, 10)
                a = random.randint(2, 10)
                x = a * b
                question = f"Solve for x: x / {a} = {b}"
                answer = x

        elif difficulty == 'hard':
            eq_type = random.choice(['fraction', 'two_var'])

            if eq_type == 'fraction':
                x = random.randint(4, 12)
                coeff_num = random.randint(1, 3)
                coeff_den = random.randint(2, 4)
                
                coeff = Fraction(coeff_num, coeff_den)
                a = random.randint(1, 5)
                b = coeff * x + a
                question = f"Solve for x: ({coeff_num}/{coeff_den})x + {a} = {b}"
                answer = x
            else: # two_var (simple system)
                x = random.randint(1, 5)
                y = random.randint(1, 5)
                sum_xy = x + y
                diff_xy = abs(x - y)
                if x > y:
                    question = f"If x + y = {sum_xy} and x - y = {diff_xy}, what is x? "
                else:
                    question = f"If x + y = {sum_xy} and y - x = {diff_xy}, what is x? "
                answer = x
        else:
            raise NotImplementedError(f"Algebra questions for {difficulty} difficulty are not yet implemented.")

        # MCQ for all difficulties
        choices = self.generate_choices(answer, is_integer=True)
        return question, answer, choices
