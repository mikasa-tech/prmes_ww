import sqlite3
import os

db_path = "app.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Delete evaluations associated with the target students first
        # to ensure referential integrity even if foreign keys aren't enforced.
        cursor.execute("DELETE FROM evaluation WHERE student_id BETWEEN 8 AND 208")
        eval_count = cursor.rowcount
        
        # Delete the students
        cursor.execute("DELETE FROM student WHERE id BETWEEN 8 AND 208")
        student_count = cursor.rowcount
        
        conn.commit()
        print(f"Successfully deleted {student_count} student records (IDs 8-208).")
        print(f"Successfully deleted {eval_count} associated evaluation records.")
        
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        conn.close()
