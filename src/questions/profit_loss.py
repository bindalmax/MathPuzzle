import random
from .base import Question

class ProfitLossQuestion(Question):
    def generate(self, difficulty):
        question = ""
        answer = 0
        is_integer = True

        if difficulty == 'easy':
            cost_price = random.randint(10, 100)
            sell_price = random.randint(cost_price - 20, cost_price + 20)

            if sell_price > cost_price:
                profit = sell_price - cost_price
                question = f"A toy is bought for ${cost_price} and sold for ${sell_price}. What is the profit? "
                answer = profit
            else:
                loss = cost_price - sell_price
                question = f"A toy is bought for ${cost_price} and sold for ${sell_price}. What is the loss? "
                answer = loss
            is_integer = True

        elif difficulty == 'medium':
            cost_price = random.randint(100, 1000)
            profit_loss_percent = random.randint(5, 50)
            is_profit = random.choice([True, False])

            if is_profit:
                profit = (profit_loss_percent * cost_price) // 100
                sell_price = cost_price + profit
                question = f"A gadget costs ${cost_price} and is sold for ${sell_price}. What is the profit percentage? "
                answer = profit_loss_percent
            else:
                loss = (profit_loss_percent * cost_price) // 100
                sell_price = cost_price - loss
                question = f"A gadget costs ${cost_price} and is sold for ${sell_price}. What is the loss percentage? "
                answer = profit_loss_percent
            is_integer = True

        elif difficulty == 'hard':
            q_type = random.choice(['discount', 'multiple'])

            if q_type == 'discount':
                original_price = random.randint(500, 2000)
                discount_percent = random.choice([10, 15, 20, 25, 30, 40, 50])
                discount_amount = (discount_percent / 100) * original_price
                final_price = original_price - discount_amount
                question = f"An item originally costs ${original_price}. After a {discount_percent}% discount, what is the final price? "
                answer = round(final_price, 2)
                is_integer = False
            else: # multiple transactions
                cost1 = random.randint(100, 500)
                sell1 = random.randint(int(cost1 * 0.9), int(cost1 * 1.3))
                cost2 = random.randint(100, 500)
                sell2 = random.randint(int(cost2 * 0.9), int(cost2 * 1.3))

                total_cost = cost1 + cost2
                total_sell = sell1 + sell2

                if total_sell > total_cost:
                    profit = total_sell - total_cost
                    question = f"Item 1: bought ${cost1}, sold ${sell1}. Item 2: bought ${cost2}, sold ${sell2}. What is the total profit? "
                    answer = profit
                else:
                    loss = total_cost - total_sell
                    question = f"Item 1: bought ${cost1}, sold ${sell1}. Item 2: bought ${cost2}, sold ${sell2}. What is the total loss? "
                    answer = loss
                is_integer = True
        else:
            raise NotImplementedError(f"Profit and Loss questions for {difficulty} difficulty are not yet implemented.")

        # MCQ for all difficulties
        choices = self.generate_choices(answer, is_integer=is_integer)
        return question, answer, choices
