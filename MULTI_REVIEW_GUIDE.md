# 📚 Multi-Phase Review System Guide

## Overview

The PRMES evaluation system now supports **4 distinct reviews**:
- **Phase 1 Review 1**
- **Phase 1 Review 2**
- **Phase 2 Review 1**
- **Phase 2 Review 2**

Each review can be uploaded, viewed, and managed independently.

## 🚀 Getting Started

### First Time Setup (Existing Database)

If you have an existing database, run the migration script first:

```bash
python migrate_db.py
```

This will:
- Add the `phase` column to your database
- Set all existing evaluations to Phase 1
- Update database constraints

### Fresh Installation

For new installations, just run the app normally:

```bash
python app.py
```

The database will be created with the correct schema automatically.

## 📤 Uploading Evaluations

### Step 1: Navigate to Upload Page
- Go to the homepage or click "Upload" in the navigation

### Step 2: Select Phase and Review
- **Phase**: Choose Phase 1 or Phase 2
- **Review**: Choose Review 1 or Review 2

### Step 3: Upload Excel File
- Select your `.xlsx` file containing student evaluations
- File format remains the same as before

### Important Notes:
- ✅ Each phase/review combination can be uploaded independently
- ✅ Re-uploading to the same phase/review will replace that data only
- ✅ Other phases/reviews remain unchanged
- ✅ Student records are shared across all reviews

## 🔍 Viewing Evaluations

### Phase/Review Selector

At the top of every student list page, you'll see a selector with 4 buttons:

**Phase 1:**
- Review 1 | Review 2

**Phase 2:**
- Review 1 | Review 2

The currently selected phase/review is highlighted in **green**.

### View Options

For each phase/review combination, you can view data in 4 ways:

1. **All Students** - Complete list with all evaluations
2. **Group-wise** - Students organized by project group
3. **Guide-wise** - Students organized by project guide
4. **Individual Detailed** - Detailed breakdown for each student

## 📊 PDF Generation

### Individual PDFs

Each PDF automatically shows the correct:
- Phase number (Phase I or Phase II)
- Review number (Review I or Review II)

Download PDFs from:
- Student list view (Download PDF link)
- Individual student detail page

### Summary PDFs

The comprehensive summary PDF includes students from the currently selected phase/review.

## 📁 Data Management

### Excel File Format

Your Excel file should contain:

**Required Columns:**
- `name` or `student_name`
- `seat_no` or `usn`
- Either:
  - `total` marks, OR
  - All four components (`literature_survey`, `problem_identification`, `presentation`, `question_answer`), OR
  - Three evaluator totals (`member1`, `member2`, `internal_guide`)

**Optional Columns:**
- `group_no` - Project group number
- `project_title` - Title of the project
- `project_guide` - Name of project guide

### Database Structure

The system maintains:
- **One student record** per seat number (shared across all reviews)
- **One evaluation record** per student per phase per review
- Total capacity: 4 evaluations per student (one for each phase/review combination)

## 🔄 Workflow Example

### Typical Semester Flow:

1. **Start of Semester - Phase 1 Review 1**
   ```
   Upload → Select Phase 1, Review 1 → Upload Excel
   ```

2. **Mid Phase 1 - Phase 1 Review 2**
   ```
   Upload → Select Phase 1, Review 2 → Upload Excel
   ```

3. **Start Phase 2 - Phase 2 Review 1**
   ```
   Upload → Select Phase 2, Review 1 → Upload Excel
   ```

4. **End of Semester - Phase 2 Review 2**
   ```
   Upload → Select Phase 2, Review 2 → Upload Excel
   ```

### Viewing Progress:

At any time, you can:
- Switch between phases/reviews using the selector
- Compare student performance across different reviews
- Generate reports for specific phases/reviews

## 🎯 Best Practices

### 1. Consistent Student Data
- Keep `seat_no` consistent across all uploads
- The system uses `seat_no` as the unique identifier
- Student name, group, and project can be updated in later uploads

### 2. Organized Uploads
- Upload reviews in chronological order when possible
- Label your Excel files clearly (e.g., `Phase1_Review1.xlsx`)
- Keep backup copies of your Excel files

### 3. Regular Verification
- After each upload, check the student list to verify data
- Download a sample PDF to ensure formatting is correct
- Use the view options to cross-check group and guide assignments

## 🔧 Troubleshooting

### Issue: Can't see data after upload
**Solution**: Make sure you've selected the correct phase and review in the selector

### Issue: Getting unique constraint errors
**Solution**: Run `python migrate_db.py` to update your database schema

### Issue: Wrong phase/review showing in PDF
**Solution**: The PDF reads from the evaluation record - verify you're downloading from the correct phase/review view

### Issue: Student appears in multiple groups
**Solution**: The latest upload's group assignment is used. Ensure consistency in your Excel files

## 📞 Support

For issues or questions:
1. Check this guide first
2. Verify your database is migrated
3. Check the console output for error messages
4. Ensure Excel file format is correct

## 🎓 Summary

The multi-phase review system allows you to:
- ✅ Track student progress across 4 evaluation points
- ✅ Upload and manage evaluations independently
- ✅ Generate phase-specific PDFs and reports
- ✅ Maintain organized records for an entire academic year
- ✅ Compare performance across different review stages

Happy evaluating! 🎉