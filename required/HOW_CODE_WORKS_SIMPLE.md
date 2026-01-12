# How PRMES Code Works - Simple Explanation

## The Big Picture: 3 Steps

```
Step 1: User uploads Excel file
        ↓
Step 2: System processes & stores in database
        ↓
Step 3: User views data & downloads PDF
```

---

## Step 1: User Uploads Excel File

### What user sees:
- Navigate to http://127.0.0.1:5000
- Click "Upload"
- Select Phase and Review
- Choose Excel file (.xlsx)
- Click Upload

### What happens in code:

**File: `app.py` - Routes section**

```python
@app.route("/upload", methods=["GET", "POST"])
def upload_csv():
    if request.method == "POST":
        # 1. Get phase and review from form
        phase = int(request.form.get("phase", 1))      # e.g., 1
        review_no = int(request.form.get("review", 1))  # e.g., 1
        
        # 2. Get Excel file from upload
        file = request.files.get("file")
        
        # 3. Read the Excel file
        raw = file.stream.read()
        wb = load_workbook(io.BytesIO(raw), data_only=True)
        ws = wb.active
        
        # 4. Get header row (first row with column names)
        header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), tuple())
        # Result: ["Name", "Seat_no", "Member 1", "Member 2", "Internal Guide"]
```

**In plain English:**
```
IF user clicked Upload button:
    1. Read form → phase=1, review=1
    2. Read file from browser
    3. Open Excel file
    4. Get header row (column names)
```

---

## Step 2: Parse Headers & Map Columns

### The Challenge:
Different teachers write column names differently!
```
Some write: "Name"        → Others write: "Student Name", "student_name"
Some write: "Seat_no"     → Others write: "USN", "Roll Number", "Seatno"
Some write: "Member 1"    → Others write: "Member1", "M1", "Chairperson"
```

### Solution: Normalize Headers

**File: `utils.py`**

```python
def normalize_header(h: str) -> str:
    """Convert any header to standard format"""
    
    # Example: "Student Name" → "student_name"
    s = h.lower()                      # "student name"
    s = s.strip()                      # remove spaces
    s = re.sub(r"[^a-z0-9]+", "_", s) # replace spaces with _
    # Result: "student_name"
    
    # Example: "Member 1" → "member_1"
    # Example: "Seat-No" → "seat_no"
    # Example: "TOTAL MARKS" → "total_marks"
```

### Map Columns to Keys

**File: `app.py` - lines 108-127**

```python
key_map = {}  # Will store mapping like {"name": "Name", "seat_no": "Seat_no"}

for raw in fieldnames:  # fieldnames = ["Name", "Seat_no", "Member 1", ...]
    h = normalize_header(raw)  # "name", "seat_no", "member_1", ...
    
    # Match common names
    if h in ("name", "student_name"):
        key_map["name"] = raw  # key_map["name"] = "Name"
    
    elif h in ("seat_no", "seatno", "usn"):
        key_map["seat_no"] = raw  # key_map["seat_no"] = "Seat_no"
    
    elif h in ("member1", "member_1"):
        key_map["member1"] = raw  # key_map["member1"] = "Member 1"
    
    # ... and so on for all columns
```

**In plain English:**
```
FOR each column header in Excel:
    1. Normalize the name (make it consistent)
    2. Check what it means
    3. Add to key_map dictionary
    
Result: key_map = {
    "name": "Name",
    "seat_no": "Seat_no",
    "member1": "Member 1",
    "member2": "Member 2",
    "internal_guide": "Internal Guide"
}
```

---

## Step 3: Detect Format & Process Data

### Detect which format user uploaded

**File: `app.py` - lines 138-142**

```python
# Check what columns we have
has_three_evaluators = all(k in key_map for k in ("member1", "member2", "internal_guide"))
has_components = all(...component columns...)
has_total = "total" in key_map

# Decide which handler to use
if has_three_evaluators:
    # Format 1: Three evaluators
    use_format_1()
elif has_components:
    # Format 2: Individual components
    use_format_2()
elif has_total:
    # Format 3: Single total
    use_format_3()
else:
    # Error: missing required data
    raise Error("Missing required columns")
```

