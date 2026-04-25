from sqlalchemy import create_engine, text
from app.core.config import DATABASE_URL

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(email_scans)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'account' not in columns:
                print("Adding 'account' column to email_scans table...")
                conn.execute(text("ALTER TABLE email_scans ADD COLUMN account VARCHAR"))
                print("Column added successfully.")
            else:
                print("'account' column already exists.")
                
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
