
import sys
import os
from sqlalchemy import text

# Add 'required' to path
sys.path.append(os.path.join(os.getcwd(), 'required'))
from app import create_app
from models import db

def describe_database():
    app = create_app()
    with app.app_context():
        print("\n=== DATABASE STRUCTURE (app.db) ===\n")
        print("This file acts like a container for multiple 'Simulated Excel Sheets' called Tables.")
        
        # Get list of tables
        inspector = db.inspect(db.engine)
        table_names = inspector.get_table_names()
        
        for table in table_names:
            print(f"\nTABLE: {table.upper()}")
            print("-" * 50)
            
            # Get columns
            columns = inspector.get_columns(table)
            print(f"Columns: {', '.join([col['name'] for col in columns])}")
            
            # Get row count
            count = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"Total Rows: {count}")
            
            # Show sample data
            if count > 0:
                print("\n  Sample Data (First 3 rows):")
                # Use raw SQL to just grab data without object overhead for visualization
                rows = db.session.execute(text(f"SELECT * FROM {table} LIMIT 3")).fetchall()
                for row in rows:
                    print(f"  - {row}")
            else:
                print("  (Table is empty)")
            print("-" * 50)

if __name__ == "__main__":
    describe_database()