**In plain English:**
```
IF (Member1 AND Member2 AND Guide columns exist):
    This is Format 1 (three evaluators)
ELSE IF (all 4 component columns exist):
    This is Format 2 (component marks)
ELSE IF (Total column exists):
    This is Format 3 (single total)
ELSE:
    ERROR - can't detect format
```

---

## Step 4: Reverse Engineer (Format 1 Example)

**File: `upload_helpers.py` - lines 44-71**

### For each evaluator (Member 1, Member 2, Guide):

```python
def handle_three_evaluators(row, key_map, phase, review):
    # Get the total marks from Excel
    member1_total = int(float(row.get(key_map["member1"], 0)))  # e.g., 42
    member2_total = int(float(row.get(key_map["member2"], 0)))  # e.g., 39
    guide_total = int(float(row.get(key_map["internal_guide"], 0)))  # e.g., 44
    
    # Reverse engineer each evaluator's total into 4 components
    member1_comp = reverse_engineer_components(42, phase=1, review=1)
    # Result: {"criteria1": 17, "criteria2": 8, "criteria3": 9, "criteria4": 8}
    
    member2_comp = reverse_engineer_components(39, phase=1, review=1)
    # Result: {"criteria1": 16, "criteria2": 8, "criteria3": 8, "criteria4": 7}
    
    guide_comp = reverse_engineer_components(44, phase=1, review=1)
    # Result: {"criteria1": 18, "criteria2": 9, "criteria3": 9, "criteria4": 8}
    
    # Calculate average
    comp = {}
    for key in member1_comp.keys():
        m1 = member1_comp[key]     # 17
        m2 = member2_comp[key]     # 16
        g = guide_comp[key]        # 18
        
        comp[key] = int(round((m1 + m2 + g) / 3))  # (17+16+18)/3 = 17
    
    return comp, member1_comp, member2_comp, guide_comp
```

**In plain English:**
```
For each evaluator:
    1. Read their total from Excel
    2. Call reverse_engineer_components(total)
    3. Get back 4 component marks
    
Then:
    1. For each component, calculate average of 3 evaluators
    2. Round the average
    3. Return everything
```

### Reverse Engineer Algorithm

**File: `utils.py` - lines 42-50**

```python
def reverse_engineer_components(total, phase=1, review=1):
    # Get weights for this phase/review
    weights = get_weights_dict(phase, review)
    # Result for Phase 1 Review 1: {criteria1: 20, criteria2: 10, criteria3: 10, criteria4: 10}
    
    # Clamp total between 0-50
    t = max(0, min(int(total), 50))  # total=42 stays 42
    
    # Step 1: Proportional scaling
    scaled = {k: (t * (w / 50)) for k, w in weights.items()}
    # scaled = {
    #     criteria1: 42 * (20/50) = 16.8,
    #     criteria2: 42 * (10/50) = 8.4,
    #     criteria3: 42 * (10/50) = 8.4,
    #     criteria4: 42 * (10/50) = 8.4
    # }
    
    # Step 2: Hamilton rounding (preserve sum)
    return _hamilton_round(scaled, t)  # Returns rounded integers summing to 42
```

**Hamilton Rounding Algorithm**

```python
def _hamilton_round(values, target_sum):
    # Step 1: Floor each value
    floors = {k: int(v) for k, v in values.items()}
    # {criteria1: 16, criteria2: 8, criteria3: 8, criteria4: 8}
    # Sum = 40
    
    # Step 2: Calculate remainder
    remainder = target_sum - sum(floors.values())  # 42 - 40 = 2
    
    # Step 3: Sort by fractional part
    fracs = sorted(
        ((k, values[k] - floors[k]) for k in values),
        key=lambda x: x[1],
        reverse=True
    )
    # fracs = [
    #     (criteria1, 0.8),  ← highest
    #     (criteria2, 0.4),
    #     (criteria3, 0.4),
    #     (criteria4, 0.4)
    # ]
    
    # Step 4: Distribute remainder
    result = floors.copy()
    for i in range(remainder):  # 2 times
        key = fracs[i % len(fracs)][0]
        result[key] += 1
    
    # i=0: key = fracs[0][0] = criteria1, result[criteria1] = 17
    # i=1: key = fracs[1][0] = criteria2, result[criteria2] = 9
    
    return result
    # {criteria1: 17, criteria2: 9, criteria3: 8, criteria4: 8}
    # Sum = 42 ✓
```

