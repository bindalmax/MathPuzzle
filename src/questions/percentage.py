import random
import math
from .base import Question

class PercentageQuestion(Question):
    def generate(self, difficulty):
        question = ""
        answer = 0
        is_integer = True

        if difficulty == 'easy':
            percent = random.choice([10, 20, 25, 50, 75])
            number = random.randint(1, 20) * 10
            answer = (percent / 100) * number
            question = f"What is {percent}% of {number}? "
            is_integer = (answer == int(answer))
        
        elif difficulty == 'medium':
            q_type = random.choice(['percentage_of', 'what_percent'])

            if q_type == 'percentage_of':
                percent = random.choice([10, 20, 25, 50])
                factor = 100 // percent
                base = random.randint(1, 20)
                number = base * factor
                answer = (percent * number) // 100
                question = f"What is {percent}% of {number}? "
            else: # what_percent
                percent = random.choice([10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90])
                factor = 100 // math.gcd(percent, 100)
                whole = random.randint(1, 10) * factor
                part = int((percent * whole) / 100)
                
                answer = percent
                question = f"What percent of {whole} is {part}? "
            is_integer = True

        elif difficulty == 'hard':
            q_type = random.choice(['percentage_of', 'what_percent', 'increase_decrease'])

            if q_type == 'percentage_of':
                percent = random.randint(1, 100)
                number = random.randint(100, 1000)
                answer = round((percent / 100) * number, 2)
                question = f"What is {percent}% of {number}? "
            elif q_type == 'what_percent':
                number = random.randint(100, 1000)
                part = random.randint(1, number)
                answer = round((part / number) * 100, 2)
                question = f"What percent of {number} is {part}? "
            else: # increase_decrease
                original = random.randint(100, 1000)
                percent = random.choice([10, 15, 20, 25, 30, 50])
                increase = random.choice([True, False])

                if increase:
                    new_value = original * (1 + percent / 100)
                    question = f"If {original} is increased by {percent}%, what is the new value? "
                    answer = round(new_value, 2)
                else:
                    new_value = original * (1 - percent / 100)
                    question = f"If {original} is decreased by {percent}%, what is the new value? "
                    answer = round(new_value, 2)
            is_integer = False

        else:
            raise NotImplementedError(f"Percentage questions for {difficulty} difficulty are not yet implemented.")

        # MCQ for all difficulties
        choices = self.generate_choices(answer, is_integer=is_integer)
        return question, answer, choices
