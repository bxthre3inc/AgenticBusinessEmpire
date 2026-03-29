import sqlite3
import os

db_path = "/home/bxthre3/Desktop/agentos/runtime/agenticbusinessempire.db"

def fix_schema():
    print(f"🛠️ Fixing schema for {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE workforce ADD COLUMN metadata TEXT")
        print("  [+] Added missing 'metadata' column to 'workforce' table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("  [!] Column 'metadata' already exists.")
        else:
            print(f"  [X] Failed to alter table: {e}")
            
    conn.commit()
    conn.close()
    print("✅ Schema fix complete.")

if __name__ == "__main__":
    fix_schema()
