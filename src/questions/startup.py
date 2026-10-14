import random
import math
from .base import Question

class StartupQuestion(Question):
    _last_category = None

    def generate(self, difficulty):
        # We ignore difficulty for now as startup challenge is fixed to "medium" vibe but scales
        categories = [
            'market_analysis', 
            'resource_optimization', 
            'unit_economics', 
            'runway_management',
            'financial_planning'
        ]
        
        # Avoid repeating the last category
        available = [c for c in categories if c != StartupQuestion._last_category]
        q_type = random.choice(available)
        StartupQuestion._last_category = q_type

        if q_type == 'market_analysis':
            # Percentage based
            percent = random.choice([10, 15, 20, 25, 30, 40, 50])
            base_users = random.randint(1, 20) * 1000
            answer = (percent * base_users) // 100
            question = f"Market Analysis: Your landing page has {base_users:,} visitors. If your conversion rate is {percent}%, how many new signups (x) will you get? "
            is_integer = True

        elif q_type == 'resource_optimization':
            # Algebra based: ax = b
            cost_per_server = random.choice([2, 5, 10, 20])
            total_budget = random.randint(5, 50) * 20
            answer = total_budget // cost_per_server
            question = f"Resource Optimization: Each cloud server costs ${cost_per_server} per month. If your infrastructure budget is ${total_budget}, how many servers (x) can you deploy? "
            is_integer = True

        elif q_type == 'unit_economics':
            # Decimals/Fractions based
            cac = round(random.uniform(1.0, 5.0), 2)
            maintenance = round(random.uniform(0.1, 2.0), 2)
            answer = round(cac + maintenance, 2)
            question = f"Unit Economics: It costs ${cac:.2f} to acquire a user and ${maintenance:.2f} to maintain them. What is the total cost (x) per user? "
            is_integer = False

        elif q_type == 'runway_management':
            # Algebra/Subtraction based: x - a = b or a - x = b
            initial_cash = random.randint(10, 100) * 1000
            remaining_cash = random.randint(5, int(initial_cash/1000) - 1) * 1000
            answer = initial_cash - remaining_cash
            question = f"Runway Management: You started the month with ${initial_cash:,}. After paying your team, you have ${remaining_cash:,} left. What was your total burn (x) for the month? "
            is_integer = True

        else: # financial_planning
            # Profit/Loss based
            cost = random.randint(10, 50)
            markup = random.randint(5, 20)
            sell_price = cost + markup
            answer = round((markup / cost) * 100, 2)
            question = f"Financial Planning: Your product costs ${cost} to produce and you sell it for ${sell_price}. What is your profit margin percentage (x)? "
            is_integer = False

        choices = self.generate_choices(answer, is_integer=is_integer)
        return question, answer, choices
