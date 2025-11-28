"""
Populate sample evaluation data for all phase/review combinations
This script creates sample data so you can test all views (groupwise, guidewise, etc.)
"""

from app import create_app
from models import db, Student, Evaluation
import random

def populate_sample_data():
    app = create_app()
    with app.app_context():
        # Get existing students from Phase 1 Review 1
        students = Student.query.all()
        
        if not students:
            print("No students found in database. Please upload Phase 1 Review 1 data first.")
            return
        
        print(f"Found {len(students)} students in database")
        
        # Create evaluations for Phase 1 Review 2, Phase 2 Review 1, Phase 2 Review 2
        phase_review_combos = [(1, 2), (2, 1), (2, 2)]
        
        for phase, review in phase_review_combos:
            print(f"\nCreating evaluations for Phase {phase} Review {review}...")
            
            # Delete existing evaluations for this phase/review
            existing = Evaluation.query.filter_by(phase=phase, review_no=review).all()
            for ev in existing:
                db.session.delete(ev)
            db.session.commit()
            
            # Get max marks for this phase/review
            from review_config import get_review_config
            config = get_review_config(phase, review)
            if not config:
                print(f"  No config found for Phase {phase} Review {review}")
                continue
            
            max_marks = [c['max_marks'] for c in config['criteria']]
            
            created = 0
            for student in students:
                # Generate realistic random marks (70-95% of max marks)
                member1_marks = [int(m * random.uniform(0.70, 0.95)) for m in max_marks]
                member2_marks = [int(m * random.uniform(0.70, 0.95)) for m in max_marks]
                guide_marks = [int(m * random.uniform(0.70, 0.95)) for m in max_marks]
                
                # Calculate averages (main criteria values)
                avg_marks = [
                    int(round((member1_marks[i] + member2_marks[i] + guide_marks[i]) / 3))
                    for i in range(4)
                ]
                
                total = sum(avg_marks)
                
                evaluation = Evaluation(
                    phase=phase,
                    review_no=review,
                    total_marks=total,
                    criteria1=avg_marks[0],
                    criteria2=avg_marks[1],
                    criteria3=avg_marks[2],
                    criteria4=avg_marks[3],
                    # Member 1
                    member1_criteria1=member1_marks[0],
                    member1_criteria2=member1_marks[1],
                    member1_criteria3=member1_marks[2],
                    member1_criteria4=member1_marks[3],
                    # Member 2
                    member2_criteria1=member2_marks[0],
                    member2_criteria2=member2_marks[1],
                    member2_criteria3=member2_marks[2],
                    member2_criteria4=member2_marks[3],
                    # Guide
                    guide_criteria1=guide_marks[0],
                    guide_criteria2=guide_marks[1],
                    guide_criteria3=guide_marks[2],
                    guide_criteria4=guide_marks[3],
                    student=student,
                )
                db.session.add(evaluation)
                created += 1
            
            db.session.commit()
            print(f"  Created {created} evaluation records")
        
        print("\n✅ Sample data populated successfully!")
        print("\nYou can now view:")
        print("  - Phase 1 Review 2: http://127.0.0.1:5000/students?phase=1&review=2")
        print("  - Phase 2 Review 1: http://127.0.0.1:5000/students?phase=2&review=1")
        print("  - Phase 2 Review 2: http://127.0.0.1:5000/students?phase=2&review=2")
        print("  - Groupwise view: http://127.0.0.1:5000/students/groupwise?phase=2&review=1")
        print("  - Guidewise view: http://127.0.0.1:5000/students/guidewise?phase=2&review=1")

if __name__ == "__main__":
    populate_sample_data()
