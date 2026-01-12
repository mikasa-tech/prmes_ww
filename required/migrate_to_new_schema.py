"""
Migrate database from old schema to new multi-phase schema
"""
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

DB_PATH = Path("app.db")
BACKUP_PATH = Path(f"app.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

print("=" * 60)
print("DATABASE MIGRATION: Old Schema -> New Multi-Phase Schema")
print("=" * 60)

# Create backup
print(f"\n1. Creating backup: {BACKUP_PATH}")
shutil.copy2(DB_PATH, BACKUP_PATH)
print("   ✓ Backup created")

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check current schema
cursor.execute("PRAGMA table_info(evaluation)")
columns = {row[1]: row[2] for row in cursor.fetchall()}
print(f"\n2. Current schema has {len(columns)} columns")

# Check if already migrated
if 'phase' in columns:
    print("\n✓ Database already migrated!")
    conn.close()
    exit(0)

print("\n3. Starting migration...")

try:
    # Create new table with updated schema
    cursor.execute("""
        CREATE TABLE evaluation_new (
            id INTEGER PRIMARY KEY,
            phase INTEGER DEFAULT 1 NOT NULL,
            review_no INTEGER DEFAULT 1 NOT NULL,
            total_marks INTEGER NOT NULL,
            criteria1 INTEGER NOT NULL,
            criteria2 INTEGER NOT NULL,
            criteria3 INTEGER NOT NULL,
            criteria4 INTEGER NOT NULL,
            member1_criteria1 INTEGER,
            member1_criteria2 INTEGER,
            member1_criteria3 INTEGER,
            member1_criteria4 INTEGER,
            member2_criteria1 INTEGER,
            member2_criteria2 INTEGER,
            member2_criteria3 INTEGER,
            member2_criteria4 INTEGER,
            guide_criteria1 INTEGER,
            guide_criteria2 INTEGER,
            guide_criteria3 INTEGER,
            guide_criteria4 INTEGER,
            student_id INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES student(id),
            UNIQUE (student_id, phase, review_no)
        )
    """)
    print("   ✓ Created new table structure")

    # Migrate data from old table to new
    # Old columns: literature_survey, problem_identification, presentation, question_answer
    # New columns: criteria1, criteria2, criteria3, criteria4
    cursor.execute("""
        INSERT INTO evaluation_new (
            id, phase, review_no, total_marks,
            criteria1, criteria2, criteria3, criteria4,
            member1_criteria1, member1_criteria2, member1_criteria3, member1_criteria4,
            member2_criteria1, member2_criteria2, member2_criteria3, member2_criteria4,
            guide_criteria1, guide_criteria2, guide_criteria3, guide_criteria4,
            student_id
        )
        SELECT 
            id,
            1 as phase,  -- Assume all existing data is Phase 1
            review_no,
            total_marks,
            literature_survey as criteria1,
            problem_identification as criteria2,
            presentation as criteria3,
            question_answer as criteria4,
            member1_literature as member1_criteria1,
            member1_problem as member1_criteria2,
            member1_presentation as member1_criteria3,
            member1_qa as member1_criteria4,
            member2_literature as member2_criteria1,
            member2_problem as member2_criteria2,
            member2_presentation as member2_criteria3,
            member2_qa as member2_criteria4,
            guide_literature as guide_criteria1,
            guide_problem as guide_criteria2,
            guide_presentation as guide_criteria3,
            guide_qa as guide_criteria4,
            student_id
        FROM evaluation
    """)
    
    rows_migrated = cursor.rowcount
    print(f"   ✓ Migrated {rows_migrated} evaluation records")

    # Drop old table and rename new one
    cursor.execute("DROP TABLE evaluation")
    cursor.execute("ALTER TABLE evaluation_new RENAME TO evaluation")
    print("   ✓ Replaced old table with new schema")

    # Commit changes
    conn.commit()
    print("\n✓ Migration completed successfully!")
    print(f"\n  Backup saved at: {BACKUP_PATH}")
    print("  You can delete the backup if everything works fine.")
    
except Exception as e:
    print(f"\n✗ Migration failed: {e}")
    conn.rollback()
    print(f"\n  Restoring from backup...")
    conn.close()
    shutil.copy2(BACKUP_PATH, DB_PATH)
    print("  ✓ Database restored from backup")
    raise

finally:
    conn.close()

print("\n" + "=" * 60)
print("You can now upload Excel files with the new format!")
print("=" * 60)
