import sqlite3

def delete_test_data():
    db_path = "app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find students to delete (Case insensitive 'test' in group_no or name)
    cursor.execute("SELECT id, name, group_no FROM student WHERE group_no LIKE '%test%' OR name LIKE '%test%'")
    students = cursor.fetchall()

    if not students:
        print("No students found matching 'test'.")
        conn.close()
        return

    print(f"Found {len(students)} students to delete:")
    for s in students:
        print(f" - ID: {s[0]}, Name: {s[1]}, Group: {s[2]}")

    # Delete evaluations first (Foreign Key constraint usually requires this, though cascade might handle it)
    student_ids = [s[0] for s in students]
    id_list = ",".join(map(str, student_ids))
    
    cursor.execute(f"DELETE FROM evaluation WHERE student_id IN ({id_list})")
    print(f"Deleted evaluations for student IDs: {id_list}")

    # Delete students
    cursor.execute(f"DELETE FROM student WHERE id IN ({id_list})")
    print(f"Deleted students with IDs: {id_list}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    delete_test_data()
