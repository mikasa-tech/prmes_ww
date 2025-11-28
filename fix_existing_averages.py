"""
Fix all existing evaluation records to use correct average calculation
(only counting non-zero evaluators)
"""

from app import create_app
from models import db, Evaluation

def fix_existing_averages():
    app = create_app()
    with app.app_context():
        print("="*70)
        print("FIXING ALL EXISTING EVALUATION AVERAGES")
        print("="*70)
        
        all_evaluations = Evaluation.query.all()
        print(f"\nFound {len(all_evaluations)} evaluation records to check/fix\n")
        
        fixed_count = 0
        unchanged_count = 0
        
        for ev in all_evaluations:
            changes_made = False
            
            # For each criterion, recalculate the average
            for i in range(1, 5):
                member1_mark = getattr(ev, f'member1_criteria{i}') or 0
                member2_mark = getattr(ev, f'member2_criteria{i}') or 0
                guide_mark = getattr(ev, f'guide_criteria{i}') or 0
                
                # Count non-zero evaluators
                evaluators = [member1_mark, member2_mark, guide_mark]
                non_zero = [val for val in evaluators if val > 0]
                
                # Calculate correct average
                if non_zero:
                    correct_avg = int(round(sum(non_zero) / len(non_zero)))
                else:
                    correct_avg = 0
                
                # Get current average
                current_avg = getattr(ev, f'criteria{i}') or 0
                
                # Update if different
                if current_avg != correct_avg:
                    setattr(ev, f'criteria{i}', correct_avg)
                    changes_made = True
                    print(f"  Fixed criteria{i}: {current_avg} → {correct_avg} "
                          f"(M1={member1_mark}, M2={member2_mark}, G={guide_mark})")
            
            # Recalculate total
            new_total = (ev.criteria1 or 0) + (ev.criteria2 or 0) + (ev.criteria3 or 0) + (ev.criteria4 or 0)
            if ev.total_marks != new_total:
                old_total = ev.total_marks
                ev.total_marks = new_total
                changes_made = True
                print(f"  Fixed total: {old_total} → {new_total}")
            
            if changes_made:
                fixed_count += 1
                student_name = ev.student.name if ev.student else "Unknown"
                print(f"✅ Fixed: {student_name} - Phase {ev.phase} Review {ev.review_no}")
            else:
                unchanged_count += 1
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Total records checked: {len(all_evaluations)}")
        print(f"Records fixed: {fixed_count}")
        print(f"Records unchanged: {unchanged_count}")
        print("\n✅ All existing averages have been corrected!")
        print("="*70)

if __name__ == "__main__":
    fix_existing_averages()
