import random
from .base import Question

class ProfitLossQuestion(Question):
    def generate(self, difficulty):
        if difficulty == 'easy':
            cost_price = random.randint(10, 100)
            sell_price = random.randint(cost_price - 20, cost_price + 20)

            if sell_price > cost_price:
                profit = sell_price - cost_price
                question = f"A toy is bought for ${cost_price} and sold for ${sell_price}. What is the profit? "
                return question, profit
            else:
                loss = cost_price - sell_price
                question = f"A toy is bought for ${cost_price} and sold for ${sell_price}. What is the loss? "
                return question, loss
        else:
            raise NotImplementedError(f"Profit and Loss questions for {difficulty} difficulty are not yet implemented.")
