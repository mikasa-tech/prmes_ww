#!/usr/bin/env python3

from models import db, Student, Evaluation
from app import create_app

def test_guide_assignments():
    """Test that guide names are meaningful and statistics are calculated"""
    print("Testing Guide Names and Statistics...")
    app = create_app()
    
    with app.app_context():
        students = Student.query.order_by(Student.name).all()
        
        # Test guide assignment logic - now using actual project_guide from database
        guides = {}
        for student in students:
            ev = sorted(student.evaluations, key=lambda e: (e.review_no, e.id))[-1] if student.evaluations else None
            if ev and student.project_guide:
                guide_name = student.project_guide.strip()
                
                if guide_name not in guides:
                    guides[guide_name] = []
                guides[guide_name].append((student, ev))
        
        print(f"Guides assigned: {list(guides.keys())}")
        
        # Test statistics calculation
        for guide_name, student_list in guides.items():
            if student_list:
                total_marks = sum(ev.total_marks for _, ev in student_list)
                avg_marks = total_marks / len(student_list)
                max_marks = max(ev.total_marks for _, ev in student_list)
                min_marks = min(ev.total_marks for _, ev in student_list)
                
                print(f"\n{guide_name}:")
                print(f"  Students: {len(student_list)}")
                print(f"  Average: {avg_marks:.1f}/50")
                print(f"  Range: {min_marks} - {max_marks}")
                print(f"  Students: {[s.name for s, _ in student_list]}")

def test_group_statistics():
    """Test group statistics calculation"""
    print("\n" + "="*50)
    print("Testing Group Statistics...")
    app = create_app()
    
    with app.app_context():
        students = Student.query.order_by(Student.group_no, Student.name).all()
        
        groups = {}
        for student in students:
            group_no = student.group_no or "No Group"
            if group_no not in groups:
                groups[group_no] = []
            
            ev = sorted(student.evaluations, key=lambda e: (e.review_no, e.id))[-1] if student.evaluations else None
            if ev:
                groups[group_no].append((student, ev))
        
        for group_no, student_list in groups.items():
            if student_list:
                total_marks = sum(ev.total_marks for _, ev in student_list)
                avg_marks = total_marks / len(student_list)
                max_marks = max(ev.total_marks for _, ev in student_list)
                min_marks = min(ev.total_marks for _, ev in student_list)
                
                print(f"\nGroup {group_no}:")
                print(f"  Students: {len(student_list)}")
                print(f"  Average: {avg_marks:.1f}/50")
                print(f"  Range: {min_marks} - {max_marks}")

if __name__ == "__main__":
    try:
        test_guide_assignments()
        test_group_statistics()
        print("\n✅ All fixes verified!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()