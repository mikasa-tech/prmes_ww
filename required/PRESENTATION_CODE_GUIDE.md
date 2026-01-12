# PRMES - Complete Code Explanation for Presentation

---

# SECTION 1: PROJECT OVERVIEW

## What is PRMES?

**PRMES** = **P**roject **R**eview **M**anagement and **E**valuation **S**ystem

### Problem It Solves:
```
Traditional Evaluation Process:
┌─────────────────────────────────────────┐
│ 1. Teachers fill marks in Excel         │ (Manual & tedious)
│ 2. Marks scattered across different files
│ 3. Manual calculation of averages       │ (Error-prone)
│ 4. Manual PDF report generation         │ (Time-consuming)
│ 5. Difficult to view data in different ways
└─────────────────────────────────────────┘

PRMES Solution:
┌─────────────────────────────────────────┐
│ 1. Upload Excel → Automatic processing  │
│ 2. Centralized database storage         │
│ 3. Automatic mark calculation           │
│ 4. One-click PDF generation             │
│ 5. Multiple views (all, group, guide)   │
└─────────────────────────────────────────┘
```

---

## Key Features

| Feature | Benefit |
|---------|---------|
| **4 Review Phases** | Track students across Phase 1 & 2, each with 2 reviews |
| **3 Evaluators** | Member 1, Member 2, Internal Guide per student |
| **Smart Mark Distribution** | Auto-split totals into components fairly |
| **Multiple Views** | All students, Group-wise, Guide-wise, Individual |
| **PDF Reports** | Professional individual & comprehensive reports |
| **Flexible Formats** | Accepts 3 different Excel formats |
| **Database Support** | SQLite (default) or MySQL |

---

## Tech Stack

```
Frontend:
  - HTML/CSS/Bootstrap
  - Jinja2 Templates

Backend:
  - Flask (Python web framework)
  - SQLAlchemy ORM (database abstraction)

Database:
  - SQLite (development) or MySQL (production)

File Processing:
  - openpyxl (read Excel files)

PDF Generation:
  - ReportLab (create professional PDFs)

Deployment:
  - Python 3.8+
  - pip (package manager)
```

---

# SECTION 2: DATABASE ARCHITECTURE

## Database Design

### Table 1: Student

```python
class Student(db.Model):
    id              INTEGER (primary key)
    name            VARCHAR(128)  - Student full name
    seat_no         VARCHAR(64)   - Roll number / USN (unique)
    group_no        VARCHAR(50)   - Project group number
    project_title   VARCHAR(255)  - Project name
    project_guide   VARCHAR(128)  - Guide name
    evaluations     RELATIONSHIP  - Links to Evaluation records
```

**Why these fields?**
- `name` + `seat_no` = Unique identifier for each student
- `group_no` = Group students for "group-wise view"
- `project_guide` = Group students for "guide-wise view"
- `evaluations` = One student can have multiple evaluations (Phase 1 Review 1, Phase 1 Review 2, etc.)

### Table 2: Evaluation

```python
class Evaluation(db.Model):
    id                      INTEGER (primary key)
    student_id              INTEGER (foreign key to Student)
    phase                   INTEGER (1 or 2)
    review_no               INTEGER (1 or 2)
    total_marks             INTEGER (sum of all criteria)
    
    # Average marks across 3 evaluators
    criteria1               INTEGER (e.g., Literature Survey avg)
    criteria2               INTEGER (e.g., Problem ID avg)
    criteria3               INTEGER (e.g., Presentation avg)
    criteria4               INTEGER (e.g., Q&A avg)
    
    # Individual marks from Member 1
    member1_criteria1       INTEGER
    member1_criteria2       INTEGER
    member1_criteria3       INTEGER
    member1_criteria4       INTEGER
    
    # Individual marks from Member 2
    member2_criteria1       INTEGER
    member2_criteria2       INTEGER
    member2_criteria3       INTEGER
    member2_criteria4       INTEGER
    
    # Individual marks from Guide
    guide_criteria1         INTEGER
    guide_criteria2         INTEGER
    guide_criteria3         INTEGER
    guide_criteria4         INTEGER
    
    # Constraint: Only one evaluation per student per phase per review
    UNIQUE(student_id, phase, review_no)
```

**Why store individual evaluator marks?**
- Track each evaluator separately
- Show consistency/discrepancy
- Display in PDF with individual columns

**Why generic criteria1-4 instead of hardcoded names?**
- Criteria change per phase/review:
  - Phase 1 Review 1: Literature, Problem, Presentation, Q&A
  - Phase 2 Review 2: Conclusion, Publication, Presentation, Q&A
- Generic fields + `review_config.py` = Dynamic system
- Easy to change criteria without DB migration