---

## Step 5: Store in Database

**File: `app.py` - lines 193-214**

```python
# For each row in Excel:
for row in rows_iter:  # row = {"Name": "John", "Seat_no": "101", ...}
    name = str(row.get(key_map["name"], "")).strip()  # "John"
    seat_no = str(row.get(key_map["seat_no"], "")).strip()  # "101"
    
    # Skip if missing required fields
    if not name or not seat_no:
        continue
    
    # Get or create student in database
    student = Student.query.filter_by(seat_no=seat_no).one_or_none()
    if not student:
        student = Student(
            name=name,
            seat_no=seat_no,
            group_no=group_no,
            project_title=project_title,
            project_guide=project_guide
        )
        db.session.add(student)
    
    # Process marks using map_excel_columns_to_criteria
    comp, member1_comp, member2_comp, guide_comp = map_excel_columns_to_criteria(
        row, key_map, phase, review_no
    )
    
    # Create evaluation record
    evaluation = Evaluation(
        student=student,
        phase=phase,
        review_no=review_no,
        total_marks=sum(comp.values()),
        criteria1=comp["criteria1"],
        criteria2=comp["criteria2"],
        criteria3=comp["criteria3"],
        criteria4=comp["criteria4"],
        member1_criteria1=member1_comp["criteria1"],
        # ... all individual evaluator marks ...
        guide_criteria4=guide_comp["criteria4"]
    )
    
    db.session.add(evaluation)

# Save all to database
db.session.commit()
```

**In plain English:**
```
FOR each row in Excel file:
    1. Extract: name, seat_no, and optional fields
    2. Check if student already exists in database
    3. If not, create new student
    4. Process marks (reverse engineer if needed)
    5. Create evaluation record with all marks
    6. Add to database
    
THEN:
    Save everything to database
```

---

## Step 6: User Views Data

**File: `app.py` - routes like `/students`, `/students/groupwise`, etc.**

```python
@app.route("/students")
def view_students():
    phase = request.args.get("phase", 1, type=int)
    review = request.args.get("review", 1, type=int)
    view_type = request.args.get("view", "all")  # all, groupwise, guidewise, individual
    
    # Query database
    if view_type == "all":
        students = Student.query.all()
        
    elif view_type == "groupwise":
        # Group students by project group
        students = Student.query.all()
        # Group them: {group1: [student1, student2], group2: [...]}
        
    elif view_type == "guidewise":
        # Group students by project guide
        
    # For each student, get their evaluation for this phase/review
    for student in students:
        evaluation = Evaluation.query.filter_by(
            student=student,
            phase=phase,
            review_no=review
        ).one_or_none()
    
    # Pass to HTML template for display
    return render_template("students.html", students=students, evaluations=evaluations)
```

**In plain English:**
```
1. Get phase, review, and view type from URL
2. Query database for students
3. Group them if needed (groupwise/guidewise)
4. Get evaluation marks for each student
5. Display in HTML table
```

---

## Step 7: Generate PDF

**File: `pdf_template.py`**

```python
def build_review1_pdf(student, evaluation, phase, review):
    """Create professional PDF report"""
    
    buffer = io.BytesIO()  # Create empty PDF in memory
    doc = SimpleDocTemplate(buffer, pagesize=A4)  # A4 size
    
    elements = []  # Will add elements to this list
    
    # 1. Add college logo and header
    elements.append(get_college_logo())
    elements.append(Paragraph("GURU NANAK DEV ENGINEERING COLLEGE"))
    
    # 2. Add student info
    elements.append(Paragraph(f"Name: {student.name}"))
    elements.append(Paragraph(f"Group: {student.group_no}"))
    elements.append(Paragraph(f"Project: {student.project_title}"))
    
    # 3. Create marks table
    # Get criteria for this phase/review
    config = get_review_config(phase, review)
    
    table_data = []
    # Add headers
    table_data.append(["Criteria", "Member 1", "Member 2", "Guide", "Average"])
    
    # Add each criterion
    for i in range(1, 5):
        m1 = evaluation.member1_criteria{i}
        m2 = evaluation.member2_criteria{i}
        guide = evaluation.guide_criteria{i}
        avg = evaluation.criteria{i}
        
        table_data.append([
            config['criteria'][i-1]['name'],
            str(m1),
            str(m2),
            str(guide),
            str(avg)
        ])
    
    # Create table
    table = Table(table_data)
    elements.append(table)
    
    # 4. Build PDF from elements
    doc.build(elements)
    
    # Return PDF as file
    return buffer.getvalue()
```

