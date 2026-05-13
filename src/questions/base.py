import random
from abc import ABC, abstractmethod

class Question(ABC):
    """Abstract base class for a question."""
    @abstractmethod
    def generate(self, difficulty):
        """
        Generates a question string, its corresponding answer, and optional choices.
        Returns:
            (question_text, answer, choices)
            - choices: List of 4 options if MCQ, else None.
        """
        pass

    def generate_choices(self, correct_answer, is_integer=True):
        """Generates 3 distractors and returns a shuffled list of 4 choices.
        """
        choices = {correct_answer}
        attempts = 0
        while len(choices) < 4 and attempts < 10:
            attempts += 1
            if is_integer:
                offset = random.choice([-1, 1]) * random.randint(1, 10)
                distractor = int(correct_answer) + offset
            else:
                offset = random.choice([-1, 1]) * random.uniform(0.1, 5.0)
                distractor = round(float(correct_answer) + float(offset), 2)
            choices.add(distractor)

        # Fill deterministically
        i = 1
        while len(choices) < 4:
            if is_integer:
                distractor = int(correct_answer) + i
            else:
                distractor = round(float(correct_answer) + i * 0.5, 2)
            choices.add(distractor)
            i += 1

        # Final formatting: ensure all choices are consistent
        if not is_integer:
            formatted_choices = [float(f"{c:.2f}") for c in choices]
            choices_list = list(set(formatted_choices))
        else:
            choices_list = list(choices)
            
        # Ensure we always have 4 choices even if set resulted in fewer
        while len(choices_list) < 4:
            choices_list.append(choices_list[-1] + (1 if is_integer else 0.5))

        random.shuffle(choices_list)
        return choices_list

class QuestionFactory:
    """Factory to create question objects based on category."""
    def __init__(self, category, difficulty):
        self.category = category
        self.difficulty = difficulty
        self.question_class = self._get_question_class()

    def _get_question_class(self):
        # Import question types locally to prevent circular imports
        from .basic_arithmetic import BasicArithmeticQuestion
        from .decimal_fraction import DecimalFractionQuestion
        from .percentage import PercentageQuestion
        from .profit_loss import ProfitLossQuestion
        from .algebra import AlgebraQuestion
        from .startup import StartupQuestion

        # Support both short keys and API-friendly names
        categories = {
            "basic": BasicArithmeticQuestion,
            "basic_arithmetic": BasicArithmeticQuestion,
            "decimal": DecimalFractionQuestion,
            "decimal_fraction": DecimalFractionQuestion,
            "percentage": PercentageQuestion,
            "profit": ProfitLossQuestion,
            "profit_loss": ProfitLossQuestion,
            "algebra": AlgebraQuestion,
            "startup": StartupQuestion,
        }
        return categories.get(self.category)

    def create_question(self):
        if not self.question_class:
            raise ValueError("Invalid question category selected.")
        return self.question_class().generate(self.difficulty)
