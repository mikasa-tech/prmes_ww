#!/usr/bin/env python3
"""
Database Migration Script
Adds 'phase' column to evaluation table for existing databases
"""

import os
from sqlalchemy import create_engine, text
from pathlib import Path

APP_DIR = Path(__file__).parent.resolve()
DB_PATH = APP_DIR / "app.db"

def migrate_database():
    """Add phase column to evaluation table if it doesn't exist"""
    
    if not DB_PATH.exists():
        print("✅ No existing database found. Will be created fresh with new schema.")
        return
    
    print("🔄 Migrating existing database...")
    
    # Connect to SQLite database
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    with engine.connect() as conn:
        # Check if phase column already exists
        result = conn.execute(text("PRAGMA table_info(evaluation)"))
        columns = [row[1] for row in result]
        
        if 'phase' in columns:
            print("✅ Database already migrated - 'phase' column exists!")
            return
        
        print("📝 Recreating evaluation table with new schema...")
        
        try:
            # SQLite doesn't support dropping constraints easily
            # We need to recreate the table
            
            # Step 1: Create new table with correct schema
            conn.execute(text("""
                CREATE TABLE evaluation_new (
                    id INTEGER PRIMARY KEY,
                    phase INTEGER DEFAULT 1 NOT NULL,
                    review_no INTEGER DEFAULT 1 NOT NULL,
                    total_marks INTEGER NOT NULL,
                    literature_survey INTEGER NOT NULL,
                    problem_identification INTEGER NOT NULL,
                    presentation INTEGER NOT NULL,
                    question_answer INTEGER NOT NULL,
                    member1_literature INTEGER,
                    member1_problem INTEGER,
                    member1_presentation INTEGER,
                    member1_qa INTEGER,
                    member2_literature INTEGER,
                    member2_problem INTEGER,
                    member2_presentation INTEGER,
                    member2_qa INTEGER,
                    guide_literature INTEGER,
                    guide_problem INTEGER,
                    guide_presentation INTEGER,
                    guide_qa INTEGER,
                    student_id INTEGER NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES student(id),
                    UNIQUE (student_id, phase, review_no)
                )
            """))
            
            # Step 2: Copy data from old table (set phase=1 for all existing records)
            conn.execute(text("""
                INSERT INTO evaluation_new 
                SELECT id, 1 as phase, review_no, total_marks, literature_survey, 
                       problem_identification, presentation, question_answer,
                       member1_literature, member1_problem, member1_presentation, member1_qa,
                       member2_literature, member2_problem, member2_presentation, member2_qa,
                       guide_literature, guide_problem, guide_presentation, guide_qa,
                       student_id
                FROM evaluation
            """))
            
            # Step 3: Drop old table
            conn.execute(text("DROP TABLE evaluation"))
            
            # Step 4: Rename new table to original name
            conn.execute(text("ALTER TABLE evaluation_new RENAME TO evaluation"))
            
            conn.commit()
            
            print("✅ Migration successful!")
            print("   - Added 'phase' column (default: 1)")
            print("   - Updated unique constraint to include phase")
            print("   - All existing evaluations set to Phase 1")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("=" * 50)
    print("Database Migration Tool")
    print("=" * 50)
    print()
    
    migrate_database()
    
    print()
    print("=" * 50)
    print("Migration complete! You can now run the app.")
    print("=" * 50)
