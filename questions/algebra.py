import random
from .base import Question
from fractions import Fraction

class AlgebraQuestion(Question):
    def generate(self, difficulty):
        if difficulty == 'easy':
            x = random.randint(1, 10)
            a = random.randint(1, 10)
            b = x + a
            return f"Solve for x: x + {a} = {b}", x
        elif difficulty == 'medium':
            eq_type = random.choice(['subtraction', 'multiplication', 'division'])

            if eq_type == 'subtraction':
                x = random.randint(5, 20)
                a = random.randint(1, 10)
                b = x - a
                return f"Solve for x: x - {a} = {b}", x
            elif eq_type == 'multiplication':
                x = random.randint(2, 10)
                a = random.randint(2, 5)
                b = x * a
                return f"Solve for x: {a}x = {b}", x
            else: # division
                b = random.randint(10, 50)
                a = random.randint(2, 10)
                x = b // a  # integer division
                b = x * a
                return f"Solve for x: x / {a} = {x}", x
        elif difficulty == 'hard':
            eq_type = random.choice(['fraction', 'two_var'])

            if eq_type == 'fraction':
                # Simple fractional coefficient
                coeff_num = random.randint(1, 3)
                coeff_den = random.randint(2, 4)
                coeff = Fraction(coeff_num, coeff_den)
                x = random.randint(4, 12)
                a = random.randint(1, 5)
                b = coeff * x + a
                return f"Solve for x: ({coeff_num}/{coeff_den})x + {a} = {b}", x
            else: # two_var (simple system)
                x = random.randint(1, 5)
                y = random.randint(1, 5)
                sum_xy = x + y
                diff_xy = abs(x - y)
                if x > y:
                    return f"If x + y = {sum_xy} and x - y = {diff_xy}, what is x? ", x
                else:
                    return f"If x + y = {sum_xy} and y - x = {diff_xy}, what is x? ", x
        else:
            raise NotImplementedError(f"Algebra questions for {difficulty} difficulty are not yet implemented.")
