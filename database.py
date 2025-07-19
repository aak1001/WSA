import sqlite3
import datetime

DB_FILE = "lan_monitor.db"

def create_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            event_type TEXT,
            ip_address TEXT,
            mac_address TEXT,
            details TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_event(event_type, ip_address="", mac_address="", details=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO events (timestamp, event_type, ip_address, mac_address, details) VALUES (?, ?, ?, ?, ?)",
              (datetime.datetime.now(), event_type, ip_address, mac_address, details))
    conn.commit()
    conn.close()