---

## Database Schema Diagram

```
┌──────────────┐                    ┌─────────────────┐
│   Student    │                    │   Evaluation    │
├──────────────┤      1───────∞     ├─────────────────┤
│ id (PK)      │──────────────→      │ id (PK)         │
│ name         │                    │ student_id (FK) │
│ seat_no      │                    │ phase           │
│ group_no     │                    │ review_no       │
│ project_title│                    │ total_marks     │
│ project_guide│                    │ criteria1-4     │
└──────────────┘                    │ member1_*       │
                                    │ member2_*       │
                                    │ guide_*         │
                                    └─────────────────┘

One Student can have multiple Evaluations:
- Phase 1, Review 1
- Phase 1, Review 2
- Phase 2, Review 1
- Phase 2, Review 2
```

---

# SECTION 3: FILE STRUCTURE & ARCHITECTURE

## Core Application Files

### 1. `app.py` - Main Application (Flask)

**Purpose:** Entry point - handles all routes and main logic

```python
# Basic structure:
from flask import Flask
from models import db

app = Flask(__name__)

# Routes:
@app.route("/")                    # Home page
@app.route("/upload", methods=...)  # File upload
@app.route("/students")            # View students
@app.route("/students/groupwise")  # View by group
@app.route("/students/guidewise")  # View by guide
@app.route("/download-pdf")        # Generate PDF
@app.route("/download-comprehensive-pdf")  # Summary PDF
```

**Main Functions:**

1. **`create_app()`** - Initializes Flask app
   - Loads environment variables
   - Configures database (SQLite or MySQL)
   - Creates tables

2. **`upload_csv()` route** - Handles file upload
   - Gets phase and review from form
   - Reads Excel file
   - Validates columns
   - Calls processing functions
   - Saves to database

3. **`view_students()` route** - Displays students
   - Retrieves students from database
   - Filters by phase/review
   - Groups by view type
   - Renders HTML template

4. **`download_pdf()` route** - Generates PDF
   - Queries database for student
   - Calls `build_review1_pdf()`
   - Sends PDF to browser

---

### 2. `models.py` - Database Models

**Purpose:** Define database table structure

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    # Fields defined here
    # Relationships defined here

class Evaluation(db.Model):
    # Fields defined here
    # Relationships defined here
```

**What it does:**
- Defines what data can be stored
- Sets up relationships between tables
- SQLAlchemy converts to actual SQL

---

### 3. `review_config.py` - Configuration

**Purpose:** Define evaluation criteria for each phase/review

```python
REVIEW_CRITERIA = {
    (1, 1): {  # Phase 1, Review 1
        'criteria': [
            {'name': 'Literature Survey', 'db_field': 'criteria1', 'max_marks': 20, 'guide_marks': True},
            {'name': 'Problem Identification', 'db_field': 'criteria2', 'max_marks': 10, 'guide_marks': True},
            {'name': 'Project presentation skill', 'db_field': 'criteria3', 'max_marks': 10, 'guide_marks': False},
            {'name': 'Question and answer session', 'db_field': 'criteria4', 'max_marks': 10, 'guide_marks': False},
        ],
        'total': 50,
        'title': 'PHASE - I REVIEW - I'
    },
    (1, 2): {...},  # Phase 1, Review 2
    (2, 1): {...},  # Phase 2, Review 1
    (2, 2): {...},  # Phase 2, Review 2
}

def get_review_config(phase, review):
    """Get config for specific phase/review"""
    return REVIEW_CRITERIA.get((phase, review))
```

**Why this matters:**
- Centralized configuration
- Easy to change criteria
- Different criteria per phase/review
- Supports dynamic mark distribution

---

### 4. `upload_helpers.py` - Upload Processing

**Purpose:** Detect Excel format and process data

```python
def map_excel_columns_to_criteria(row, key_map, phase, review):
    """
    Main function that routes to correct handler
    
    Detects which format and processes accordingly
    """
    if has_three_evaluators():
        return handle_three_evaluators(...)
    elif has_components():
        return handle_component_columns(...)
    elif has_total():
        return handle_total_marks(...)
```

**Three Handlers:**

1. **`handle_three_evaluators()`**
   - Format: Member 1 total, Member 2 total, Guide total
   - Action: Reverse engineer each into 4 components
   - Calculate average

2. **`handle_component_columns()`**
   - Format: Individual columns for each criterion
   - Action: Use marks directly
   - No reverse engineering needed

3. **`handle_total_marks()`**
   - Format: Single total column
   - Action: Reverse engineer into 4 components
   - Normalize if out of range

---

### 5. `utils.py` - Utility Functions

**Purpose:** Helper functions for data processing

```python
def normalize_header(h):
    """Convert any header variation to standard format
    
    "Student Name" → "student_name"
    "Member 1" → "member_1"
    "Seat-No" → "seat_no"
    """
    # Makes system flexible with column names
