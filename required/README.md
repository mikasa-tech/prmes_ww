# PRMES - Project Review Management and Evaluation System

A Flask web application for managing student project evaluations across multiple phases and reviews.

## Features

- 4 review phases (Phase 1: Review 1 & 2, Phase 2: Review 1 & 2)
- Multiple evaluators support (Member 1, Member 2, Internal Guide)
- Automatic mark distribution based on criteria weights
- PDF report generation
- Excel upload with flexible formats
- Multiple view options (all, group-wise, guide-wise, individual)
- SQLite and MySQL support

## Installation

```bash
# Clone repository
git clone https://github.com/mikasa-tech/prmes_ww.git
cd prmes_ww

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Access at: **http://127.0.0.1:5000**

## Quick Start

1. **Prepare Excel file** with columns: `Name`, `Seat_no`, `Member 1`, `Member 2`, `Internal Guide`
2. **Upload**: Select Phase and Review, upload Excel file
3. **View**: Browse students (all, group-wise, guide-wise, or individual)
4. **Download**: Generate PDF reports

## Usage

### Views
- **All Students**: Overview with criteria breakdown
- **Group-wise**: Organized by project groups
- **Guide-wise**: Organized by guides
- **Individual**: Detailed breakdown per student

### Reports
- Individual PDFs with evaluator marks and averages
- Comprehensive PDF for all phases/reviews

## Excel Format

Supports three input formats:

**1. Three Evaluator Totals (Recommended)**
- Columns: `Name`, `Seat_no`, `Member 1`, `Member 2`, `Internal Guide`
- System distributes totals across criteria automatically

**2. Component Marks**
- Individual columns for each criterion (e.g., Literature Survey, Presentation, Q&A)

**3. Single Total**
- Columns: `Name`, `Seat_no`, `Total`
- Distributed proportionally

**Optional:** `Project Group`, `Project Title`, `Project Guide`

## Evaluation Criteria

| Phase/Review | Criteria 1 | Criteria 2 | Criteria 3 | Criteria 4 |
|--------------|-----------|-----------|------------|------------|
| P1R1 | Literature Survey (20) | Problem ID (10) | Presentation (10) | Q&A (10) |
| P1R2 | Objectives (10) | Methodology (10) | Presentation (15) | Q&A (15) |
| P2R1 | Preliminary Studies (15) | Execution & Analysis (15) | Presentation (10) | Q&A (10) |
| P2R2 | Conclusion (10) | Publication (10) | Presentation (15) | Q&A (15) |

Total: 50 marks per review

## Project Structure

- `app.py` - Main Flask application
- `models.py` - Database models
- `review_config.py` - Evaluation criteria
- `upload_helpers.py` - Excel processing
- `pdf_template.py` - PDF generation
- `templates/` - HTML templates

## Configuration

**SQLite** (default): No setup needed

**MySQL**: Create `.env` file:
```env
DB_USER=your_user
DB_PASS=your_password
DB_HOST=localhost
DB_NAME=prmes_db
```

**Customize**: Edit `review_config.py` for criteria changes

## Development

**Database reset**: `Remove-Item app.db` then `python app.py`

**Testing**: Run `test_reverse_engineer.py` or `check_excel.py`

**Architecture**: Dynamic criteria system - database stores generic fields, meaning changes via `review_config.py`

## Troubleshooting

- **Port busy**: Change port in `app.py`
- **Database error**: Delete `app.db` and restart
- **Upload fails**: Close Excel file, check columns (`Name`, `Seat_no`)
- **Wrong phase data**: Verify phase/review selection during upload
