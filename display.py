from flask import Flask, render_template
import sqlite3

# Flask application setup
app = Flask(__name__)

# SQLite DB file
DB_FILE = "jira_tickets.db"

# Fetch data from the database
def fetch_data():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        query = """
        SELECT jira_id, defected_job, triggered_build_name, status, reporting_time
        FROM jira_tickets
        ORDER BY reporting_time DESC
        """
        cursor.execute(query)
        data = cursor.fetchall()

        conn.close()
        return data
    except Exception as e:
        print(f"Error fetching data from DB: {e}")
        return []

# Home route to display Jira data
@app.route("/")
def index():
    jira_data = fetch_data()
    return render_template("index.html", jira_data=jira_data)

# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)