```

```python
def reverse_engineer_components(total, phase, review):
    """Split total mark into 4 components fairly
    
    Input: 42 (total mark)
    Output: {criteria1: 17, criteria2: 8, criteria3: 9, criteria4: 8}
    """
    weights = get_weights_dict(phase, review)  # Get weights from review_config
    scaled = {k: (total * (w / 50)) for k, w in weights.items()}  # Proportional
    return _hamilton_round(scaled, total)  # Round fairly
```

```python
def _hamilton_round(values, target_sum):
    """Hamilton's Largest Remainder Method
    
    Rounds while preserving exact sum
    - Floor all values
    - Distribute remainder to those with largest fractional parts
    - Result: sum always equals target_sum
    """
```

**Why these functions matter:**
- `normalize_header()` = Flexible with different column names
- `reverse_engineer_components()` = Core algorithm for mark distribution
- `_hamilton_round()` = Fair, mathematically correct rounding

---

### 6. `pdf_template.py` - Individual PDF Report

**Purpose:** Generate professional PDF for single student

```python
def build_review1_pdf(student, evaluation, phase, review):
    """Create PDF with:
    - College header with logo
    - Student information
    - Project details
    - Marks table (Member 1, Member 2, Guide, Average)
    - Formatted professionally
    """
```

**What it includes:**
- College name & logo
- Student name, seat number, group
- Project title and guide
- Evaluation criteria with marks
- Individual evaluator marks
- Average marks
- Date generated

---

### 7. `comprehensive_pdf_template.py` - Summary PDF

**Purpose:** Generate PDF with all phases/reviews combined

```python
def build_comprehensive_pdf(all_data):
    """Create PDF with:
    - All phases and reviews
    - All students
    - Summary tables
    - One report for entire semester
    """
