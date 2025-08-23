import sqlite3
import json

def read_all_statuses():
    try:
        conn = sqlite3.connect("data/monitoring.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT host, is_reachable, metrics FROM device_status;")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("Database is empty.")
            return

        print("--- Database Content ---")
        for row in rows:
            metrics = json.loads(row['metrics'])
            print(f"Host: {row['host']}, Reachable: {row['is_reachable']}")
            print(f"  Metrics: {json.dumps(metrics, indent=2)}")
        print("------------------------")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except FileNotFoundError:
        print("Database file not found.")

if __name__ == "__main__":
    read_all_statuses()
