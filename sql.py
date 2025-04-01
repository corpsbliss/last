import sqlite3

# --- SQLite Database Configuration ---
DB_FILE = "jira_tickets.db"  # SQLite DB file name

# Create the DB connection and table
def create_db_schema():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create the 'jira_tickets' table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jira_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jira_id TEXT UNIQUE,
                defected_job TEXT,
                triggered_build_name TEXT,
                status TEXT,
                reporting_time TEXT
            )
            """
        )
        conn.commit()
        conn.close()
        print("Database and table created successfully.")
    except Exception as e:
        print(f"Error creating database schema: {e}")

if __name__ == "__main__":
    create_db_schema()