```

**Structure:**
- Page 1: Header + Title
- Pages 2-N: One page per phase/review
- Each page has table of all students
- Multiple page breaks between sections

---

## Additional Files

| File | Purpose |
|------|---------|
| `excel_template.py` | Generate sample Excel templates for download |
| `read_excel.py` | Debug tool - read and display Excel structure |
| `check_excel.py` | Validate Excel format |
| `populate_sample_data.py` | Create test data for demo |
| `test_reverse_engineer.py` | Unit tests for algorithm |
| `test_views.py` | Test view functionality |
| `migrate_db.py` | Database schema updates |
| `fix_*.py` | Various data correction scripts |

---

# SECTION 4: DATA FLOW DIAGRAM

## Complete User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER JOURNEY - PRMES                         │
└─────────────────────────────────────────────────────────────────┘

STEP 1: LAUNCH APPLICATION
┌──────────────────────────────┐
│ User opens browser            │
│ http://127.0.0.1:5000         │
└────────────┬──────────────────┘
             │
             ↓
┌──────────────────────────────┐
│ Flask app.py loads            │
│ create_app() initializes      │
│ Database connected            │
└────────────┬──────────────────┘
             │
             ↓
┌──────────────────────────────┐
│ User sees home page           │
│ Options: Upload, View         │
└────────────┬──────────────────┘

STEP 2: UPLOAD EXCEL FILE
             │
             ↓
┌──────────────────────────────┐
│ User clicks "Upload"          │
│ Selects Phase 1, Review 1     │
│ Chooses Excel file            │
└────────────┬──────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ app.py receives file                     │
│ @app.route("/upload", methods=POST)      │
│                                          │
│ phase = 1, review_no = 1                 │
│ file = uploaded Excel                    │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ Parse Excel Headers                      │
│ utils.normalize_header()                 │
│                                          │
│ "Name" → "name"                          │
│ "Seat_no" → "seat_no"                    │
│ "Member 1" → "member1"                   │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ Map Columns to Keys                      │
│                                          │
│ key_map = {                              │
│   "name": "Name",                        │
│   "seat_no": "Seat_no",                  │
│   "member1": "Member 1",                 │
│   "member2": "Member 2",                 │
│   "internal_guide": "Internal Guide"     │
│ }                                        │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ Detect Format                            │
│ upload_helpers.py                        │
│                                          │
│ Has Member1, Member2, Guide? → Format 1 │
│ Has all 4 components? → Format 2         │
│ Has Total? → Format 3                    │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ STEP 3: PROCESS DATA                     │
│                                          │
│ For each row in Excel:                   │
│   name = "John Doe"                      │
│   seat_no = "101"                        │
│   member1 = 42                           │
│   member2 = 39                           │
│   internal_guide = 44                    │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ Reverse Engineer Each Evaluator          │
│ utils.reverse_engineer_components()      │
│                                          │
│ member1_comp = reverse_engineer(42)      │
│   → {c1: 17, c2: 8, c3: 9, c4: 8}      │
│                                          │
│ member2_comp = reverse_engineer(39)      │
│   → {c1: 16, c2: 8, c3: 8, c4: 7}      │
│                                          │
│ guide_comp = reverse_engineer(44)        │
│   → {c1: 18, c2: 9, c3: 9, c4: 8}      │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ Calculate Average                        │
│                                          │
│ avg_c1 = (17 + 16 + 18) / 3 = 17        │
│ avg_c2 = (8 + 8 + 9) / 3 = 8            │
│ avg_c3 = (9 + 8 + 9) / 3 = 8            │
│ avg_c4 = (8 + 7 + 8) / 3 = 7            │
│ total = 17 + 8 + 8 + 7 = 40             │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ STEP 4: STORE IN DATABASE                │
│                                          │
│ Create Student (if not exists)           │
│   name = "John Doe"                      │
│   seat_no = "101"                        │
│   group_no = "Group 1"                   │
│   project_title = "..."                  │
│   project_guide = "Dr. Smith"            │
│                                          │
│ Create Evaluation                        │
│   student_id = 1                         │
│   phase = 1, review_no = 1               │
│   total_marks = 40                       │
│   criteria1 = 17, criteria2 = 8, ...     │
│   member1_criteria1 = 17, ...            │
│   member2_criteria1 = 16, ...            │
│   guide_criteria1 = 18, ...              │
│                                          │
│ db.session.commit()                      │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ STEP 5: USER VIEWS DATA                  │
│                                          │
│ User clicks "View Students"              │
│ Selects phase, review, view type         │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ app.py /students route                   │
│                                          │
│ Query database:                          │
│   SELECT * FROM Student                  │
│   JOIN Evaluation WHERE                  │
│     phase = 1 AND review_no = 1          │
│                                          │
│ Group if needed:                         │
│   Group by group_no (groupwise view)     │
│   Group by project_guide (guidewise)     │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ Render HTML Template                     │
│ templates/students.html                  │
│                                          │
│ Display table:                           │
│ | Name | Seat# | Group | C1 | C2 | ... | │
│ | John | 101   | Gr1   | 17 | 8  | ... | │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ STEP 6: GENERATE PDF (Optional)          │
│                                          │
│ User clicks "Download PDF"               │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ app.py /download-pdf route               │
│                                          │
│ Query database for student               │
│ Call pdf_template.build_review1_pdf()    │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ PDF Generation                           │
│ pdf_template.py                          │
│                                          │
│ 1. Create empty PDF in memory            │
│ 2. Add college header & logo             │
│ 3. Add student information               │
│ 4. Create marks table:                   │
│    Criteria | M1 | M2 | Guide | Avg     │
│    C1: Lit  | 17 | 16 | 18    | 17      │
│    C2: Prob | 8  | 8  | 9     | 8       │
│    ... (all 4 criteria)                  │
│ 5. Format professionally                 │
│ 6. Build PDF                             │
└────────────┬──────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────┐
│ Browser receives PDF                     │
│ User downloads as file                   │
│ Saves on computer                        │
└──────────────────────────────────────────┘
```

---

# SECTION 5: KEY ALGORITHMS

## Algorithm 1: Header Normalization

**Problem:** Different teachers name columns differently
**Solution:** Normalize all variations to standard format

```python
def normalize_header(h: str) -> str:
    """
    Input:  "Student Name", "Name", "STUDENT_NAME", "student name"
    Output: "student_name"
    
    Process:
    1. Lowercase everything
    2. Replace spaces/special chars with underscore
    3. Remove leading/trailing underscores
    """
    s = h.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)  # [^a-z0-9]+ means: anything that's not letter/number
    s = re.sub(r"_+", "_", s).strip("_")  # Remove extra underscores
    return s

# Examples:
normalize_header("Name")          # → "name"
normalize_header("Student Name")  # → "student_name"
normalize_header("Member 1")      # → "member_1"
normalize_header("Seat-No")       # → "seat_no"
```

---

## Algorithm 2: Reverse Engineering (Core Algorithm)

**Problem:** Teacher gives total (42), but system needs 4 component marks

**Solution:** Distribute proportionally, then round fairly

