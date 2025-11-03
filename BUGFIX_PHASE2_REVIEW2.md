# Bug Fix: Phase 2 Review 2 Displaying Phase 2 Review 1 Data

## Issue Description

When viewing Phase 2 Review 2 data in the "Individual Detailed" view (`students_individual.html`), clicking on "View" or "PDF" links would show Phase 2 Review 1 data instead of Phase 2 Review 2 data.

**Symptoms:**
- Phase 2 Review 2 component marks matched Phase 2 Review 1
- Marks were showing 15/15/10/10 (P2R1) instead of 10/10/15/15 (P2R2)
- Individual section components were identical between P2R1 and P2R2

## Root Cause

In `templates/students_individual.html` (lines 82-83), the links to `student_detail` and `download_review1` were **not passing the `phase` and `review` query parameters**:

```html
<!-- BEFORE (INCORRECT) -->
<a href="{{ url_for('student_detail', student_id=student.id) }}">View</a>
<a href="{{ url_for('download_review1', student_id=student.id) }}">PDF</a>
```

Since the Flask routes default to `phase=1` and `review=1` when no parameters are provided, clicking these links would always fetch Phase 1 Review 1 data, regardless of which phase/review you were currently viewing.

## Fix Applied

Updated the links to pass the current `phase` and `review` context:

```html
<!-- AFTER (CORRECT) -->
<a href="{{ url_for('student_detail', student_id=student.id, phase=phase, review=review) }}">View</a>
<a href="{{ url_for('download_review1', student_id=student.id, phase=phase, review=review) }}">PDF</a>
```

## Verification

The other template files were already correct:
- ✅ `students.html` - Already passing phase/review parameters
- ✅ `students_groupwise.html` - Already passing phase/review parameters  
- ✅ `students_guidewise.html` - Already passing phase/review parameters
- ❌ `students_individual.html` - **FIXED** - Now passing phase/review parameters

## How the System Works

### Database Structure
- Each student can have up to 4 evaluation records (one per phase/review combination)
- Unique constraint: `(student_id, phase, review_no)`
- The `criteria1` through `criteria4` fields are generic and change meaning based on phase/review

### Phase/Review Configuration (review_config.py)

**Phase 2 Review 1:**
- criteria1: Preliminary studies (15 marks)
- criteria2: Execution & Result Analysis (15 marks)
- criteria3: Project presentation skill (10 marks)
- criteria4: Question and answer session (10 marks)

**Phase 2 Review 2:**
- criteria1: Conclusion & Future scope of work (10 marks)
- criteria2: Publication of project work (10 marks)
- criteria3: Project presentation skill (15 marks)
- criteria4: Question and answer session (15 marks)

### Query Parameter Flow

1. User clicks Phase 2 Review 2 button → URL: `/students/individual?phase=2&review=2`
2. `students_individual()` route receives `phase=2, review=2`
3. Queries: `Evaluation.query.filter_by(student=s, phase=2, review_no=2)`
4. Template renders with `phase=2, review=2` in context
5. **Links must preserve these parameters** when navigating to detail/PDF views

## Testing

To verify the fix:

1. Upload data for Phase 2 Review 1 and Phase 2 Review 2 with different marks
2. Navigate to Individual Detailed view
3. Select Phase 2 Review 2
4. Click "View" or "PDF" for any student
5. Verify the correct Phase 2 Review 2 data is shown (10/10/15/15 criteria weights)

## Related Files

- `templates/students_individual.html` - **FIXED**
- `app.py` (routes that accept phase/review parameters):
  - `students_individual()` - line 318
  - `student_detail()` - line 348
  - `download_review1()` - line 367
- `review_config.py` - Defines criteria for each phase/review
- `models.py` - Database schema with phase and review_no columns

## Prevention

When adding new routes or templates:
1. Always include `phase` and `review` in query parameters (default to 1, 1)
2. Always pass `phase=phase, review=review` in all `url_for()` calls within that view
3. Test all phase/review combinations (4 total) when making changes
