"""
Verify that students in the same group have identical total marks
"""

from app import create_app
from models import db, Student, Evaluation

def verify_group_marks():
    app = create_app()
    with app.app_context():
        students = Student.query.order_by(Student.group_no).all()
        
        # Group students
        groups = {}
        for s in students:
            if s.group_no not in groups:
                groups[s.group_no] = []
            groups[s.group_no].append(s)
        
        print("="*70)
        print("GROUP MARKS VERIFICATION")
        print("="*70)
        
        phase_review_combos = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for phase, review in phase_review_combos:
            print(f"\n{'='*70}")
            print(f"PHASE {phase} REVIEW {review}")
            print(f"{'='*70}")
            
            for group_no in sorted(groups.keys()):
                group_students = groups[group_no]
                print(f"\nGroup {group_no} ({len(group_students)} students):")
                
                for student in group_students:
                    ev = Evaluation.query.filter_by(student=student, phase=phase, review_no=review).first()
                    if ev:
                        print(f"  {student.name:25} : {ev.total_marks}/50")
                
                # Check if all marks are identical
                marks = [Evaluation.query.filter_by(student=s, phase=phase, review_no=review).first().total_marks 
                        for s in group_students]
                if len(set(marks)) == 1:
                    print(f"  ✅ All students have identical marks ({marks[0]}/50)")
                else:
                    print(f"  ⚠️  Marks vary: {marks}")

if __name__ == "__main__":
    verify_group_marks()
