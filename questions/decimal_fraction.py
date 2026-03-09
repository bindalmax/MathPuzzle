import random
from fractions import Fraction
from .base import Question

class DecimalFractionQuestion(Question):
    def generate(self, difficulty):
        if difficulty == 'easy':
            q_type = random.choice(['decimal', 'fraction'])
            operator = random.choice(['+', '-'])

            if q_type == 'decimal':
                num1 = round(random.uniform(0.1, 9.9), 1)
                num2 = round(random.uniform(0.1, 9.9), 1)
                
                if operator == '+':
                    answer = num1 + num2
                    question = f"What is {num1} + {num2}? "
                else:
                    if num1 < num2: num1, num2 = num2, num1
                    answer = num1 - num2
                    question = f"What is {num1} - {num2}? "
                return question, round(answer, 2)

            else: # fraction
                fractions_pool = [Fraction(1, 2), Fraction(1, 4), Fraction(3, 4), Fraction(1, 3), Fraction(2, 3)]
                f1 = random.choice(fractions_pool)
                f2 = random.choice(fractions_pool)

                if operator == '+':
                    result_fraction = f1 + f2
                    question = f"What is {f1} + {f2}? (Answer as decimal, round to 2 places) "
                else:
                    if f1 < f2: f1, f2 = f2, f1
                    result_fraction = f1 - f2
                    question = f"What is {f1} - {f2}? (Answer as decimal, round to 2 places) "
                
                return question, round(float(result_fraction), 2)
        else:
            raise NotImplementedError(f"Decimal and Fraction questions for {difficulty} difficulty are not yet implemented.")
