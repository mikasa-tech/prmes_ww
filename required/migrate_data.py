
import sqlite3
import os
import sys
from sqlalchemy import create_engine, text

# Add 'required' to path
sys.path.append(os.path.join(os.getcwd(), 'required'))
from app import create_app
from models import db, Student, Evaluation

def migrate_data():
    sqlite_path = os.path.join(os.getcwd(), 'required', 'app.db')
    if not os.path.exists(sqlite_path):
        print(f"SQLite DB not found at {sqlite_path}")
        return

    print("--- Starting Migration: SQLite -> MySQL ---")
    
    # 1. Read from SQLite
    print("Reading from SQLite app.db...")
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    # Read Students
    cursor.execute("SELECT id, group_no, project_title, project_guide, seat_no, name FROM student")
    sqlite_students = cursor.fetchall()
    print(f"Found {len(sqlite_students)} students.")
    
    # Read Evaluations
    cursor.execute("SELECT id, phase, review_no, total_marks, criteria1, criteria2, criteria3, criteria4, member1_criteria1, member1_criteria2, member1_criteria3, member1_criteria4, member2_criteria1, member2_criteria2, member2_criteria3, member2_criteria4, guide_criteria1, guide_criteria2, guide_criteria3, guide_criteria4, student_id FROM evaluation")
    sqlite_evals = cursor.fetchall()
    print(f"Found {len(sqlite_evals)} evaluations.")
    
    conn.close()
    
    # 2. Write to MySQL
    print("\nConnecting to MySQL via App...")
    app = create_app()
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        
        # Clear existing MySQL data to avoid duplicates if re-running
        db.session.execute(text("DELETE FROM evaluation"))
        db.session.execute(text("DELETE FROM student"))
        db.session.commit()
        
        # Insert Students
        # We need to map old IDs to new objects to keep relationships if IDs change (auto-increment)
        # But we can try to force insert IDs or just match by seat_no
        
        # Let's preserve IDs if possible, but auto-increment might fight us.
        # Safest is to map: old_id -> new_student_obj
        
        id_map = {}
        for row in sqlite_students:
            s = Student(
                group_no=row[1],
                project_title=row[2],
                project_guide=row[3],
                seat_no=row[4],
                name=row[5]
            )
            db.session.add(s)
            db.session.flush() # get new ID
            id_map[row[0]] = s.id
        
        print(f"Migrated {len(id_map)} students.")
        
        # Insert Evaluations
        for row in sqlite_evals:
            old_student_id = row[20]
            new_student_id = id_map.get(old_student_id)
            if not new_student_id:
                print(f"Warning: Skipping evaluation for unknown student ID {old_student_id}")
                continue
                
            e = Evaluation(
                phase=row[1],
                review_no=row[2],
                total_marks=row[3],
                criteria1=row[4],
                criteria2=row[5],
                criteria3=row[6],
                criteria4=row[7],
                member1_criteria1=row[8],
                member1_criteria2=row[9],
                member1_criteria3=row[10],
                member1_criteria4=row[11],
                member2_criteria1=row[12],
                member2_criteria2=row[13],
                member2_criteria3=row[14],
                member2_criteria4=row[15],
                guide_criteria1=row[16],
                guide_criteria2=row[17],
                guide_criteria3=row[18],
                guide_criteria4=row[19],
                student_id=new_student_id
            )
            db.session.add(e)
            
        db.session.commit()
        print(f"Migrated evaluations.")
        print("\n--- Migration Complete ---")

if __name__ == "__main__":
    migrate_data()
