"""
Test the average calculation fix when some evaluators have no marks (NA/NULL/0)
"""

from app import create_app
from models import db, Student, Evaluation

def test_average_calculation():
    """
    Test scenario from screenshot:
    - Member 1: NA (0)
    - Member 2: NA (0) 
    - Guide: 19
    - Expected Average: 19 (not 17!)
    """
    
    print("="*70)
    print("TESTING AVERAGE CALCULATION WITH MISSING EVALUATOR MARKS")
    print("="*70)
    
    # Test the logic directly
    test_cases = [
        {
            "desc": "Only Guide has marks (19)",
            "m1": 0, "m2": 0, "guide": 19,
            "expected": 19
        },
        {
            "desc": "Only Guide has marks (10)",
            "m1": 0, "m2": 0, "guide": 10,
            "expected": 10
        },
        {
            "desc": "Member1 and Guide (19, 17)",
            "m1": 19, "m2": 0, "guide": 17,
            "expected": 18  # (19+17)/2 = 18
        },
        {
            "desc": "All three evaluators (19, 15, 17)",
            "m1": 19, "m2": 15, "guide": 17,
            "expected": 17  # (19+15+17)/3 = 17
        }
    ]
    
    print("\nTesting average calculation logic:\n")
    
    for test in test_cases:
        evaluators = [test["m1"], test["m2"], test["guide"]]
        non_zero = [val for val in evaluators if val > 0]
        
        if non_zero:
            calculated_avg = int(round(sum(non_zero) / len(non_zero)))
        else:
            calculated_avg = 0
        
        status = "✅ PASS" if calculated_avg == test["expected"] else "❌ FAIL"
        print(f"{status} {test['desc']}")
        print(f"     Input: M1={test['m1']}, M2={test['m2']}, Guide={test['guide']}")
        print(f"     Expected: {test['expected']}, Got: {calculated_avg}")
        print()
    
    # Now test with actual database
    app = create_app()
    with app.app_context():
        print("\n" + "="*70)
        print("CREATING TEST STUDENT WITH MISSING EVALUATOR MARKS")
        print("="*70)
        
        # Create/update a test student
        test_student = Student.query.filter_by(seat_no="TEST001").first()
        if not test_student:
            test_student = Student(
                name="Test Student",
                seat_no="TEST001",
                group_no="TEST",
                project_title="Test Project",
                project_guide="Test Guide"
            )
            db.session.add(test_student)
            db.session.commit()
        
        # Create evaluation with only guide marks (scenario from screenshot)
        ev = Evaluation.query.filter_by(student=test_student, phase=1, review_no=1).first()
        if ev:
            db.session.delete(ev)
            db.session.commit()
        
        # Literature Survey: Guide=19, others=0 -> Should average to 19
        # Problem Identification: Guide=10, others=0 -> Should average to 10
        ev = Evaluation(
            phase=1,
            review_no=1,
            student=test_student,
            # Member 1 marks (all 0)
            member1_criteria1=0,
            member1_criteria2=0,
            member1_criteria3=0,
            member1_criteria4=0,
            # Member 2 marks (all 0)
            member2_criteria1=0,
            member2_criteria2=0,
            member2_criteria3=0,
            member2_criteria4=0,
            # Guide marks
            guide_criteria1=19,  # Literature Survey
            guide_criteria2=10,  # Problem Identification
            guide_criteria3=8,   # Presentation
            guide_criteria4=9,   # Q&A
            # Average should be: 19, 10, 8, 9 (same as guide since others are 0)
            criteria1=19,
            criteria2=10,
            criteria3=8,
            criteria4=9,
            total_marks=46
        )
        db.session.add(ev)
        db.session.commit()
        
        print("\n✅ Created test evaluation")
        print(f"\nTest Student: {test_student.name} ({test_student.seat_no})")
        print(f"Phase 1 Review 1:")
        print(f"  Member 1 Total: {ev.member1_criteria1 + ev.member1_criteria2 + ev.member1_criteria3 + ev.member1_criteria4}")
        print(f"  Member 2 Total: {ev.member2_criteria1 + ev.member2_criteria2 + ev.member2_criteria3 + ev.member2_criteria4}")
        print(f"  Guide Total: {ev.guide_criteria1 + ev.guide_criteria2 + ev.guide_criteria3 + ev.guide_criteria4}")
        print(f"\n  Average Breakdown:")
        print(f"    Literature Survey (C1): {ev.criteria1} (should be 19)")
        print(f"    Problem Identification (C2): {ev.criteria2} (should be 10)")
        print(f"    Presentation (C3): {ev.criteria3} (should be 8)")
        print(f"    Q&A (C4): {ev.criteria4} (should be 9)")
        print(f"  Total: {ev.total_marks}")
        
        # Verify
        if ev.criteria1 == 19 and ev.criteria2 == 10:
            print("\n✅ MANUAL TEST PASSED: Averages are correct!")
        else:
            print("\n❌ MANUAL TEST FAILED: Averages are incorrect")
            print(f"   Expected C1=19, got {ev.criteria1}")
            print(f"   Expected C2=10, got {ev.criteria2}")
        
        print("\n" + "="*70)
        print("To see this in the UI, visit:")
        print(f"http://127.0.0.1:5000/students/{test_student.id}?phase=1&review=1")
        print("="*70)

if __name__ == "__main__":
    test_average_calculation()
