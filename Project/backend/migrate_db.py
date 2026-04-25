import sqlite3
import os

DB_FILE = "sql_app.db"

def migrate():
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} not found. Nothing to migrate.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Add 'status' column
        try:
            cursor.execute("ALTER TABLE email_scans ADD COLUMN status TEXT DEFAULT 'Open'")
            print("Added 'status' column.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("'status' column already exists.")
            else:
                raise e

        # Add 'closure_notes' column
        try:
            cursor.execute("ALTER TABLE email_scans ADD COLUMN closure_notes TEXT")
            print("Added 'closure_notes' column.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("'closure_notes' column already exists.")
            else:
                raise e

        # Mark existing unsafe emails as "Open", safe as "Closed"?
        # For now, everything defaults to Open via the column default.
        # But we might want to auto-close "clean" ones?
        # User wants "Alerts" for "new Emails which are found as malicious".
        # So "safe" emails shouldn't be alerts.
        # Let's update status based on verdict.
        cursor.execute("UPDATE email_scans SET status = 'Closed' WHERE overall_verdict = 'safe'")
        print("Auto-closed safe emails.")

        conn.commit()
        print("Migration complete.")
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
