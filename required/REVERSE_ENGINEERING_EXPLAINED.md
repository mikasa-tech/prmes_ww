# Reverse Engineering Explained - PRMES

## What is Reverse Engineering?

**Reverse Engineering** = Breaking down a **total mark** into **individual component marks** while maintaining the total.

### Why is it needed?

When a teacher gives you **only the total mark** (e.g., 42/50), but your system needs marks for each **criterion** (Literature Survey, Problem ID, Presentation, Q&A), you need to distribute that total across 4 criteria proportionally.

---

## The Problem

### Teacher's Excel File:
```
| Name       | Seat_no | Total |
|------------|---------|-------|
| John Doe   | 101     | 42    |
| Jane Smith | 102     | 38    |
```

### System Needs:
```
| Name       | Criteria1 | Criteria2 | Criteria3 | Criteria4 | Total |
|------------|-----------|-----------|-----------|-----------|-------|
| John Doe   |     ?     |     ?     |     ?     |     ?     |  42   |
| Jane Smith |     ?     |     ?     |     ?     |     ?     |  38   |
```

---

## How Reverse Engineering Works

### Step 1: Define Weights (Max Marks Per Criteria)

**Phase 1 Review 1** criteria:
- Criteria1 (Literature Survey): **20 marks** max
- Criteria2 (Problem ID): **10 marks** max  
- Criteria3 (Presentation): **10 marks** max
- Criteria4 (Q&A): **10 marks** max
- **Total: 50 marks**

### Step 2: Calculate Proportional Distribution

Given total = 42, distribute proportionally based on weights:

```
Formula: (Criteria_Mark / Total_50) = (Weight / 50)

Criteria1 = 42 × (20/50) = 42 × 0.4 = 16.8
Criteria2 = 42 × (10/50) = 42 × 0.2 = 8.4
Criteria3 = 42 × (10/50) = 42 × 0.2 = 8.4
Criteria4 = 42 × (10/50) = 42 × 0.2 = 8.4
```

Sum = 16.8 + 8.4 + 8.4 + 8.4 = 42 ✓

### Step 3: Round to Integers (Hamilton Rounding)

Problem: We get decimals, but marks must be integers!

```
Before rounding:
Criteria1 = 16.8
Criteria2 = 8.4
Criteria3 = 8.4
Criteria4 = 8.4
```

Simple rounding would give: 17 + 8 + 8 + 8 = 41 ❌ (Lost 1 mark!)

**Solution: Hamilton's Largest Remainder Method**

1. **Floor each value** (round down):
   ```
   Criteria1 = 16 (floor of 16.8, remainder = 0.8)
   Criteria2 = 8  (floor of 8.4, remainder = 0.4)
   Criteria3 = 8  (floor of 8.4, remainder = 0.4)
   Criteria4 = 8  (floor of 8.4, remainder = 0.4)
   Sum = 40
   ```

2. **Calculate remainder** from target:
   ```
   Remainder needed = 42 - 40 = 2
   ```

3. **Sort by fractional part** (largest remainder first):
   ```
   Criteria1: 0.8 (highest)
   Criteria2: 0.4 
   Criteria3: 0.4
   Criteria4: 0.4
   ```

4. **Distribute remainder** to top criteria:
   ```
   Give +1 to Criteria1 (has 0.8)
   Give +1 to Criteria2 (has 0.4, first in line)
   
   Final:
   Criteria1 = 17 (16 + 1)
   Criteria2 = 9  (8 + 1)
   Criteria3 = 8
   Criteria4 = 8
   Sum = 17 + 9 + 8 + 8 = 42 ✓
   ```

---

## Code Implementation

### The Algorithm (in `utils.py`):

```python
def reverse_engineer_components(total: int, phase: int = 1, review: int = 1):
    """
    Input: total mark (e.g., 42)
    Output: Dictionary with marks for each criteria
    """
    # Get weights for this phase/review
    weights = {
        "criteria1": 20,  # Literature Survey
        "criteria2": 10,  # Problem ID
        "criteria3": 10,  # Presentation
        "criteria4": 10,  # Q&A
    }
    
    # Clamp total between 0 and 50
    t = max(0, min(int(total), 50))
    
    # Step 1: Proportional scaling
    scaled = {
        k: (t * (w / 50))  # t=42, w=20 → 42 * (20/50) = 16.8
        for k, w in weights.items()
    }
    
    # Step 2: Hamilton rounding
    return _hamilton_round(scaled, t)


def _hamilton_round(values: Dict[str, float], target_sum: int):
    """
    Hamilton's Largest Remainder Method
    """
    # Step 1: Floor each value
    floors = {k: int(v) for k, v in values.items()}  # 16.8 → 16
    
    # Step 2: Calculate how many marks we still need to distribute
    remainder = target_sum - sum(floors.values())  # 42 - 40 = 2
    
    if remainder == 0:
        return floors  # Already perfect
    
    # Step 3: Sort by fractional part (largest first)
    fracs = sorted(
        ((k, values[k] - floors[k]) for k in values),
        key=lambda x: x[1],
        reverse=True
    )
    # fracs = [('criteria1', 0.8), ('criteria2', 0.4), ...]
    
    # Step 4: Distribute remainder marks
    result = floors.copy()
    for i in range(remainder):
        key = fracs[i % len(fracs)][0]
        result[key] += 1
    
    return result
```

