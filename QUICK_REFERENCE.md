# Quick Reference Guide
## Medium Mode Question Logic
### PercentageQuestion - Medium Mode
#### Type 1: Percentage Of (50% chance)
```
percent = randomly chosen from [15, 25, 30, 40, 60, 75, 80, 90]
number = random between 100-1000
answer = (percent / 100) × number
Example: "What is 40% of 250?" → 100.0
```
#### Type 2: What Percent (50% chance)  
```
number = random between 100-1000 (the whole)
part = random between 1-number (the part)
answer = (part / number) × 100
Example: "What percent of 800 is 320?" → 40.0
```
---
### ProfitLossQuestion - Medium Mode
#### Profit Scenario (when sell > cost)
```
cost_price = random between 100-1000
sell_price = random between (cost × 0.8) to (cost × 1.5)
profit% = ((sell - cost) / cost) × 100
Example: "Buy $500, sell $650. Profit %?" → 30.0
```
#### Loss Scenario (when sell ≤ cost)
```
cost_price = random between 100-1000
sell_price = random between (cost × 0.8) to (cost × 1.# Quick Reference Guide
## Medium Mode Question Logic
### PercentageQuestion - Me?# Medium Mode QuestioFo### PercentageQuestion - Med E#### Type 1: Percentage Of (50% cha--```
percent = randomly chosen from [15 npebenumber = random between 100-1000
answer = (percent / 100) × n00answer = (percent / 100) ×| ProfExample: "What is 40% of 250?" ? ```
#### Type 2: What Percent (50% chan| ##co```
number = random between 100-1000 (t ?u10part = random between 1-number (the part)
apeanswer = (part / number) × 100
Example:--Example: "What percent of 800 (n```
---
### ProfitLossQuestion - Medium Mode
#ge--pe##en#### Profit Scenario (when sell > c40```
cost_price = random between 100-10(ccot)sell_price = random between (cost ?Pprofit% = ((sell - cost) / cost) × 100
Example: "Buy $50f Example: "Buy $500, sell $650. Profit si```
#### Loss Scenario (when sell ≤ cost)
```
cRD##??```
cost_price = random between 100-10??o?ell_price = random between (cost Ô?## Medium Mode Question Logic
### PercentageQuestion - Me?# Medium Mode Ques %### PercentageQuestion - Me?rpercent = randomly chosen from [15 npebenumber = random between 100-1000
answer = (percent / 100) × n00answer = (percent ulanswer = (percent / 100) × n00answer = (percent / 100) ×| ProfExampleit#### Type 2: What Percent (50% chan| ##co```
number = random between 100-1000 (t ?u10part = random b0?number = random between 100-1000 (t ?u10paWhapeanswer = (part / number) × 100
Example:--Example: "What percent of 800 (n```
eaExample:--Example: "What percent Lo---
### ProfitLossQuestion - Medium Mode
#ge "##y #ge--pe##en#### Profit Scenario (whescost_price = random between 100-10(ccot)sell_pricefiExample: "Buy $50f Example: "Buy $500, sell $650. Profit si```
#### Loss Scenario (when sell ≤ cost)
```
cRD##??`e #### Loss Scenario (when sell ≤ cost)
```
cRD##??```
cost_pme```
cRD##??```
cost_price = random bet TcRe cost_pricon### PercentageQuestion - Me?# Medium Mode Ques %### PercentageQuestion - Me?rpercent = randomly chosenREanswer = (pcd /Users/keshavbindal/IdeaProjects/AIHandsOn && echo "=== Documentation Files Created ===" && ls -1 *.md && echo -e "\n=== Tests Status ===" && python -m unittest test_math_game.py test_app.py 2>&1 | tail -3
cd /Users/keshavbindal/IdeaProjects/AIHandsOn && ls -1 *.md
cd /Users/keshavbindal/IdeaProjects/AIHandsOn && python -m unittest test_math_game.py test_app.py
cd /Users/keshavbindal/IdeaProjects/AIHandsOn && python -m unittest test_math_game.py test_app.py 2>&1 | tail -10
cd /Users/keshavbindal/IdeaProjects/AIHandsOn && python -m unittest test_math_game.py test_app.py 2>&1
cd /Users/keshavbindal/IdeaProjects/AIHandsOn && python -m unittest test_math_game.py test_app.py -v 2>&1 | head -40
cd /Users/keshavbindal/IdeaProjects/AIHandsOn && python -c "import unittest; unittest.main(module='test_math_game', exit=False, argv=['test', '-v'])" 2>&1 | tail -20
cd /Users/keshavbindal/IdeaProjects/AIHandsOn && python3 -m pytest test_math_game.py::TestPercentageQuestion::test_medium_percentage_of -v 2>&1 || python3 -m unittest test_math_game.TestPercentageQuestion.test_medium_percentage_of -v 2>&1
cd /Users/keshavbindal/IdeaProjects/AIHandsOn && python3 test_math_game.py 2>&1 | tail -5
cd /Users/keshavbindal/IdeaProjects/AIHandsOn && python3 << 'EOF'
from questions.percentage import PercentageQuestion
from questions.profit_loss import ProfitLossQuestion
# Test percentage medium
pq = PercentageQuestion()
for i in range(3):
    q, a = pq.generate('medium')
    print(f"Percentage: {q} -> {a} (type: {type(a).__name__})")
print()
# Test profit/loss medium  
pl = ProfitLossQuestion()
for i in range(3):
    q, a = pl.generate('medium')
    print(f"ProfitLoss: {q} -> {a} (type: {type(a).__name__})")
