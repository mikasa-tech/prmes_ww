# Excel Upload Formats - Complete Guide

## Overview: Three Ways to Upload Data

Your PRMES system accepts **3 different Excel formats**. It auto-detects which format you're using.

---

## Format 1: Three Evaluator Totals ⭐ (Most Common)

### What is it?
Each evaluator (Member 1, Member 2, Internal Guide) provides their **total marks** only (not individual components).

### Example Excel File:
```
| Name       | Seat_no | Member 1 | Member 2 | Internal Guide |
|------------|---------|----------|----------|----------------|
| John Doe   | 101     | 42       | 39       | 44             |
| Jane Smith | 102     | 38       | 41       | 40             |
```

### What Happens in PRMES:
```
1. System detects: "Member 1", "Member 2", "Internal Guide" columns
2. Reverse engineers each evaluator's total → 4 component marks
3. Calculates average across 3 evaluators
4. Stores in database
```

### Example Processing (John Doe):

**Member 1: 42 total marks**
```
Using Phase 1 Review 1 weights (20, 10, 10, 10):

Criteria1 = 42 × (20/50) = 16.8 → 17
Criteria2 = 42 × (10/50) = 8.4  → 8
Criteria3 = 42 × (10/50) = 8.4  → 9
Criteria4 = 42 × (10/50) = 8.4  → 8
Total = 42 ✓
```

**Member 2: 39 total marks**
```
Criteria1 = 39 × (20/50) = 15.6 → 16
Criteria2 = 39 × (10/50) = 7.8  → 8
Criteria3 = 39 × (10/50) = 7.8  → 8
Criteria4 = 39 × (10/50) = 7.8  → 7
Total = 39 ✓
```

**Internal Guide: 44 total marks**
```
Criteria1 = 44 × (20/50) = 17.6 → 18
Criteria2 = 44 × (10/50) = 8.8  → 9
Criteria3 = 44 × (10/50) = 8.8  → 9
Criteria4 = 44 × (10/50) = 8.8  → 8
Total = 44 ✓
```

**Average Across Evaluators:**
```
Criteria1_avg = (17 + 16 + 18) / 3 = 17
Criteria2_avg = (8 + 8 + 9) / 3 = 8 (rounded from 8.33)
Criteria3_avg = (9 + 8 + 9) / 3 = 8 (rounded from 8.67)
Criteria4_avg = (8 + 7 + 8) / 3 = 8 (rounded from 7.67)

FINAL STORED: [17, 8, 8, 8]
Total = 41
```

### Advantages:
✓ Easiest for teachers (just one number per evaluator)
✓ No need to know component breakdown
✓ System handles distribution automatically
✓ Most commonly used format

### When to Use:
- Teacher only has total marks from each evaluator
- Different evaluators use different evaluation formats
- You want consistency across all evaluators

---

## Format 2: Individual Component Marks

### What is it?
Each component/criterion has its own column with marks from one evaluator.

### Example Excel File:
```
| Name     | Seat_no | Literature | Problem | Presentation | Q&A |
|----------|---------|------------|---------|--------------|-----|
| John Doe | 101     | 17         | 8       | 9            | 8   |
| Jane     | 102     | 16         | 8       | 8            | 7   |
```

### What Happens in PRMES:
```
1. System detects component columns: "Literature", "Problem", etc.
2. NO reverse engineering needed!
3. Uses marks directly
4. Stores in database as-is
```

### Example Processing (John Doe):
```
Criteria1 (Literature) = 17 (used directly)
Criteria2 (Problem) = 8 (used directly)
Criteria3 (Presentation) = 9 (used directly)
Criteria4 (Q&A) = 8 (used directly)
Total = 42

FINAL STORED: [17, 8, 9, 8]
Total = 42 ✓
```

### Advantages:
✓ No rounding needed (exact marks)
✓ No math involved
✓ Direct from evaluator's breakdown

### Disadvantages:
✗ Requires evaluator to provide component breakdown
✗ More columns in Excel
✗ Teacher must know max marks for each component

### When to Use:
- Evaluator already broke down marks into components
- You want exact marks (not rounded)
- Each phase/review has different component names

---

## Format 3: Single Total Mark

### What is it?
Just one "Total" column with combined marks (usually 0-50 or sometimes 0-100).

### Example Excel File:
```
| Name       | Seat_no | Total |
|------------|---------|-------|
| John Doe   | 101     | 42    |
| Jane Smith | 102     | 38    |
```

### What Happens in PRMES:
```
1. System detects: "Total" column
2. Converts 100→50 scale if needed (if total > 50)
3. Reverse engineers into 4 components
4. Stores in database
```

### Example Processing (John Doe):