```python
def reverse_engineer_components(total: int, phase: int, review: int) -> Dict:
    """
    Input:  total=42, phase=1, review=1
    Output: {criteria1: 17, criteria2: 8, criteria3: 9, criteria4: 8}
    
    Phase 1 Review 1 weights: {criteria1: 20, criteria2: 10, criteria3: 10, criteria4: 10}
    """
    
    # Get weights for this phase/review
    weights = {criteria1: 20, criteria2: 10, criteria3: 10, criteria4: 10}  # Max marks
    
    # Clamp total between 0-50
    t = max(0, min(int(total), 50))  # Ensure 0 ≤ t ≤ 50
    
    # Step 1: Proportional Distribution
    # Each criterion gets: (total * (its_weight / total_weight))
    scaled = {
        criteria1: 42 * (20/50) = 16.8,    # 40% of total
        criteria2: 42 * (10/50) = 8.4,     # 20% of total
        criteria3: 42 * (10/50) = 8.4,     # 20% of total
        criteria4: 42 * (10/50) = 8.4      # 20% of total
    }
    
    # Step 2: Hamilton Rounding
    return _hamilton_round(scaled, t)
```

---

## Algorithm 3: Hamilton's Largest Remainder Method

**Problem:** Rounding 16.8, 8.4, 8.4, 8.4 loses the total

**Solution:** Floor, calculate remainder, distribute fairly

```python
def _hamilton_round(values: Dict, target_sum: int) -> Dict:
    """
    Input:  {c1: 16.8, c2: 8.4, c3: 8.4, c4: 8.4}, target_sum=42
    Output: {c1: 17, c2: 9, c3: 8, c4: 8}  ← Sum = 42 ✓
    """
    
    # Step 1: Floor each value (round down)
    floors = {c1: 16, c2: 8, c3: 8, c4: 8}
    current_sum = 16 + 8 + 8 + 8 = 40
    
    # Step 2: Calculate remainder
    remainder = target_sum - current_sum = 42 - 40 = 2
    # We need to add 2 more marks somewhere
    
    # Step 3: Sort by fractional part (those with highest decimal)
    fracs = [
        (c1, 0.8),  ← Highest (16.8 - 16)
        (c2, 0.4),
        (c3, 0.4),
        (c4, 0.4)
    ]
    
    # Step 4: Distribute remainder to those with highest fractional parts
    result = floors.copy()
    for i in range(remainder):  # i = 0, 1
        key = fracs[i][0]
        result[key] += 1
    
    # i=0: Add 1 to c1 (has 0.8) → c1 becomes 17
    # i=1: Add 1 to c2 (has 0.4) → c2 becomes 9
    
    return result
    # {c1: 17, c2: 9, c3: 8, c4: 8}  ← Sum = 42 ✓
```

**Why this method?**
- ✓ Sum always equals target
- ✓ Fair: gives extra marks to those with highest fractional parts
- ✓ Mathematical: used in parliament seat allocation worldwide
- ✓ No bias: not always rounding up or down

---

## Algorithm 4: Excel Format Detection

**Problem:** Three different Excel formats possible

**Solution:** Check for columns, route to correct handler

```python
def map_excel_columns_to_criteria(row, key_map, phase, review):
    """
    Auto-detect which format user uploaded
    """
    
    # Format 1: Three Evaluator Totals
    if all(k in key_map for k in ("member1", "member2", "internal_guide")):
        # Excel has: Member 1 (42), Member 2 (39), Guide (44)
        return handle_three_evaluators(row, key_map, phase, review)
    
    # Format 2: Component Marks
    elif all(k in key_map for k in ("criteria1", "criteria2", "criteria3", "criteria4")):
        # Excel has: Literature (17), Problem (8), Presentation (9), Q&A (8)
        return handle_component_columns(row, key_map, phase, review)
    
    # Format 3: Single Total
    elif "total" in key_map:
        # Excel has: Total (42)
        return handle_total_marks(row, key_map, phase, review)
    
    else:
        # No recognized format
        raise ValueError("Excel must have evaluator totals, component marks, or total column")
```

---

# SECTION 6: DATA PROCESSING EXAMPLE

## Real-World Example: Processing One Student

### Excel Input:
```
| Name     | Seat_no | Member 1 | Member 2 | Internal Guide |
|----------|---------|----------|----------|----------------|
| John Doe | 101     | 42       | 39       | 44             |
```

### Processing Steps:

**Step 1: Parse Headers**
```
normalize_header("Name") → "name"
normalize_header("Seat_no") → "seat_no"
normalize_header("Member 1") → "member_1"
normalize_header("Member 2") → "member_2"
normalize_header("Internal Guide") → "internal_guide"

key_map = {
    "name": "Name",
    "seat_no": "Seat_no",
    "member1": "Member 1",
    "member2": "Member 2",
    "internal_guide": "Internal Guide"
}
```

