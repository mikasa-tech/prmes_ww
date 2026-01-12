"""
Add Phase 1 Review 2 evaluations for the 7 students
"""
import sqlite3

db_path = "app.db"

# Sample marks for Phase 1 Review 2 (Objectives:10, Methodology:10, Presentation:10, Q&A:10 = 40 total)
p1r2_data = [
    # student_id, phase, review_no, total, c1, c2, c3, c4, m1c1, m1c2, m1c3, m1c4, m2c1, m2c2, m2c3, m2c4, gc1, gc2, gc3, gc4
    (1, 1, 2, 40, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10),  # Bhavani C
    (2, 1, 2, 38, 9, 10, 10, 9, 9, 10, 10, 9, 9, 10, 10, 9, 9, 10, 10, 9),  # Mahadevi
    (3, 1, 2, 42, 10, 10, 11, 11, 10, 10, 11, 11, 10, 10, 11, 11, 10, 10, 11, 11),  # Aishwarya
    (4, 1, 2, 39, 10, 9, 10, 10, 10, 9, 10, 10, 10, 9, 10, 10, 10, 9, 10, 10),  # Diksha
    (5, 1, 2, 41, 10, 10, 11, 10, 10, 10, 11, 10, 10, 10, 11, 10, 10, 10, 11, 10),  # Ningamma
    (6, 1, 2, 37, 9, 9, 10, 9, 9, 9, 10, 9, 9, 9, 10, 9, 9, 9, 10, 9),  # Kanaka
    (7, 1, 2, 43, 11, 10, 11, 11, 11, 10, 11, 11, 11, 10, 11, 11, 11, 10, 11, 11),  # Akshata
]

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    for data in p1r2_data:
        student_id, phase, review_no, total, c1, c2, c3, c4, m1c1, m1c2, m1c3, m1c4, m2c1, m2c2, m2c3, m2c4, gc1, gc2, gc3, gc4 = data
        
        cursor.execute("""
            INSERT INTO evaluation (
                student_id, phase, review_no, total_marks,
                criteria1, criteria2, criteria3, criteria4,
                member1_criteria1, member1_criteria2, member1_criteria3, member1_criteria4,
                member2_criteria1, member2_criteria2, member2_criteria3, member2_criteria4,
                guide_criteria1, guide_criteria2, guide_criteria3, guide_criteria4
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, phase, review_no, total, c1, c2, c3, c4, m1c1, m1c2, m1c3, m1c4, m2c1, m2c2, m2c3, m2c4, gc1, gc2, gc3, gc4))
    
    conn.commit()
    print("SUCCESS: Added 7 Phase 1 Review 2 evaluations")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM evaluation")
    total = cursor.fetchone()[0]
    print(f"Total evaluations now: {total}")
    
except Exception as e:
    conn.rollback()
    print(f"ERROR: {e}")
finally:
    conn.close()