**Input: 42 (out of 50)**
```
No conversion needed (already out of 50)

Reverse engineer:
Criteria1 = 42 × (20/50) = 16.8 → 17
Criteria2 = 42 × (10/50) = 8.4  → 8
Criteria3 = 42 × (10/50) = 8.4  → 9
Criteria4 = 42 × (10/50) = 8.4  → 8
Total = 42 ✓
```

**Alternative: If input was 84 (out of 100)**
```
Convert to 50 scale first:
Normalized = 84 × (50/100) = 42

Then reverse engineer (same as above)
Criteria1 = 17, Criteria2 = 8, Criteria3 = 9, Criteria4 = 8
Total = 42 ✓
```

### Advantages:
✓ Simplest Excel format (just 3 columns)
✓ Works with both 50 and 100 scale
✓ Auto-converts scales

### Disadvantages:
✗ Requires reverse engineering (rounding)
✗ All students get same component distribution

### When to Use:
- Quick data entry
- Evaluator only has total (not components)
- Don't need component-level detail

---

## Comparison Table

| Aspect | Format 1 | Format 2 | Format 3 |
|--------|----------|----------|----------|
| **Columns** | Name, Seat_no, Member1, Member2, Guide | Name, Seat_no, Crit1, Crit2, Crit3, Crit4 | Name, Seat_no, Total |
| **Evaluators** | 3 | 1 | 1 |
| **Reverse Engineering** | ✓ Yes | ✗ No | ✓ Yes |
| **Complexity** | Medium | High | Low |
| **Use Case** | Most common | Exact marks | Quick entry |
| **Rounding** | Yes (fair) | None | Yes (fair) |
| **Effort** | Low | High | Very Low |

---

## How Column Detection Works

### System looks for these column names (case-insensitive):

**Required for all formats:**
- `Name`, `Student Name`, `Student_Name`
- `Seat_no`, `Seatno`, `USN`, `Roll Number`

**Format 1 (Three Evaluators):**
- `Member 1`, `Member1`, `Chairperson`, `M1`
- `Member 2`, `Member2`, `M2`
- `Internal Guide`, `Guide`, `Project Guide`

**Format 2 (Components) - varies by phase/review:**
- Phase 1 Review 1: `Literature Survey`, `Problem Identification`, `Presentation`, `Q&A`
- Phase 1 Review 2: `Objectives`, `Methodology`, `Presentation`, `Q&A`
- Phase 2 Review 1: `Preliminary Studies`, `Execution & Result Analysis`, `Presentation`, `Q&A`
- Phase 2 Review 2: `Conclusion & Future Scope`, `Publication`, `Presentation`, `Q&A`

**Format 3 (Total):**
- `Total`, `Total Marks`, `Average`, `Avg`, `Score`

**Optional columns:**
- `Project Group`, `Group No`, `Group Number`
- `Project Title`, `Title`
- `Project Guide`

---

## Detection Priority

PRMES checks in this order:

1. **Does it have all 3 evaluator columns?** → Format 1
2. **Does it have all 4 component columns?** → Format 2
3. **Does it have a Total column?** → Format 3
4. **None of above?** → Error ❌

```python
# From upload_helpers.py
if all columns exist for Format 1:
    use_format_1()
elif all columns exist for Format 2:
    use_format_2()
elif total column exists:
    use_format_3()
else:
    raise Error("Missing required columns")
```

---

## Example: Same Student, All 3 Formats

### Format 1: Three Evaluators
```
| John | 101 | 42 | 39 | 44 |
```
After processing: [17, 8, 8, 8] (average across 3)

### Format 2: Components
```
| John | 101 | 17 | 8 | 9 | 8 |
```
After processing: [17, 8, 9, 8] (direct)

### Format 3: Total
```
| John | 101 | 42 |
```
After processing: [17, 8, 9, 8] (reverse engineered)

### Result:
All three give similar but slightly different results due to rounding differences!

---

## Tips for Best Results

✓ Use **Format 1** if you have 3 evaluators
✓ Use **Format 2** if you want exact marks
✓ Use **Format 3** for quick entry with one evaluator
✓ Always include optional columns (Group, Title, Guide) if available
✓ Keep column names close to standard names (the system is flexible!)
✓ Save Excel file as `.xlsx` (not `.xls` or `.csv`)

---

## Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Missing Name or Seat_no" | Column names not found | Check spelling: must include "Name" and "Seat_no" |
| "Must have Total or evaluator marks" | Wrong format | Ensure one of 3 formats is present |
| "Invalid Excel file" | Corrupted file | Save as `.xlsx` and try again |
| "Phase/Review must be 1 or 2" | Invalid selection | Select Phase 1 or 2, Review 1 or 2 |
| "File must be .xlsx" | Wrong file type | Save in Excel format, not CSV or XLS |