**Step 2: Detect Format**
```
Check: Does key_map have member1? YES
Check: Does key_map have member2? YES
Check: Does key_map have internal_guide? YES

→ Format 1 (Three Evaluators)
Call: handle_three_evaluators()
```

**Step 3: Extract Values**
```
row = {
    "Name": "John Doe",
    "Seat_no": "101",
    "Member 1": 42,
    "Member 2": 39,
    "Internal Guide": 44
}

member1_total = 42
member2_total = 39
guide_total = 44
```

**Step 4: Reverse Engineer Each Evaluator**

**For Member 1 (42):**
```
Phase 1 Review 1 weights: {c1: 20, c2: 10, c3: 10, c4: 10}

Step 1: Proportional distribution
  c1 = 42 × (20/50) = 16.8
  c2 = 42 × (10/50) = 8.4
  c3 = 42 × (10/50) = 8.4
  c4 = 42 × (10/50) = 8.4

Step 2: Hamilton rounding
  floors: {c1: 16, c2: 8, c3: 8, c4: 8} (sum = 40)
  remainder = 42 - 40 = 2
  fracs sorted: [(c1, 0.8), (c2, 0.4), (c3, 0.4), (c4, 0.4)]
  
  Distribute 2 marks:
    i=0: c1 += 1 → 17
    i=1: c2 += 1 → 9
  
  Result: {c1: 17, c2: 9, c3: 8, c4: 8} ✓ sum = 42
```

**For Member 2 (39):**
```
  c1 = 39 × (20/50) = 15.6
  c2 = 39 × (10/50) = 7.8
  c3 = 39 × (10/50) = 7.8
  c4 = 39 × (10/50) = 7.8

Floored: {c1: 15, c2: 7, c3: 7, c4: 7} (sum = 36)
Remainder = 39 - 36 = 3

Distribute:
  i=0: c1 += 1 → 16 (0.6 largest)
  i=1: c2 += 1 → 8 (0.8 largest)
  i=2: c3 += 1 → 8 (0.8 second largest)

Result: {c1: 16, c2: 8, c3: 8, c4: 7} ✓ sum = 39
```

**For Guide (44):**
```
  c1 = 44 × (20/50) = 17.6
  c2 = 44 × (10/50) = 8.8
  c3 = 44 × (10/50) = 8.8
  c4 = 44 × (10/50) = 8.8

Floored: {c1: 17, c2: 8, c3: 8, c4: 8} (sum = 41)
Remainder = 44 - 41 = 3

Distribute:
  i=0: c1 += 1 → 18 (0.6 largest)
  i=1: c2 += 1 → 9 (0.8 largest)
  i=2: c3 += 1 → 9 (0.8 second)

Result: {c1: 18, c2: 9, c3: 9, c4: 8} ✓ sum = 44
```

**Step 5: Calculate Averages**
```
For criteria1:
  m1 = 17, m2 = 16, guide = 18
  avg = (17 + 16 + 18) / 3 = 51 / 3 = 17

For criteria2:
  m1 = 9, m2 = 8, guide = 9
  avg = (9 + 8 + 9) / 3 = 26 / 3 = 8.67 → 9 (rounded)

For criteria3:
  m1 = 8, m2 = 8, guide = 9
  avg = (8 + 8 + 9) / 3 = 25 / 3 = 8.33 → 8 (rounded)

For criteria4:
  m1 = 8, m2 = 7, guide = 8
  avg = (8 + 7 + 8) / 3 = 23 / 3 = 7.67 → 8 (rounded)

AVERAGES: {c1: 17, c2: 9, c3: 8, c4: 8}
TOTAL = 17 + 9 + 8 + 8 = 42
```

**Step 6: Store in Database**
```
INSERT INTO Student:
  id: 1
  name: "John Doe"
  seat_no: "101"
  group_no: (if provided)
  project_title: (if provided)
  project_guide: (if provided)

INSERT INTO Evaluation:
  id: 1
  student_id: 1
  phase: 1
  review_no: 1
  total_marks: 42
  
  # Averages
  criteria1: 17
  criteria2: 9
  criteria3: 8
  criteria4: 8
  
  # Member 1 individual
  member1_criteria1: 17
  member1_criteria2: 9
  member1_criteria3: 8
  member1_criteria4: 8
  
  # Member 2 individual
  member2_criteria1: 16
  member2_criteria2: 8
  member2_criteria3: 8
  member2_criteria4: 7
  
  # Guide individual
  guide_criteria1: 18
  guide_criteria2: 9
  guide_criteria3: 9
  guide_criteria4: 8
```

