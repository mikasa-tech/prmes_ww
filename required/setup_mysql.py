
import pymysql
import os
from dotenv import load_dotenv

def create_db_if_not_exists():
    env_path = os.path.join(os.getcwd(), 'required', '.env')
    load_dotenv(env_path)
    
    host = os.getenv('DB_HOST', 'localhost')
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASS', '')
    port = int(os.getenv('DB_PORT', 3306))
    db_name = os.getenv('DB_NAME', 'prmes_db')
    
    print(f"Connecting to MySQL at {host}:{port} as {user}...")
    
    try:
        conn = pymysql.connect(host=host, user=user, password=password, port=port)
        cursor = conn.cursor()
        
        print(f"Creating database '{db_name}' if it doesn't exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print("Done.")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        # Assuming XAMPP default often has no password for root. 
        # If this fails, user might have a password set.

if __name__ == "__main__":
    create_db_if_not_exists()
