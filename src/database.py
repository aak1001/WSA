import sqlite3
import json
import datetime
from typing import Dict, Any, List

DB_PATH = "data/monitoring.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database and creates the necessary tables if they don't exist.
    A simple key-value store for the latest status of each device.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Table to store the last known state for each device
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_status (
            host TEXT PRIMARY KEY,
            last_seen TEXT NOT NULL,
            is_reachable BOOLEAN NOT NULL,
            metrics TEXT
        );
    """)
    conn.commit()
    conn.close()
    print("Database initialized.")

def update_device_status(host: str, data: Dict[str, Any]):
    """
    Inserts or updates the status of a device in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    last_seen = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # A device is considered reachable if there's no 'snmp_error' key.
    # This is a simple assumption for now.
    is_reachable = 'snmp_error' not in data
    metrics_json = json.dumps(data)

    cursor.execute("""
        INSERT INTO device_status (host, last_seen, is_reachable, metrics)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(host) DO UPDATE SET
            last_seen = excluded.last_seen,
            is_reachable = excluded.is_reachable,
            metrics = excluded.metrics;
    """, (host, last_seen, is_reachable, metrics_json))

    conn.commit()
    conn.close()

def get_all_device_statuses() -> List[Dict[str, Any]]:
    """
    Retrieves the latest status for all devices from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT host, last_seen, is_reachable, metrics FROM device_status;")
    rows = cursor.fetchall()
    conn.close()

    statuses = []
    for row in rows:
        status = dict(row)
        status['metrics'] = json.loads(status['metrics'])
        statuses.append(status)

    return statuses

# Initialize the database when the module is first imported.
init_db()
