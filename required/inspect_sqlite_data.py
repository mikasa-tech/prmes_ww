import sqlite3
import pandas as pd
import os

db_path = "app.db"

if not os.path.exists(db_path):
    print("app.db not found!")
else:
    conn = sqlite3.connect(db_path)
    
    print("--- TABLE: student (First 5 rows) ---")
    try:
        df_student = pd.read_sql_query("SELECT * FROM student LIMIT 5", conn)
        print(df_student.to_string(index=False))
    except Exception as e:
        print(e)
        
    print("\n--- TABLE: evaluation (First 5 rows) ---")
    try:
        df_eval = pd.read_sql_query("SELECT * FROM evaluation LIMIT 5", conn)
        print(df_eval.to_string(index=False))
    except Exception as e:
        print(e)

    conn.close()
