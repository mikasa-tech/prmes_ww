"""
Fix evaluation data so students in the same group have similar marks
(with small variations for individual performance)
"""

from app import create_app
from models import db, Student, Evaluation
import random

def fix_group_marks():
    app = create_app()
    with app.app_context():
        # Get all students grouped by group_no
        students = Student.query.all()
        
        if not students:
            print("No students found in database.")
            return
        
        # Group students by group_no
        groups = {}
        for student in students:
            group_no = student.group_no or "No Group"
            if group_no not in groups:
                groups[group_no] = []
            groups[group_no].append(student)
        
        print(f"Found {len(groups)} groups\n")
        
        from review_config import get_review_config
        
        # For each phase and review
        phase_review_combos = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for phase, review in phase_review_combos:
            print(f"Updating Phase {phase} Review {review}...")
            config = get_review_config(phase, review)
            if not config:
                continue
            
            max_marks = [c['max_marks'] for c in config['criteria']]
            
            # For each group, set base marks
            for group_no, group_students in groups.items():
                # Generate base marks for this group (80-90% of max)
                base_percentage = random.uniform(0.80, 0.90)
                base_member1 = [int(m * base_percentage) for m in max_marks]
                base_member2 = [int(m * base_percentage) for m in max_marks]
                base_guide = [int(m * base_percentage) for m in max_marks]
                
                # Calculate group average marks (same for all students in group)
                group_avg_marks = [
                    int(round((base_member1[i] + base_member2[i] + base_guide[i]) / 3))
                    for i in range(4)
                ]
                group_total = sum(group_avg_marks)
                
                # Apply same total to all students in group
                for student in group_students:
                    # Small variation in individual evaluator marks but same total
                    member1_marks = []
                    member2_marks = []
                    guide_marks = []
                    
                    for i in range(4):
                        # Add small random variations that cancel out
                        var = random.randint(-1, 1)
                        m1 = max(0, min(max_marks[i], base_member1[i] + var))
                        m2 = max(0, min(max_marks[i], base_member2[i] - var))
                        g = max(0, min(max_marks[i], base_guide[i]))
                        
                        member1_marks.append(m1)
                        member2_marks.append(m2)
                        guide_marks.append(g)
                    
                    # Use the same group average marks for all students
                    avg_marks = group_avg_marks
                    total = group_total
                    
                    # Update evaluation
                    ev = Evaluation.query.filter_by(student=student, phase=phase, review_no=review).first()
                    if ev:
                        ev.total_marks = total
                        ev.criteria1 = avg_marks[0]
                        ev.criteria2 = avg_marks[1]
                        ev.criteria3 = avg_marks[2]
                        ev.criteria4 = avg_marks[3]
                        ev.member1_criteria1 = member1_marks[0]
                        ev.member1_criteria2 = member1_marks[1]
                        ev.member1_criteria3 = member1_marks[2]
                        ev.member1_criteria4 = member1_marks[3]
                        ev.member2_criteria1 = member2_marks[0]
                        ev.member2_criteria2 = member2_marks[1]
                        ev.member2_criteria3 = member2_marks[2]
                        ev.member2_criteria4 = member2_marks[3]
                        ev.guide_criteria1 = guide_marks[0]
                        ev.guide_criteria2 = guide_marks[1]
                        ev.guide_criteria3 = guide_marks[2]
                        ev.guide_criteria4 = guide_marks[3]
            
            db.session.commit()
            print(f"  ✅ Updated all groups")
        
        print("\n✅ Fixed! Students in same groups now have similar marks")
        print("\nGroup-wise mark distribution:")
        for group_no, group_students in sorted(groups.items()):
            print(f"\n  Group {group_no}:")
            for student in group_students:
                ev = Evaluation.query.filter_by(student=student, phase=1, review_no=1).first()
                if ev:
                    print(f"    {student.name}: {ev.total_marks}/50")

if __name__ == "__main__":
    fix_group_marks()
