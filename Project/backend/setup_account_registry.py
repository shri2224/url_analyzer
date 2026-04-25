"""
One-time setup script: creates account_registry table and seeds it.
"""
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('sql_app.db')
cur = conn.cursor()

# 1. Create account_registry table
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='account_registry'")
if not cur.fetchone():
    cur.execute("""
        CREATE TABLE account_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR UNIQUE NOT NULL,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_connected INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    print("account_registry table created")
else:
    print("account_registry table already exists")

# 2. Seed from existing email_scans account column
cur.execute("SELECT DISTINCT account FROM email_scans WHERE account IS NOT NULL AND account != ''")
known_accounts = [row[0] for row in cur.fetchall()]
print(f"Known accounts from scans: {known_accounts}")

for email in known_accounts:
    cur.execute("SELECT id FROM account_registry WHERE email = ?", (email,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO account_registry (email, is_connected, first_seen, last_seen) VALUES (?, 1, ?, ?)",
            (email, datetime.utcnow().isoformat(), datetime.utcnow().isoformat())
        )
        print(f"  Seeded: {email}")
    else:
        # Update connected status
        cur.execute(
            "UPDATE account_registry SET is_connected = 1, last_seen = ? WHERE email = ?",
            (datetime.utcnow().isoformat(), email)
        )
        print(f"  Updated: {email}")

conn.commit()

# 3. Show final state
cur.execute("SELECT * FROM account_registry")
rows = cur.fetchall()
print(f"\nAccount Registry ({len(rows)} accounts):")
for row in rows:
    print(f"  {row}")

conn.close()
print("\nDone.")
