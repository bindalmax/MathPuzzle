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
            return question, answer, None

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
                # Equation: x / a = b
                # We want integer answer x.
                # Pick b (result) and a (divisor).
                b = random.randint(2, 10)
                a = random.randint(2, 10)
                x = a * b
                question = f"Solve for x: x / {a} = {b}"
                answer = x
            
            choices = self.generate_choices(answer, is_integer=True)
            return question, answer, choices

        elif difficulty == 'hard':
            eq_type = random.choice(['fraction', 'two_var'])

            if eq_type == 'fraction':
                # Equation: (num/den)x + a = b
                # We want integer x
                x = random.randint(4, 12)
                # Ensure x is divisible by den for cleaner arithmetic? 
                # Not strictly necessary if we calculate b correctly, but helps avoid float issues in verification if we were verifying.
                # But here we construct b from x.
                
                coeff_num = random.randint(1, 3)
                coeff_den = random.randint(2, 4)
                
                # To ensure (num/den)*x is integer (optional but nice), let's retry x
                # x = random.randint(1, 5) * coeff_den 
                # Keeping original logic for now which didn't ensure integer intermediate, but b is fraction.
                
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
            
            choices = self.generate_choices(answer, is_integer=True)
            return question, answer, choices

        else:
            raise NotImplementedError(f"Algebra questions for {difficulty} difficulty are not yet implemented.")
