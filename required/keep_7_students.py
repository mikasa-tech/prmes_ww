import sqlite3
import os

db_path = "app.db"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Delete evaluations for student IDs greater than 7
        cursor.execute("DELETE FROM evaluation WHERE student_id > 7")
        eval_count = cursor.rowcount
        
        # Delete students with IDs greater than 7
        cursor.execute("DELETE FROM student WHERE id > 7")
        student_count = cursor.rowcount
        
        conn.commit()
        print(f"Successfully deleted {student_count} extra student records.")
        print(f"Successfully deleted {eval_count} associated evaluation records.")
        
        # Final count check
        cursor.execute("SELECT id, name, seat_no FROM student")
        remaining = cursor.fetchall()
        print(f"\nRemaining Students ({len(remaining)}):")
        for r in remaining:
            print(r)
        
    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        conn.close()
