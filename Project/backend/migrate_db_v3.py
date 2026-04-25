
import sqlite3

def migrate():
    conn = sqlite3.connect('sql_app.db')
    cur = conn.cursor()

    # Check if column exists
    cur.execute("PRAGMA table_info(email_scans)")
    columns = [row[1] for row in cur.fetchall()]
    
    if 'auth_results' not in columns:
        print("Adding 'auth_results' column to email_scans table...")
        # JSON type in SQLite is just TEXT/VARCHAR, but we'll use JSON for clarity in intent
        cur.execute("ALTER TABLE email_scans ADD COLUMN auth_results JSON")
        conn.commit()
        print("Column added successfully.")
    else:
        print("'auth_results' column already exists.")
        
    conn.close()

if __name__ == "__main__":
    migrate()