**Step 7: Display to User**
```
HTML Table:
┌─────────┬──────┬─────────────────────────────────┐
│ Name    │ ID   │ Phase 1 Review 1 Marks          │
├─────────┼──────┼─────────────────────────────────┤
│ Criteria│ M1   │ M2 │ Guide │ Average │ Total    │
├─────────┼──────┼─────────────────────────────────┤
│ Lit Srv │ 17   │ 16 │ 18    │ 17      │          │
│ Problem │ 9    │ 8  │ 9     │ 9       │          │
│ Present │ 8    │ 8  │ 9     │ 8       │          │
│ Q&A     │ 8    │ 7  │ 8     │ 8       │          │
├─────────┴──────┴────┴───────┴─────────┴──────────┤
│ TOTAL:                                      42    │
└────────────────────────────────────────────────────┘
```

---

# SECTION 7: USER INTERFACE FLOWS

## View 1: All Students
```
Shows all students with their marks:
┌─────────────┬─────┬──────────────────────┐
│ Name        │ Gr  │ C1 │ C2 │ C3 │ C4   │
├─────────────┼─────┼────┼────┼────┼──────┤
│ John Doe    │ Gr1 │ 17 │ 9  │ 8  │ 8    │
│ Jane Smith  │ Gr2 │ 16 │ 8  │ 8  │ 7    │
│ Mike Wilson │ Gr1 │ 18 │ 9  │ 9  │ 8    │
└─────────────┴─────┴────┴────┴────┴──────┘
```

## View 2: Group-Wise
```
Groups students by project group:
┌──────────────────────────────────┐
│ GROUP 1                          │
├─────────────┬────┬────┬────┬─────┤
│ John Doe    │ 17 │ 9  │ 8  │ 8   │
│ Mike Wilson │ 18 │ 9  │ 9  │ 8   │
│ Group Total │ 35 │ 18 │ 17 │ 16  │
└─────────────┴────┴────┴────┴─────┘

┌──────────────────────────────────┐
│ GROUP 2                          │
├─────────────┬────┬────┬────┬─────┤
│ Jane Smith  │ 16 │ 8  │ 8  │ 7   │
│ Group Total │ 16 │ 8  │ 8  │ 7   │
└─────────────┴────┴────┴────┴─────┘
```

## View 3: Guide-Wise
```
Groups students by project guide:
┌──────────────────────────────────┐
│ Dr. Smith (Guide)                │
├─────────────┬────┬────┬────┬─────┤
│ John Doe    │ 17 │ 9  │ 8  │ 8   │
│ Jane Smith  │ 16 │ 8  │ 8  │ 7   │
│ Guide Total │ 33 │ 17 │ 16 │ 15  │
└─────────────┴────┴────┴────┴─────┘
```

## View 4: Individual Detail
```
Detailed view for one student:

STUDENT: John Doe
SEAT NO: 101
GROUP: Group 1
GUIDE: Dr. Smith
PROJECT: AI-Based Recommendation System

Marks Detail:
┌──────────────────────────────────────────┐
│                                          │
│ Criteria          M1   M2   Guide   Avg  │
│ Literature Srv    17   16   18      17   │
│ Problem ID        9    8    9       9    │
│ Presentation      8    8    9       8    │
│ Q&A               8    7    8       8    │
│                                          │
│ TOTAL MARKS:      42   39   44      42   │
└──────────────────────────────────────────┘
```

---

# SECTION 8: PDF REPORT EXAMPLE

```
╔════════════════════════════════════════╗
║      GURU NANAK DEV ENG. COLLEGE       ║
║              BIDAR 585403              ║
║    Affiliated to VTU & Approved AICTE  ║
║  Department of Computer Science Eng.   ║
╚════════════════════════════════════════╝

Academic Year: 2024-25        Semester: VII

FINAL YEAR STUDENTS MAJOR PROJECT WORK
CONTINUOUS INTERNAL EVALUATION (CIE)
PHASE - I REVIEW - I

Group No: Group 1
Project Title: AI-Based Recommendation System using Deep Learning

╔════════════════════════════════════════════════════════════╗
║              EVALUATION MARKS TABLE                        ║
╠════════════════════════════════════════════════════════════╣
║                  Marks allotted by Committee               ║
║ Criteria              │ M1 │ M2 │ Guide │ Average         ║
║───────────────────────┼────┼────┼───────┼─────────────────║
║ Literature Survey(20) │ 17 │ 16 │  18   │ 17              ║
║ Problem ID(10)        │ 9  │ 8  │  9    │ 9               ║
║ Presentation(10)      │ 8  │ 8  │  9    │ 8               ║
║ Q&A Session(10)       │ 8  │ 7  │  8    │ 8               ║
╠════════════════════════════════════════════════════════════╣
║ TOTAL (50 Marks)      │ 42 │ 39 │  44   │ 42              ║
╚════════════════════════════════════════════════════════════╝

Remarks: ________________________________________________

Signature: ________________    Date: ________________
```

