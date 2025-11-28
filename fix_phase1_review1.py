"""
Fix Phase 1 Review 1 data:
- Criteria 1 (Literature Survey): Only Guide has marks, M1 and M2 should be 0
- Criteria 2 (Problem Identification): Only Guide has marks, M1 and M2 should be 0
- Criteria 3 & 4: Keep current marks (all evaluators provided marks)
"""

from app import create_app
from models import db, Evaluation

def fix_phase1_review1():
    app = create_app()
    with app.app_context():
        print("="*70)
        print("FIXING PHASE 1 REVIEW 1 DATA")
        print("="*70)
        print("\nSetting Member-1 and Member-2 marks to 0 for Criteria 1 & 2")
        print("(Only Guide provided marks for Literature Survey and Problem ID)\n")
        
        # Get all Phase 1 Review 1 evaluations
        evaluations = Evaluation.query.filter_by(phase=1, review_no=1).all()
        
        if not evaluations:
            print("No Phase 1 Review 1 evaluations found!")
            return
        
        print(f"Found {len(evaluations)} records to fix\n")
        
        for ev in evaluations:
            student_name = ev.student.name if ev.student else "Unknown"
            print(f"Fixing {student_name}:")
            print(f"  Before - C1: M1={ev.member1_criteria1}, M2={ev.member2_criteria1}, G={ev.guide_criteria1} -> Avg={ev.criteria1}")
            print(f"  Before - C2: M1={ev.member1_criteria2}, M2={ev.member2_criteria2}, G={ev.guide_criteria2} -> Avg={ev.criteria2}")
            
            # Set Member-1 and Member-2 to 0 for criteria 1 and 2
            ev.member1_criteria1 = 0
            ev.member2_criteria1 = 0
            ev.member1_criteria2 = 0
            ev.member2_criteria2 = 0
            
            # Recalculate averages for criteria 1 and 2 (now just Guide marks)
            # Criteria 1: Only Guide has marks
            guide1 = ev.guide_criteria1 or 0
            ev.criteria1 = guide1  # Average is just the guide mark
            
            # Criteria 2: Only Guide has marks
            guide2 = ev.guide_criteria2 or 0
            ev.criteria2 = guide2  # Average is just the guide mark
            
            # Recalculate total
            ev.total_marks = (ev.criteria1 or 0) + (ev.criteria2 or 0) + (ev.criteria3 or 0) + (ev.criteria4 or 0)
            
            print(f"  After  - C1: M1=0, M2=0, G={ev.guide_criteria1} -> Avg={ev.criteria1}")
            print(f"  After  - C2: M1=0, M2=0, G={ev.guide_criteria2} -> Avg={ev.criteria2}")
            print(f"  New Total: {ev.total_marks}\n")
        
        # Commit all changes
        db.session.commit()
        
        print("="*70)
        print("✅ Phase 1 Review 1 data fixed!")
        print("="*70)
        print("\nNow:")
        print("  - Literature Survey average = Guide mark only")
        print("  - Problem Identification average = Guide mark only")
        print("  - PDFs will show correct averages")

if __name__ == "__main__":
    fix_phase1_review1()