---

## Real-World Example

### Teacher provides:
```
| Name       | Seat_no | Member1 | Member2 | Guide |
|------------|---------|---------|---------|-------|
| Raj Kumar  | 101     |   42    |   39    |  44   |
```

### For each evaluator, reverse engineer:

**Member 1 (42 marks):**
```
Criteria1 = 42 × (20/50) = 16.8 → 17
Criteria2 = 42 × (10/50) = 8.4  → 8
Criteria3 = 42 × (10/50) = 8.4  → 9  (gets remainder)
Criteria4 = 42 × (10/50) = 8.4  → 8
Total = 42 ✓
```

**Member 2 (39 marks):**
```
Criteria1 = 39 × (20/50) = 15.6 → 16
Criteria2 = 39 × (10/50) = 7.8  → 8  (gets remainder)
Criteria3 = 39 × (10/50) = 7.8  → 8  (gets remainder)
Criteria4 = 39 × (10/50) = 7.8  → 7
Total = 39 ✓
```

**Guide (44 marks):**
```
Criteria1 = 44 × (20/50) = 17.6 → 18  (gets remainder)
Criteria2 = 44 × (10/50) = 8.8  → 9  (gets remainder)
Criteria3 = 44 × (10/50) = 8.8  → 9  (gets remainder)
Criteria4 = 44 × (10/50) = 8.8  → 8
Total = 44 ✓
```

### Final Average:
```
Criteria1_avg = (17 + 16 + 18) / 3 = 17
Criteria2_avg = (8 + 8 + 9) / 3 = 8
Criteria3_avg = (9 + 8 + 9) / 3 = 9
Criteria4_avg = (8 + 7 + 8) / 3 = 8
Total = 17 + 8 + 9 + 8 = 42
```

---

## Different Formats Handled

### Format 1: Three Evaluator Totals (uses reverse engineering)
```
| Name | Seat_no | Member1 | Member2 | Guide |
|------|---------|---------|---------|-------|
| John |   101   |   42    |   39    |  44   |
```
✓ Reverse engineer each evaluator's marks

### Format 2: Individual Component Marks (no reverse engineering)
```
| Name | Literature | Problem | Presentation | Q&A |
|------|------------|---------|--------------|-----|
| John |     17     |    8    |       9      |  8  |
```
✓ Use marks directly, no calculation needed

### Format 3: Single Total (uses reverse engineering)
```
| Name | Seat_no | Total |
|------|---------|-------|
| John |   101   |  42   |
```
✓ Reverse engineer into 4 components

---

## Why Hamilton Rounding?

### Other methods lose marks:

**Simple Rounding:**
```
16.8 → 17, 8.4 → 8, 8.4 → 8, 8.4 → 8 = 41 ❌ (Lost 1 mark)
```

**Always Round Up:**
```
16.8 → 17, 8.4 → 9, 8.4 → 9, 8.4 → 9 = 44 ❌ (Gained 2 marks)
```

**Hamilton Method:**
```
Maintains the sum = 42 ✓
Fair distribution based on fractional parts
```

---

## In Your Application

When you upload Excel with "Member1: 42, Member2: 39, Guide: 44":

1. `upload_helpers.py` detects the format
2. Calls `reverse_engineer_components()` for each evaluator
3. Stores individual criteria marks in database
4. Calculates averages across evaluators
5. Displays in PDF report

```python
# In upload_helpers.py line 50-53
member1_comp = reverse_engineer_components(42, phase=1, review=1)
member2_comp = reverse_engineer_components(39, phase=1, review=1)
guide_comp = reverse_engineer_components(44, phase=1, review=1)
```

---

## Key Takeaways

| Concept | Explanation |
|---------|-------------|
| **What** | Convert total mark into individual component marks |
| **Why** | Teachers give totals, but system needs per-criterion breakdown |
| **How** | Proportional distribution based on max marks, then Hamilton rounding |
| **Result** | Marks sum to original total while being fairly distributed |
| **Benefit** | Automatic mark distribution - users upload one number, system calculates 4 |
