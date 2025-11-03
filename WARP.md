# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

PRMES (Project Review Management and Evaluation System) is a Flask-based web application for managing student project evaluations across multiple phases and reviews. The system supports 4 distinct evaluation points (Phase 1 Review 1, Phase 1 Review 2, Phase 2 Review 1, Phase 2 Review 2) for engineering college final year projects.

## Common Commands

### Running the Application

```powershell
# Recommended: Interactive launcher with browser auto-open
python run_local.py

# Alternative: Direct Flask app launch
python app.py

# Windows batch file
.\run_local.bat
```

The application runs on `http://127.0.0.1:5000` (localhost only for security).

### Database Operations

```powershell
# Migrate existing database to support multi-phase reviews
python migrate_db.py

# Delete and recreate database (fresh start)
Remove-Item app.db
python app.py
```

### Testing

```powershell
# Run test fixes
python test_fixes.py

# Test comprehensive PDF generation
python test_comprehensive_pdf.py
```

### Development Dependencies

```powershell
# Install required packages
pip install Flask==3.0.3 Flask-SQLAlchemy==3.1.1 SQLAlchemy==2.0.32 openpyxl==3.1.5 python-dotenv==1.0.1 PyMySQL>=1.1.1 reportlab
```

## Architecture

### Core Design Pattern: Dynamic Configuration System

The system uses a **configuration-driven architecture** where evaluation criteria, weights, and labels change dynamically based on phase and review number. This eliminates hardcoding and enables flexible evaluation schemas.

**Key principle**: The database stores generic `criteria1` through `criteria4` fields, but their semantic meaning (e.g., "Literature Survey" vs "Objectives") is resolved at runtime via `review_config.py`.

### Data Flow

1. **Upload**: Excel → `upload_helpers.py` → Dynamic column mapping → Database (via `models.py`)
2. **View**: Database → Phase/Review filter → `review_config.py` (labels/weights) → Templates
3. **PDF**: Database → `review_config.py` → `pdf_template.py` → Generated PDF

### Three-Layer Model

1. **Data Layer** (`models.py`):
   - `Student`: One record per student (shared across all reviews)
   - `Evaluation`: Multiple records per student (unique per student_id + phase + review_no)
   - Generic criteria columns (`criteria1` to `criteria4`) that adapt meaning based on context

2. **Configuration Layer** (`review_config.py`):
   - Central source of truth for evaluation schemas
   - Maps phase/review combinations to criteria names, max marks, and PDF labels
   - Example: Phase 1 Review 1 → criteria1 = "Literature Survey" (20 marks)
   - Example: Phase 1 Review 2 → criteria1 = "Objectives" (10 marks)

3. **Presentation Layer** (`app.py` + templates):
   - Routes dynamically filter by phase/review query parameters
   - Templates receive `config` object with phase-appropriate labels

### Excel Upload Intelligence

The system supports **three input formats** (auto-detected):

1. **Three evaluator totals**: Member 1, Member 2, Internal Guide total marks
   - Uses `reverse_engineer_components()` to distribute totals across criteria proportionally

2. **Component columns**: Individual criterion marks (e.g., Literature Survey, Problem Identification)
   - Direct mapping to database fields

3. **Single total**: Overall marks only
   - Distributed proportionally using phase/review-specific weights

This flexibility allows the same system to handle different Excel formats from different evaluation committees.

### PDF Generation Strategy

- Individual PDFs (`pdf_template.py`): Single student, one phase/review
- Comprehensive PDFs (`comprehensive_pdf_template.py`): All students, all phases/reviews
- Both use `review_config.py` for dynamic labeling and `reportlab` for precise layout control
- PDFs match official college evaluation forms with college logo, headers, and signatures sections

## Key Files

### Core Application
- `app.py`: Main Flask application with all routes (upload, views, downloads)
- `models.py`: SQLAlchemy models (Student, Evaluation)
- `review_config.py`: **Critical** - Defines evaluation criteria for each phase/review

### Upload Processing
- `upload_helpers.py`: Dynamic column mapping and three-format detection
- `utils.py`: Header normalization and proportional mark distribution (Hamilton rounding)

### PDF Generation
- `pdf_template.py`: Individual student evaluation PDFs
- `comprehensive_pdf_template.py`: Multi-page summary reports

