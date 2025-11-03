# PRMES - Project Review Management and Evaluation System

A Flask-based web application for managing and evaluating engineering college final year project reviews across multiple phases and evaluation cycles.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

PRMES streamlines the evaluation process for final year engineering projects by:
- Managing student evaluations across 4 distinct review phases
- Supporting multiple evaluators (Committee Member 1, Member 2, and Internal Guide)
- Automatically distributing marks across evaluation criteria based on phase/review
- Generating professional PDF reports matching official evaluation forms
- Providing multiple views: individual, group-wise, and guide-wise

### Key Features

- **Multi-Phase Support**: Track evaluations across Phase 1 Review 1, Phase 1 Review 2, Phase 2 Review 1, and Phase 2 Review 2
- **Dynamic Criteria System**: Evaluation criteria automatically adapt based on phase and review number
- **Flexible Excel Upload**: Supports three input formats (evaluator totals, component marks, or single total)
- **Professional PDF Generation**: Creates PDFs matching official college evaluation forms with college logo
- **Multiple Views**: View data by all students, groups, guides, or detailed individual breakdowns
- **Database Support**: Works with both SQLite (development) and MySQL (production)

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Excel File Format](#excel-file-format)
- [Evaluation Criteria](#evaluation-criteria)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone the Repository

```bash
git clone https://github.com/mikasa-tech/prmes_ww.git
cd prmes_ww
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- Flask==3.0.3
- Flask-SQLAlchemy==3.1.1
- SQLAlchemy==2.0.32
- openpyxl==3.1.5
- python-dotenv==1.0.1
- PyMySQL>=1.1.1
- reportlab (for PDF generation)

### Step 3: Run the Application

**Option 1: Interactive Launcher (Recommended)**
```bash
python run_local.py
```

**Option 2: Direct Launch**
```bash
python app.py
```

**Option 3: Windows Batch File**
```bash
run_local.bat
```

The application will start at: **http://127.0.0.1:5000**

## 🎓 Quick Start

### 1. Prepare Your Data

Create an Excel file (.xlsx) with the following columns:
- **Required**: `Name`, `Seat_no`
- **Evaluation Data**: Either `Member 1`, `Member 2`, `Internal Guide` (totals)
- **Optional**: `Project Group`, `Project Title`, `Project Guide`

### 2. Upload Evaluations

1. Navigate to the Upload page
2. Select **Phase** (1 or 2) and **Review** (1 or 2)
3. Choose your Excel file
4. Click **Upload**

### 3. View Results

- **All Students**: Complete list with all evaluations
- **Group-wise**: Organized by project groups
- **Guide-wise**: Organized by project guides
- **Individual Detailed**: Detailed breakdown with evaluator marks

### 4. Generate Reports

- Click **View** to see student details
- Click **Download PDF** for individual evaluation reports
- Click **Download Summary PDF** for comprehensive reports

## 📊 Usage Guide

### Navigation

The system provides phase/review selectors on all view pages:

```
Phase 1: [Review 1] [Review 2]
Phase 2: [Review 1] [Review 2]
```

The currently selected phase/review is highlighted in green.

### View Options

1. **All Students View**: Quick overview of all students with criteria breakdown
2. **Group-wise View**: Students organized by project groups
3. **Guide-wise View**: Students organized by their project guides (shows guide's marks highlighted)
4. **Individual Detailed View**: Complete breakdown showing all three evaluators' marks

### PDF Reports

**Individual PDFs:**
- Show student details, project information
- Display all three evaluators' marks
- Calculate averages automatically
- Include signature sections

**Comprehensive PDF:**
- Multi-page report covering all phases and reviews
- Organized by groups and guides
- Summary statistics for each phase/review

## 📁 Excel File Format

### Format 1: Three Evaluator Totals (Recommended)

```
| Name      | Seat_no      | Member 1 | Member 2 | Internal Guide | ... |
|-----------|--------------|----------|----------|----------------|-----|
| John Doe  | 3GN22CS001  | 45       | 46       | 50             | ... |
```

The system automatically distributes these totals across criteria based on phase/review weights.

### Format 2: Component Marks

```
| Name      | Literature Survey | Problem Identification | Presentation | Q&A | ... |
|-----------|-------------------|------------------------|--------------|-----|-----|
| John Doe  | 18                | 9                      | 10           | 9   | ... |
```

Column names must match the criteria names for the specific phase/review.

### Format 3: Single Total

```
| Name      | Seat_no      | Total | ... |
|-----------|--------------|-------|-----|
| John Doe  | 3GN22CS001  | 46    | ... |
```

The system distributes the total proportionally across criteria.

### Optional Columns

- `Project Group` / `Group No`: Group number
- `Project Title`: Title of the project
- `Project Guide`: Name of the project guide

## 📝 Evaluation Criteria

### Phase 1 Review 1 (Total: 50 marks)
- Literature Survey: **20 marks** (Guide)
- Problem Identification: **10 marks** (Guide)
- Project Presentation Skill: **10 marks** (Committee)
- Question and Answer Session: **10 marks** (Committee)

### Phase 1 Review 2 (Total: 50 marks)
- Objectives: **10 marks** (Guide)
- Methodology: **10 marks** (Guide)
- Project Presentation Skill: **15 marks** (Committee)
- Question and Answer Session: **15 marks** (Committee)

### Phase 2 Review 1 (Total: 50 marks)
- Preliminary Studies: **15 marks** (Guide)
- Execution & Result Analysis: **15 marks** (Guide)
- Project Presentation Skill: **10 marks** (Committee)
- Question and Answer Session: **10 marks** (Committee)

### Phase 2 Review 2 (Total: 50 marks)
- Conclusion & Future Scope: **10 marks** (Guide)
- Publication of Project Work: **10 marks** (Guide)
- Project Presentation Skill: **15 marks** (Committee)
- Question and Answer Session: **15 marks** (Committee)

**Note**: "Guide" criteria are evaluated by the Internal Guide, while "Committee" criteria are evaluated by both committee members.

## 🏗️ Project Structure

```
prmes_ww/
├── app.py                              # Main Flask application
├── models.py                           # Database models (Student, Evaluation)
├── review_config.py                    # Evaluation criteria configuration
├── utils.py                            # Utility functions (normalization, mark distribution)
├── upload_helpers.py                   # Excel upload processing
├── pdf_template.py                     # Individual PDF generation
├── comprehensive_pdf_template.py       # Summary PDF generation
├── run_local.py                        # Interactive application launcher
├── requirements.txt                    # Python dependencies
├── templates/                          # Jinja2 HTML templates
│   ├── base.html                       # Base template
│   ├── upload.html                     # Upload page
│   ├── students.html                   # All students view
│   ├── students_groupwise.html         # Group-wise view
│   ├── students_guidewise.html         # Guide-wise view
│   ├── students_individual.html        # Individual detailed view
│   └── student_detail.html             # Single student detail
├── exports/                            # CSV exports directory
├── WARP.md                             # Development guide for AI assistants
└── BUGFIX_PHASE2_REVIEW2.md           # Bug fix documentation
```

## ⚙️ Configuration

### Local Development (SQLite)

No configuration needed. The application automatically creates `app.db` in the project directory.

### Production (MySQL)

Create a `.env` file in the project root:

```env
DB_USER=your_mysql_user
DB_PASS=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=prmes_db
```

The application automatically creates the database if it doesn't exist.

### Customization

**Modify Evaluation Criteria:**

Edit `review_config.py` to change criteria names, max marks, or add new phase/review combinations.

**Change College Information:**

Edit headers in `pdf_template.py` and `comprehensive_pdf_template.py`:
```python
Paragraph("<b>YOUR COLLEGE NAME</b><br/>"
         "<font size=9>Affiliated to YOUR UNIVERSITY</font><br/>"
         "<font size=10><b>Department of YOUR DEPARTMENT</b></font>", title_style)
```

**Replace College Logo:**

Replace `college_logo.png` with your college logo (recommended: 25mm x 25mm).

## 🛠️ Development

### Database Operations

**Migrate existing database:**
```bash
python migrate_db.py
```

**Fresh start (delete and recreate):**
```bash
Remove-Item app.db
python app.py
```

### Testing

**Test reverse engineering logic:**
```bash
python test_reverse_engineer.py
```

**Check Excel file structure:**
```bash
python check_excel.py
```

**Re-upload specific phase/review:**
```bash
# Edit PHASE and REVIEW in reupload_p2r2.py
python reupload_p2r2.py
```

### Key Architecture Concepts

**Dynamic Configuration System:**
- Database stores generic `criteria1` through `criteria4` fields
- Meaning changes based on phase/review via `review_config.py`
- No database migrations needed when criteria change

**Three-Layer Model:**
1. **Data Layer** (`models.py`): Student and Evaluation tables
2. **Configuration Layer** (`review_config.py`): Criteria definitions
3. **Presentation Layer** (`app.py` + templates): Dynamic labeling

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Change port in app.py
app.run(host="127.0.0.1", port=5001, debug=True)
```

### Database Errors
```bash
# Delete database and restart
Remove-Item app.db
python app.py
```

### Excel Upload Fails

1. Ensure Excel file is closed
2. Check required columns exist (`Name`, `Seat_no`)
3. Verify evaluator columns or total column present
4. Check for special characters or BOM in headers

### Wrong Criteria Showing

1. Verify you selected the correct Phase and Review during upload
2. Check phase/review selector on view pages
3. Re-upload with correct phase/review selection

### Phase 2 Review 2 Shows P2R1 Data

This was a known issue (fixed in commit 83ffa58). Update to latest version.

## 📖 Documentation

- **WARP.md**: Comprehensive development guide (architecture, patterns, critical rules)
- **LOCAL_SETUP.md**: Local setup instructions
- **MULTI_REVIEW_GUIDE.md**: Multi-phase review system guide
- **BUGFIX_PHASE2_REVIEW2.md**: Bug fix documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Guidelines

- Always update `review_config.py` first when modifying criteria
- Include `phase` and `review` parameters in all routes
- Pass `phase=phase, review=review` in all `url_for()` calls
- Test with all three Excel input formats
- Use `normalize_header()` before comparing column names

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏫 Institution

Developed for **Guru Nanak Dev Engineering College, Bidar**  
Department of Computer Science Engineering

## 👥 Authors

- Initial development and maintenance: [Your Team/Organization]
- Bug fixes and enhancements: [Contributors]

## 🙏 Acknowledgments

- VTU (Visvesvaraya Technological University) for evaluation guidelines
- Flask and SQLAlchemy communities
- ReportLab for PDF generation capabilities

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub: https://github.com/mikasa-tech/prmes_ww/issues
- Email: [your-email@example.com]

---

**Made with ❤️ for Engineering Education**
