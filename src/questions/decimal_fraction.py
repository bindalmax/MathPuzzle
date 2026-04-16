import random
from fractions import Fraction
from .base import Question

class DecimalFractionQuestion(Question):
    def generate(self, difficulty):
        question = ""
        answer = 0.0

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
                answer = round(answer, 2)

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
                
                answer = round(float(result_fraction), 2)

        elif difficulty == 'medium':
            q_type = random.choice(['decimal', 'fraction', 'mixed'])
            operator = random.choice(['+', '-', '*', '/'])

            if q_type == 'decimal':
                num1 = round(random.uniform(0.1, 99.9), 1)
                num2 = round(random.uniform(0.1, 99.9), 1)

                if operator == '+':
                    answer = num1 + num2
                    question = f"What is {num1} + {num2}? "
                elif operator == '-':
                    if num1 < num2: num1, num2 = num2, num1
                    answer = num1 - num2
                    question = f"What is {num1} - {num2}? "
                elif operator == '*':
                    answer = num1 * num2
                    question = f"What is {num1} * {num2}? "
                else: # '/'
                    answer = num1 / num2
                    question = f"What is {num1} / {num2}? (Round to 2 decimal places) "
                answer = round(answer, 2)

            elif q_type == 'fraction':
                fractions_pool = [Fraction(1, 2), Fraction(1, 3), Fraction(2, 3), Fraction(1, 4), Fraction(3, 4), Fraction(1, 5), Fraction(2, 5), Fraction(3, 5), Fraction(4, 5)]
                f1 = random.choice(fractions_pool)
                f2 = random.choice(fractions_pool)

                if operator == '+':
                    result_fraction = f1 + f2
                    question = f"What is {f1} + {f2}? (Answer as decimal, round to 2 places) "
                elif operator == '-':
                    if f1 < f2: f1, f2 = f2, f1
                    result_fraction = f1 - f2
                    question = f"What is {f1} - {f2}? (Answer as decimal, round to 2 places) "
                elif operator == '*':
                    result_fraction = f1 * f2
                    question = f"What is {f1} * {f2}? (Answer as decimal, round to 2 places) "
                else: # '/'
                    result_fraction = f1 / f2
                    question = f"What is {f1} / {f2}? (Answer as decimal, round to 2 places) "
                answer = round(float(result_fraction), 2)

            else: # mixed
                whole1 = random.randint(1, 10)
                frac1 = random.choice([Fraction(1, 2), Fraction(1, 3), Fraction(2, 3), Fraction(1, 4), Fraction(3, 4)])
                mixed1 = whole1 + frac1

                whole2 = random.randint(1, 10)
                frac2 = random.choice([Fraction(1, 2), Fraction(1, 3), Fraction(2, 3), Fraction(1, 4), Fraction(3, 4)])
                mixed2 = whole2 + frac2

                if operator == '+':
                    result = mixed1 + mixed2
                    question = f"What is {whole1} {frac1} + {whole2} {frac2}? (Answer as decimal, round to 2 places) "
                elif operator == '-':
                    if mixed1 < mixed2: mixed1, mixed2, whole1, frac1, whole2, frac2 = mixed2, mixed1, whole2, frac2, whole1, frac1
                    result = mixed1 - mixed2
                    question = f"What is {whole1} {frac1} - {whole2} {frac2}? (Answer as decimal, round to 2 places) "
                elif operator == '*':
                    result = mixed1 * mixed2
                    question = f"What is {whole1} {frac1} * {whole2} {frac2}? (Answer as decimal, round to 2 places) "
                else: # '/'
                    result = mixed1 / mixed2
                    question = f"What is {whole1} {frac1} / {whole2} {frac2}? (Answer as decimal, round to 2 places) "
                answer = round(float(result), 2)

        elif difficulty == 'hard':
            q_type = random.choice(['decimal', 'fraction', 'mixed'])
            operator = random.choice(['+', '-', '*', '/'])

            if q_type == 'decimal':
                num1 = round(random.uniform(0.01, 999.99), 2)
                num2 = round(random.uniform(0.01, 999.99), 2)

                if operator == '+':
                    answer = num1 + num2
                    question = f"What is {num1} + {num2}? "
                elif operator == '-':
                    if num1 < num2: num1, num2 = num2, num1
                    answer = num1 - num2
                    question = f"What is {num1} - {num2}? "
                elif operator == '*':
                    answer = num1 * num2
                    question = f"What is {num1} * {num2}? (Round to 2 decimal places) "
                else: # '/'
                    answer = num1 / num2
                    question = f"What is {num1} / {num2}? (Round to 2 decimal places) "
                answer = round(answer, 2)

            elif q_type == 'fraction':
                fractions_pool = [Fraction(i, j) for j in range(2, 11) for i in range(1, j)]
                f1 = random.choice(fractions_pool)
                f2 = random.choice(fractions_pool)

                if operator == '+':
                    result_fraction = f1 + f2
                    question = f"What is {f1} + {f2}? (Answer as decimal, round to 2 places) "
                elif operator == '-':
                    if f1 < f2: f1, f2 = f2, f1
                    result_fraction = f1 - f2
                    question = f"What is {f1} - {f2}? (Answer as decimal, round to 2 places) "
                elif operator == '*':
                    result_fraction = f1 * f2
                    question = f"What is {f1} * {f2}? (Answer as decimal, round to 2 places) "
                else: # '/'
                    result_fraction = f1 / f2
                    question = f"What is {f1} / {f2}? (Answer as decimal, round to 2 places) "
                answer = round(float(result_fraction), 2)

            else: # mixed
                whole1 = random.randint(10, 50)
                frac1 = random.choice([Fraction(i, j) for j in range(2, 11) for i in range(1, j)])
                mixed1 = whole1 + frac1

                whole2 = random.randint(10, 50)
                frac2 = random.choice([Fraction(i, j) for j in range(2, 11) for i in range(1, j)])
                mixed2 = whole2 + frac2

                if operator == '+':
                    result = mixed1 + mixed2
                    question = f"What is {whole1} {frac1} + {whole2} {frac2}? (Answer as decimal, round to 2 places) "
                elif operator == '-':
                    if mixed1 < mixed2: mixed1, mixed2, whole1, frac1, whole2, frac2 = mixed2, mixed1, whole2, frac2, whole1, frac1
                    result = mixed1 - mixed2
                    question = f"What is {whole1} {frac1} - {whole2} {frac2}? (Answer as decimal, round to 2 places) "
                elif operator == '*':
                    result = mixed1 * mixed2
                    question = f"What is {whole1} {frac1} * {whole2} {frac2}? (Answer as decimal, round to 2 places) "
                else: # '/'
                    result = mixed1 / mixed2
                    question = f"What is {whole1} {frac1} / {whole2} {frac2}? (Answer as decimal, round to 2 places) "
                answer = round(float(result), 2)
        else:
            raise NotImplementedError(f"Decimal and Fraction questions for {difficulty} difficulty are not yet implemented.")

        # MCQ for all difficulties
        choices = self.generate_choices(answer, is_integer=False)
        return question, answer, choices
