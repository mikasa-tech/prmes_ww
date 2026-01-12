
import time
import sys
import os
import random
from datetime import datetime

# Add parent directory (required) to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, Student, Evaluation

def run_benchmark():
    app = create_app()
    
    with app.app_context():
        print("--- Starting Benchmark: 200 Students ---")
        
        # 1. Setup Phase: Clear existing data to ensure clean slate
        PHASE = 2
        REVIEW = 2
        
        print(f"Cleaning data for Phase {PHASE} Review {REVIEW}...")
        Evaluation.query.filter_by(phase=PHASE, review_no=REVIEW).delete()
        db.session.commit()
        
        # 2. Data Generation (In-memory)
        print("Generating 200 dummy student records...")
        dummy_data = []
        for i in range(1, 201):
            dummy_data.append({
                "name": f"Student_{i}",
                "seat_no": f"USN_{i:03d}",
                "group_no": f"G_{i // 4 + 1}", # Groups of 4
                "project_title": f"Project {i // 4 + 1}",
                "project_guide": f"Guide_{i // 20 + 1}", # 1 guide per 20 students
                # Marks
                "m1": random.randint(30, 50),
                "m2": random.randint(30, 50),
                "guide": random.randint(30, 50)
            })
            
        # 3. Simulate Import Process (Write Performance)
        print("Benchmarking Write Performance (Insert/Update)...")
        start_time = time.time()
        
        for row in dummy_data:
            seat_no = row['seat_no']
            student = Student.query.filter_by(seat_no=seat_no).one_or_none()
            if not student:
                student = Student(
                    name=row['name'], 
                    seat_no=row['seat_no'], 
                    group_no=row['group_no'], 
                    project_title=row['project_title'], 
                    project_guide=row['project_guide']
                )
                db.session.add(student)
            
            # Simulate marks calculation (simplified for bench)
            # Just distributing total into criteria roughly
            total = int((row['m1'] + row['m2'] + row['guide']) / 3)
            
            ev = Evaluation(
                phase=PHASE,
                review_no=REVIEW,
                total_marks=total,
                criteria1=total//2, criteria2=total//4, criteria3=total//8, criteria4=total-((total//2)+(total//4)+(total//8)),
                member1_criteria1=row['m1'], member1_criteria2=0, member1_criteria3=0, member1_criteria4=0,
                member2_criteria1=row['m2'], member2_criteria2=0, member2_criteria3=0, member2_criteria4=0,
                guide_criteria1=row['guide'], guide_criteria2=0, guide_criteria3=0, guide_criteria4=0,
                student=student
            )
            db.session.add(ev)
            
        db.session.commit()
        end_time = time.time()
        write_duration = end_time - start_time
        print(f"Write Complete. Time taken: {write_duration:.4f} seconds for 200 records.")
        print(f"Rate: {200/write_duration:.2f} students/second")
        
        # 4. Simulate Read Performance (List View)
        print("\nBenchmarking Read Performance (N+1 Query Pattern)...")
        start_time = time.time()
        
        students = Student.query.order_by(Student.group_no, Student.name).all()
        count = 0
        for s in students:
            ev = Evaluation.query.filter_by(student=s, phase=PHASE, review_no=REVIEW).first()
            if ev:
                count += 1
                
        end_time = time.time()
        read_duration = end_time - start_time
        print(f"Read Complete. Time taken: {read_duration:.4f} seconds.")
        
        # 5. Clean up
        print("\nCleaning up test data...")
        Evaluation.query.filter_by(phase=PHASE, review_no=REVIEW).delete()
        db.session.commit()
        
        # 6. Conclusion
        print("\n--- Benchmark Results ---")
        if write_duration < 2.0 and read_duration < 1.0:
            print("Status: EXCELLENT. System handles 200 students with sub-second latency.")
        elif write_duration < 5.0:
            print("Status: GOOD. Performance is acceptable.")
        else:
            print("Status: WARNING. Performance might be sluggish.")

if __name__ == "__main__":
    run_benchmark()
