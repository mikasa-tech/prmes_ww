
import pymysql
import os
from dotenv import load_dotenv

def create_simplified_view():
    env_path = os.path.join(os.getcwd(), 'required', '.env')
    load_dotenv(env_path)
    
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASS', ''),
        port=int(os.getenv('DB_PORT', 3306)),
        database=os.getenv('DB_NAME', 'prmes_db')
    )
    cursor = conn.cursor()
    
    print("Creating 'readable_marks' view...")
    
    # Drop if exists to ensure clean state
    cursor.execute("DROP VIEW IF EXISTS readable_marks")
    
    # Create View
    # Combines Student Name with Phase, Review, and Total Marks
    sql = """
    CREATE VIEW readable_marks AS
    SELECT 
        s.name AS Student_Name,
        s.seat_no AS Seat_Number,
        e.phase AS Phase,
        e.review_no AS Review,
        e.total_marks AS Total_Marks,
        e.criteria1 AS Criteria_1,
        e.criteria2 AS Criteria_2,
        e.criteria3 AS Criteria_3,
        e.criteria4 AS Criteria_4
    FROM evaluation e
    JOIN student s ON e.student_id = s.id
    ORDER BY s.name, e.phase, e.review_no;
    """
    
    cursor.execute(sql)
    conn.commit()
    print("View 'readable_marks' created successfully.")
    
    # Verify by printing first few rows
    print("\n--- Preview of Simplified View ---")
    cursor.execute("SELECT * FROM readable_marks LIMIT 5")
    columns = [desc[0] for desc in cursor.description]
    print(f"{columns}")
    for row in cursor.fetchall():
        print(row)
        
    conn.close()

if __name__ == "__main__":
    create_simplified_view()
