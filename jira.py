import time
import sqlite3
from jira import JIRA
from datetime import datetime

# --- Jira Configuration ---
JIRA_SERVER = "https://your-jira-instance.atlassian.net"
JIRA_USERNAME = "your-jira-email"
JIRA_API_TOKEN = "your-jira-api-token"
JQL_QUERY = "project=qwerty123 AND status='To Do'"

# --- SQLite Database Configuration ---
DB_FILE = "jira_tickets.db"  # SQLite DB file name

# Connect to Jira
def get_jira_connection():
    try:
        options = {"server": JIRA_SERVER}
        jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
        return jira
    except Exception as e:
        print(f"Error connecting to Jira: {e}")
        return None

# Connect to SQLite
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Check if ticket exists in DB
def is_ticket_present(jira_id, cursor):
    query = "SELECT 1 FROM jira_tickets WHERE jira_id = ?"
    cursor.execute(query, (jira_id,))
    return cursor.fetchone() is not None

# Insert Jira ticket into DB
def insert_ticket(jira_id, defected_job, triggered_build_name, status, reporting_time, conn):
    cursor = conn.cursor()
    query = """
        INSERT INTO jira_tickets (jira_id, defected_job, triggered_build_name, status, reporting_time)
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(query, (jira_id, defected_job, triggered_build_name, status, reporting_time))
    conn.commit()
    print(f"Inserted: {jira_id} - {defected_job} - {triggered_build_name} - {status}")

# Poll Jira every 15 minutes
def poll_jira():
    jira = get_jira_connection()
    if not jira:
        return

    while True:
        try:
            issues = jira.search_issues(JQL_QUERY)
            conn = get_db_connection()
            if not conn:
                return

            cursor = conn.cursor()

            for issue in issues:
                jira_id = issue.key
                summary = issue.fields.summary
                status = issue.fields.status.name

                # Extract defected job and triggered build name from summary
                defected_job = extract_defected_job(summary)
                triggered_build_name = extract_triggered_build_name(summary)
                
                # Get current timestamp as reporting time
                reporting_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Skip if the ticket is already in DB
                if not is_ticket_present(jira_id, cursor):
                    insert_ticket(jira_id, defected_job, triggered_build_name, status, reporting_time, conn)
                else:
                    print(f"Skipped: {jira_id} - Already in DB")

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error polling Jira: {e}")

        print("Waiting for 15 minutes...")
        time.sleep(900)  # Sleep for 15 minutes

# Dummy function to extract defected job from summary (modify as needed)
def extract_defected_job(summary):
    if "Defected Job:" in summary:
        return summary.split("Defected Job:")[1].split()[0]
    return "Unknown Job"

# Dummy function to extract triggered build name from summary (modify as needed)
def extract_triggered_build_name(summary):
    if "Build Name:" in summary:
        return summary.split("Build Name:")[1].split()[0]
    return "Unknown Build"

if __name__ == "__main__":
    poll_jira()