**In plain English:**
```
1. Create empty PDF in memory
2. Add header (logo, college name)
3. Add student information (name, group, project)
4. Create table with marks from database
5. Build everything into PDF
6. Return PDF file to user
```

---

## Complete Flow Summary

```
┌─────────────────────────────────────────┐
│ 1. User opens http://127.0.0.1:5000     │
└──────────────────┬──────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────┐
│ 2. Click "Upload"                       │
│    Select Phase 1, Review 1             │
│    Choose Excel file                    │
└──────────────────┬──────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────┐
│ 3. app.py receives file                 │
│    - normalize_header() fixes col names │
│    - map_excel_columns_to_criteria()    │
│      detects format (1, 2, or 3)        │
└──────────────────┬──────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────┐
│ 4. Process data                         │
│    - reverse_engineer_components()      │
│    - _hamilton_round() for fair dist    │
│    - Calculate averages                 │
└──────────────────┬──────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────┐
│ 5. Store in database                    │
│    - Create/update Student              │
│    - Create Evaluation record           │
│    - Save to app.db or MySQL            │
└──────────────────┬──────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────┐
│ 6. User views data                      │
│    - Click "View Students"              │
│    - Select view type (all, group, etc) │
│    - Display in HTML table              │
└──────────────────┬──────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────┐
│ 7. Generate PDF (optional)              │
│    - Click "Download PDF"               │
│    - build_review1_pdf() creates report │
│    - User saves as .pdf file            │
└─────────────────────────────────────────┘
```

---

## Files & What They Do

| File | What it does |
|------|-------------|
| `app.py` | Main application - handles routes (upload, view, download) |
| `models.py` | Database structure - Student and Evaluation tables |
| `review_config.py` | Configuration - defines criteria for each phase/review |
| `upload_helpers.py` | Detects Excel format and routes to correct handler |
| `utils.py` | Helper functions - normalize headers, reverse engineer marks |
| `pdf_template.py` | Creates individual PDF reports |
| `comprehensive_pdf_template.py` | Creates summary PDF for all phases |

---

## Quick Example: User uploads Excel

### Excel file:
```
Name      | Seat_no | Member 1 | Member 2 | Internal Guide
John Doe  | 101     | 42       | 39       | 44
```

### What code does:

```
1. app.py reads file
   ↓
2. normalize_header() → "Member 1" becomes "member_1"
   ↓
3. detect format → "Has member1, member2, internal_guide" → Format 1
   ↓
4. For John Doe:
   - member1_comp = reverse_engineer(42) → [17, 8, 9, 8]
   - member2_comp = reverse_engineer(39) → [16, 8, 8, 7]
   - guide_comp = reverse_engineer(44) → [18, 9, 9, 8]
   
   - comp = average → [17, 8, 8, 7]
   ↓
5. Create Student and Evaluation records
   ↓
6. Save to database
   ↓
7. User clicks "View" → Shows table with marks
   ↓
8. User clicks "PDF" → build_review1_pdf() generates report
```

### Result in database:

```
Student table:
  id | name     | seat_no | group_no | project_title | project_guide
  1  | John Doe | 101     | Group 1  | ...           | Dr. Smith

Evaluation table:
  id | student_id | phase | review_no | criteria1 | criteria2 | criteria3 | criteria4 | total_marks
  1  | 1          | 1     | 1         | 17        | 8         | 8         | 7         | 40

  member1_criteria1 | member1_criteria2 | member1_criteria3 | member1_criteria4
  17                | 8                 | 9                 | 8

  member2_criteria1 | member2_criteria2 | member2_criteria3 | member2_criteria4
  16                | 8                 | 8                 | 7

  guide_criteria1 | guide_criteria2 | guide_criteria3 | guide_criteria4
  18              | 9               | 9               | 8
```

---

## That's it! 

The entire system is just:
1. **Upload** → Read Excel
2. **Parse** → Understand column names
3. **Process** → Reverse engineer marks if needed
4. **Store** → Save to database
5. **Display** → Show in table or PDF
