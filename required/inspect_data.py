
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add 'required' to path
sys.path.append(os.path.join(os.getcwd(), 'required'))
from models import Evaluation, Student, db
from app import create_app

def inspect_phase2_data():
    app = create_app()
    with app.app_context():
        print("\n--- Inspecting Phase 1 Review 1 (1, 1) ---")
        evals_p1r1 = Evaluation.query.filter_by(phase=1, review_no=1).all()
        if not evals_p1r1:
            print("No data found for Phase 1 Review 1")
        else:
            for ev in evals_p1r1[:5]: # Show first 5
                print(f"Student: {ev.student.name}, Total: {ev.total_marks}, "
                      f"C1: {ev.criteria1}, C2: {ev.criteria2}, C3: {ev.criteria3}, C4: {ev.criteria4}")
        
        print("\n--- Inspecting Phase 1 Review 2 (1, 2) ---")
        evals_p1r2 = Evaluation.query.filter_by(phase=1, review_no=2).all()
        if not evals_p1r2:
            print("No data found for Phase 1 Review 2")
        else:
            for ev in evals_p1r2[:5]: # Show first 5
                print(f"Student: {ev.student.name}, Total: {ev.total_marks}, "
                      f"C1: {ev.criteria1}, C2: {ev.criteria2}, C3: {ev.criteria3}, C4: {ev.criteria4}")

if __name__ == "__main__":
    inspect_phase2_data()
