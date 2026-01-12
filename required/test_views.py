"""
Test script to verify all views are working correctly
"""

from app import create_app
from models import db, Student, Evaluation

def test_all_views():
    app = create_app()
    client = app.test_client()
    
    print("Testing all views...\n")
    
    # Test cases: (url, description)
    test_cases = [
        ("/students?phase=1&review=1", "Phase 1 Review 1 - Students List"),
        ("/students?phase=1&review=2", "Phase 1 Review 2 - Students List"),
        ("/students?phase=2&review=1", "Phase 2 Review 1 - Students List"),
        ("/students?phase=2&review=2", "Phase 2 Review 2 - Students List"),
        ("/students/groupwise?phase=1&review=1", "Phase 1 Review 1 - Groupwise"),
        ("/students/groupwise?phase=1&review=2", "Phase 1 Review 2 - Groupwise"),
        ("/students/groupwise?phase=2&review=1", "Phase 2 Review 1 - Groupwise"),
        ("/students/groupwise?phase=2&review=2", "Phase 2 Review 2 - Groupwise"),
        ("/students/guidewise?phase=1&review=1", "Phase 1 Review 1 - Guidewise"),
        ("/students/guidewise?phase=1&review=2", "Phase 1 Review 2 - Guidewise"),
        ("/students/guidewise?phase=2&review=1", "Phase 2 Review 1 - Guidewise"),
        ("/students/guidewise?phase=2&review=2", "Phase 2 Review 2 - Guidewise"),
    ]
    
    all_passed = True
    for url, description in test_cases:
        response = client.get(url)
        status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL (Status: {response.status_code})"
        print(f"{status} - {description}")
        if response.status_code != 200:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All views are working correctly!")
    else:
        print("❌ Some views failed. Check the errors above.")
    print("="*60)
    
    # Print data summary
    with app.app_context():
        students = Student.query.all()
        evaluations = Evaluation.query.all()
        print(f"\nData Summary:")
        print(f"  Total Students: {len(students)}")
        print(f"  Total Evaluations: {len(evaluations)}")
        
        from collections import Counter
        combos = Counter([(e.phase, e.review_no) for e in evaluations])
        print(f"  Evaluations by Phase-Review:")
        for (p, r), count in sorted(combos.items()):
            print(f"    Phase {p} Review {r}: {count} records")

if __name__ == "__main__":
    test_all_views()