### Templates (Jinja2)
- `upload.html`: Phase/review selector + Excel upload form
- `students.html`: Main list with phase/review button selector
- `students_groupwise.html`, `students_guidewise.html`, `students_individual.html`: Grouped views
- `student_detail.html`: Detailed single student breakdown

## Database Schema

### Student Table
- Primary identifier: `seat_no` (unique across all reviews)
- Shared metadata: `name`, `group_no`, `project_title`, `project_guide`

### Evaluation Table
- Unique constraint: `(student_id, phase, review_no)`
- Generic criteria: `criteria1`, `criteria2`, `criteria3`, `criteria4` (meaning varies by phase/review)
- Individual evaluator marks: `member1_criteria1` through `guide_criteria4` (12 columns)
- Each student can have up to 4 evaluations (one per phase/review combination)

**Important**: Always filter evaluations by both `phase` and `review_no` to avoid mixing data from different reviews.

## Critical Development Rules

### When Modifying Evaluation Criteria

1. **Always update `review_config.py` first** - This is the single source of truth
2. Update both `REVIEW_CRITERIA` dict and helper functions (`get_review_config`, `get_weights_dict`)
3. Database schema (`criteria1-4`) remains unchanged - only semantic meaning changes
4. Test with all three Excel input formats after changes

### When Adding New Routes

- Include `phase` and `review` query parameters (default to 1, 1)
- Pass `config = get_review_config(phase, review)` to templates
- Filter evaluations: `Evaluation.query.filter_by(student=s, phase=phase, review_no=review)`
- Maintain phase/review context in all URL generation: `url_for('route_name', phase=phase, review=review)`

### When Modifying PDF Templates

- Use `config = get_review_config(phase, review)` for dynamic labels
- Access criteria via: `config['criteria'][i-1]['name']` and `config['criteria'][i-1]['max_marks']`
- Check `criterion['guide_marks']` to determine if guide marks apply (criteria 1-2 typically yes, 3-4 typically no)
- PDF headers must show: `Phase {phase_roman}` and `Review {review_roman}` (use Roman numerals I/II)

### Excel Column Mapping

- Always use `normalize_header()` before comparing column names (handles BOM, spaces, case)
- Support multiple synonyms for each field (e.g., "seat_no", "seatno", "usn", "univ_seat_no")
- Validation order: Check for three evaluators → Check for components → Check for total → Raise error

## Database Configuration

### Local Development (SQLite)
Default configuration uses SQLite (`app.db` file) - no setup required.

### Production (MySQL)
Create `.env` file with:
```
DB_USER=your_user
DB_PASS=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=prmes_db
```

The app auto-creates the database if it doesn't exist.

## Testing Strategy

When testing changes:

1. Test with each Excel format (three evaluators, components, total only)
2. Test each phase/review combination (4 total)
3. Verify PDF labels match `review_config.py`
4. Check phase/review filtering in all view modes (all, groupwise, guidewise, individual)
5. Ensure re-uploading to same phase/review replaces only that data

## Common Pitfalls

- **Don't hardcode criteria labels** - Always use `review_config.py`
- **Don't assume evaluation exists** - Always check `ev = Evaluation.query.filter_by(...).first()` and handle None
- **Don't mix phase/review data** - Always include both filters when querying evaluations
- **Don't modify generic column names** (`criteria1-4`) - Modify `review_config.py` instead
- **Don't forget Hamilton rounding** - When distributing marks, use `_hamilton_round()` to maintain exact totals

## Project Structure Rationale

**Why generic criteria columns?**
- Avoids schema migrations when evaluation criteria change
- Enables single codebase to support multiple evaluation types
- Configuration changes don't require database changes

**Why phase + review_no instead of single review_id?**
- Matches academic structure (two phases, two reviews per phase)
- Natural filtering/grouping in UI
- Clear semantic meaning in URLs and reports

**Why three upload formats?**
- Different evaluation committees provide different Excel formats
- System adapts to input rather than forcing specific format
- Reduces data entry errors and manual reformatting

## Future Maintenance

When VTU (university) changes evaluation criteria:
1. Update `REVIEW_CRITERIA` in `review_config.py`
2. No database migration needed
3. No code changes in upload or PDF generation needed
4. System automatically adapts to new criteria labels and weights
