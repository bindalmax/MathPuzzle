import random
from .base import Question

class PercentageQuestion(Question):
    def generate(self, difficulty):
        if difficulty == 'easy':
            percent = random.choice([10, 20, 25, 50, 75])
            number = random.randint(1, 20) * 10
            answer = (percent / 100) * number
            return f"What is {percent}% of {number}? ", answer
        elif difficulty == 'medium':
            q_type = random.choice(['percentage_of', 'what_percent'])

            if q_type == 'percentage_of':
                percent = random.choice([15, 25, 30, 40, 60, 75, 80, 90])
                number = random.randint(10, 100) * 10  # 100 to 1000
                answer = (percent / 100) * number
                return f"What is {percent}% of {number}? ", answer
            else: # what_percent
                number = random.randint(10, 100) * 10
                part = random.randint(1, number)
                percent = (part / number) * 100
                return f"What percent of {number} is {part}? ", round(percent, 2)
        elif difficulty == 'hard':
            q_type = random.choice(['percentage_of', 'what_percent', 'increase_decrease'])

            if q_type == 'percentage_of':
                percent = random.randint(1, 100)
                number = random.randint(100, 1000)
                answer = (percent / 100) * number
                return f"What is {percent}% of {number}? ", round(answer, 2)
            elif q_type == 'what_percent':
                number = random.randint(100, 1000)
                part = random.randint(1, number)
                percent = (part / number) * 100
                return f"What percent of {number} is {part}? ", round(percent, 2)
            else: # increase_decrease
                original = random.randint(100, 1000)
                percent = random.choice([10, 15, 20, 25, 30, 50])
                increase = random.choice([True, False])

                if increase:
                    new_value = original * (1 + percent / 100)
                    return f"If {original} is increased by {percent}%, what is the new value? ", round(new_value, 2)
                else:
                    new_value = original * (1 - percent / 100)
                    return f"If {original} is decreased by {percent}%, what is the new value? ", round(new_value, 2)
        else:
            raise NotImplementedError(f"Percentage questions for {difficulty} difficulty are not yet implemented.")
