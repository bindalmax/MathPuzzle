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
        """Generates 3 distractors and returns a shuffled list of 4 choices."""
        choices = {correct_answer}
        
        while len(choices) < 4:
            if is_integer:
                # Generate a close number
                offset = random.choice([-1, 1]) * random.randint(1, 10)
                distractor = correct_answer + offset
            else:
                # Float logic
                offset = random.choice([-1, 1]) * random.uniform(0.1, 5.0)
                distractor = round(correct_answer + offset, 2)
            
            choices.add(distractor)
            
        choices_list = list(choices)
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

        categories = {
            "basic": BasicArithmeticQuestion,
            "decimal": DecimalFractionQuestion,
            "percentage": PercentageQuestion,
            "profit_loss": ProfitLossQuestion,
            "algebra": AlgebraQuestion,
        }
        return categories.get(self.category)

    def create_question(self):
        if not self.question_class:
            raise ValueError("Invalid question category selected.")
        return self.question_class().generate(self.difficulty)
