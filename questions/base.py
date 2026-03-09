from abc import ABC, abstractmethod

class Question(ABC):
    """Abstract base class for a question."""
    @abstractmethod
    def generate(self, difficulty):
        """Generates a question string and its corresponding answer."""
        pass

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