---

# SECTION 9: KEY FEATURES EXPLAINED

## Feature 1: Flexible Excel Format Detection

**Why it matters:**
- Different evaluators use different formats
- System auto-detects and handles all 3 formats
- No need to train users on specific format

**How it works:**
1. Check if columns have evaluators → Format 1
2. Check if columns have components → Format 2
3. Check if column has total → Format 3
4. If none match → Show error

---

## Feature 2: Fair Mark Distribution (Hamilton Method)

**Why it matters:**
- Mathematically correct
- Preserves exact total
- No marks lost or gained
- Fair to all students

**How it works:**
1. Proportional distribution (may have decimals)
2. Floor all values
3. Sort remainder by fractional part
4. Distribute to highest fractional parts

**Example:**
```
Total 42 → [16.8, 8.4, 8.4, 8.4]
Hamilton → [17, 9, 8, 8] ✓ Sum = 42
```

---

## Feature 3: Multiple Views

**All Students View:**
- Quick overview of entire class
- See all students and marks
- Use case: Class performance analysis

**Group-Wise View:**
- See students grouped by project group
- Calculate group totals
- Use case: Identify strong/weak groups

**Guide-Wise View:**
- See students grouped by project guide
- Calculate guide totals
- Use case: Compare guide performance

**Individual View:**
- Detailed breakdown for one student
- See each evaluator's marks
- Use case: Student counseling

---

## Feature 4: Dynamic Configuration

**Why it matters:**
- Criteria change per phase/review
- No database migration needed
- Change config file, restart app
- System auto-applies to all reports

**Example:**
```
Phase 1 Review 1:
- Literature Survey (20 marks)
- Problem ID (10 marks)
- Presentation (10 marks)
- Q&A (10 marks)

Phase 2 Review 2:
- Conclusion (10 marks)
- Publication (10 marks)
- Presentation (15 marks)
- Q&A (15 marks)

Same criteria1-4 fields, different meanings!
```

---

# SECTION 10: DEPLOYMENT & RUNNING

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python app.py

# 3. Open browser
http://127.0.0.1:5000
```

## Database Options

**SQLite (Default):**
```
- File-based (app.db)
- No setup needed
- Good for development
- Single user
```

**MySQL (Production):**
```
- Requires server setup
- Connection via .env file
- Multi-user support
- Better for large scale
```

---

# SECTION 11: SUMMARY FOR PRESENTATION

## What is PRMES?
Web application for automated project evaluation management

## Key Problems Solved:
1. Manual mark calculation errors
2. Scattered evaluation data
3. Tedious report generation
4. Difficulty tracking across phases

## Key Features:
1. **Smart Excel Import** - 3 format support
2. **Automatic Mark Distribution** - Hamilton method
3. **Multiple Views** - All/Group/Guide/Individual
4. **PDF Reports** - Professional generation
5. **Dynamic Configuration** - Change criteria easily

## Technology Stack:
- **Backend:** Flask + SQLAlchemy
- **Database:** SQLite/MySQL
- **PDF:** ReportLab
- **Excel:** openpyxl
- **Language:** Python

## User Benefits:
- ✓ Save time (automatic processing)
- ✓ Reduce errors (mathematical algorithm)
- ✓ Professional reports (formatted PDFs)
- ✓ Flexible input (3 formats)
- ✓ Multiple analysis views

## Technical Highlights:
- ✓ Smart header normalization (flexible column names)
- ✓ Fair rounding algorithm (Hamilton method)
- ✓ Dynamic configuration (criteria per phase)
- ✓ Proper database design (normalized)
- ✓ Multiple export formats (PDF)

---

# PRESENTATION TALKING POINTS

1. **Problem:** "Evaluating hundreds of students across multiple phases manually is error-prone and time-consuming."

2. **Solution:** "PRMES automates the entire process - upload Excel, system calculates marks, generates reports."

3. **Smart Algorithm:** "We use Hamilton's method to distribute marks fairly - no rounding errors, exact totals preserved."

4. **Flexible Input:** "Accepts 3 different Excel formats - evaluators can use whatever format suits them."

5. **Multiple Views:** "View by all students, group, guide, or individual - choose what insights you need."

6. **Professional Output:** "Generate PDF reports that look like official university documents."

7. **Easy to Deploy:** "Just run Python, opens in browser, no complex setup needed."

8. **Future Ready:** "Dynamic configuration means changing criteria doesn't need database migration."

---

# END OF PRESENTATION GUIDE
