import sqlite3

class Database:
    def __init__(self, db_name="lan_manager.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY,
            ip_address TEXT UNIQUE,
            mac_address TEXT,
            hostname TEXT,
            os TEXT,
            custom_name TEXT,
            notes TEXT,
            tags TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            message TEXT
        )
        """)
        self.conn.commit()

    def add_or_update_device(self, device_data):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO devices (ip_address, mac_address, hostname, os)
        VALUES (?, ?, ?, ?)
        """, (device_data['ip'], device_data['mac'], device_data.get('hostname'), device_data.get('os')))
        self.conn.commit()

    def get_all_devices(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ip_address, mac_address, hostname, os, custom_name, notes, tags FROM devices")
        return cursor.fetchall()

    def log_event(self, event_type, message):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO logs (event_type, message) VALUES (?, ?)", (event_type, message))
        self.conn.commit()

    def get_logs(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT timestamp, event_type, message FROM logs ORDER BY timestamp DESC")
        return cursor.fetchall()
