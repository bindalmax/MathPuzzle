# Medium Mode Logic Explanation

## PercentageQuestion - Medium Mode

### Two Question Types (Randomly Selected):

#### 1. **"What is X% of Y?"** (Percentage Of)
**Purpose**: Direct percentage calculation with larger numbers

**Logic**:
```python
q_type = 'percentage_of'
percent = random.choice([15, 25, 30, 40, 60, 75, 80, 90])
number = random.randint(10, 100) * 10  # 100 to 1000
answer = (percent / 100) * number
```

**Example**:
- Percent: 25 (chosen from predefined list)
- Number: 350 (random between 100-1000)
- Question: "What is 25% of 350?"
- Calculation: (25 / 100) * 350 = 87.5
- Answer: 87.5

**Complexity vs Easy**:
- ✅ **Larger numbers**: 100-1000 (vs easy: 10-200)
- ✅ **More percentages**: 8 options (vs easy: 5 options)
- ✅ **More varied percents**: Includes 15, 30, 40, 60, 80, 90 (vs easy: only 10, 20, 25, 50, 75)

**Real-world Application**: Calculating discounts, tax, tips on larger amounts

---

#### 2. **"What percent of X is Y?"** (Reverse Percentage)
**Purpose**: Inverse thinking - finding percentage from part and whole

**Logic**:
```python
q_type = 'what_percent'
number = random.randint(10, 100) * 10  # 100 to 1000
part = random.randint(1, number)  # Part is always smaller than whole
percent = (part / number) * 100
return f"What percent of {number} is {part}? ", round(percent, 2)
```

**Example**:
- Whole number: 500
- Part: 150
- Question: "What percent of 500 is 150?"
- Calculation: (150 / 500) * 100 = 30%
- Answer: 30.0

**Complexity vs Easy**:
- ✅ **New question type**: Reverses the thinking (part/whole instead of percent/whole)
- ✅ **Larger ranges**: Numbers 100-1000 with varied parts
- ✅ **Decimal answers**: Results rounded to 2 decimal places (e.g., 33.33%)

**Real-world Application**: Calculating yield, growth rates, completion percentages

---

### Key Differences from Easy Mode:

| Aspect | Easy | Medium |
|--------|------|--------|
| **Number Range** | 10-200 | 100-1000 |
| **Question Types** | 1 (percentage_of only) | 2 (percentage_of, what_percent) |
| **Percent Values** | Fixed set: [10, 20, 25, 50, 75] | Expanded set: [15, 25, 30, 40, 60, 75, 80, 90] |
| **Answer Precision** | Integer result | Float with 2 decimal places |
| **Cognitive Load** | Simple calculation | Requires reverse thinking for part 2 |

---

## ProfitLossQuestion - Medium Mode

### Single Calculation Type with Two Outcomes:

**Purpose**: Calculate profit/loss percentage (more advanced than simple difference)

**Logic**:
```python
difficulty == 'medium':
    cost_price = random.randint(100, 1000)
    sell_price = random.randint(int(cost_price * 0.8), int(cost_price * 1.5))

    if sell_price > cost_price:
        profit = sell_price - cost_price
        profit_percent = (profit / cost_price) * 100
        return question, round(profit_percent, 2)
    else:
        loss = cost_price - sell_price
        loss_percent = (loss / cost_price) * 100
        return question, round(loss_percent, 2)
```

### Detailed Breakdown:

#### **Cost and Sell Price Generation**:
```python
cost_price = random.randint(100, 1000)
sell_price = random.randint(int(cost_price * 0.8), int(cost_price * 1.5))
```

- **Cost Price**: Random value between $100-$1000
- **Sell Price**: Controlled range ensuring realistic profit/loss:
  - Minimum: 80% of cost (20% loss)
  - Maximum: 150% of cost (50% profit)

**Example**:
- Cost Price: $500
- Sell Price range: $400 (0.8 × 500) to $750 (1.5 × 500)
- Actual Sell Price: $650

#### **Profit Scenario** (When sell_price > cost_price):
```python
profit = sell_price - cost_price  # e.g., 650 - 500 = 150
profit_percent = (profit / cost_price) * 100  # (150/500) × 100 = 30%
Question: "A gadget costs $500 and is sold for $650. What is the profit percentage?"
Answer: 30.0
```

**Formula**: `(Profit / Cost Price) × 100`

#### **Loss Scenario** (When sell_price ≤ cost_price):
```python
loss = cost_price - sell_price  # e.g., 500 - 400 = 100
loss_percent = (loss / cost_price) * 100  # (100/500) × 100 = 20%
Question: "A gadget costs $500 and is sold for $400. What is the loss percentage?"
Answer: 20.0
```

**Formula**: `(Loss / Cost Price) × 100`

---

### Key Differences from Easy Mode:

| Aspect | Easy | Medium |
|--------|------|--------|
| **Price Range** | $10-$100 | $100-$1000 |
| **Calculation** | Absolute profit/loss ($) | Percentage profit/loss (%) |
| **Formula** | profit = sell - cost | profit% = (profit/cost) × 100 |
| **Sell Price Range** | ±$20 variance | ±20% to +50% variance |
| **Answer Precision** | Integer (dollars) | Float with 2 decimals (percent) |
| **Complexity** | Basic subtraction | Percentage calculation with formula |

---

## Pedagogical Progression

### Medium Mode Educational Goals:

**PercentageQuestion**:
1. Apply percentages to realistic business amounts (100-1000)
2. Understand **reverse percentage** thinking (part → whole percentage)
3. Handle decimal/fractional percentage results
4. Recognize that 25% of $500 requires different thinking than "$X is 25% of what?"

**ProfitLossQuestion**:
1. Move from absolute values to **relative percentages** (more meaningful in business)
2. Understand why percentage is important: $100 profit is more significant on $500 cost vs $10,000 cost
3. Apply the **percentage formula**: `(change / original) × 100`
4. Develop intuition about profit margins in business contexts

---

## Examples by Difficulty

### Percentage Progression:

**Easy**: "What is 25% of 100?" → Answer: 25
- Single operation, whole numbers, predefined percentages

**Medium Type 1**: "What is 30% of 450?" → Answer: 135.0
- Larger numbers, more diverse percentages, decimal answers

**Medium Type 2**: "What percent of 600 is 180?" → Answer: 30.0
- Reverse thinking, requires division, percentage formula

**Hard**: "If 850 is increased by 15%, what is the new value?" → Answer: 977.5
- Percentage applied to modification (multiplier), more complex formula

---

### Profit Loss Progression:

**Easy**: "Bought for $50, sold for $65. What is the profit?" → Answer: 15
- Simple subtraction, small numbers, absolute dollar amounts

**Medium**: "Bought for $450, sold for $540. What is the profit percentage?" → Answer: 20.0
- Percentage calculation, larger amounts, relative thinking

**Hard (Discount)**: "Item costs $1200. After 25% discount, what's final price?" → Answer: 900.0
- Reverse percentage application, real-world scenario

**Hard (Multiple)**: "Item 1: buy $200, sell $240. Item 2: buy $300, sell $270. Total profit?" → Answer: -30
- Multi-transaction accounting, can result in overall loss despite one profit

---

## Summary

**Medium Mode Philosophy**:
- ✅ Introduces **formula-based thinking** beyond simple arithmetic
- ✅ Uses **realistic business values** (100-1000 range)
- ✅ Teaches **percentage as relative measurement** (not just "X% of Y")
- ✅ Requires understanding of **inverse relationships** (for percentage: part ↔ whole)
- ✅ Builds foundation for **complex business calculations** (hard mode)

