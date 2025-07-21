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
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_profiles (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            network_range TEXT,
            ports TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS password (
            id INTEGER PRIMARY KEY,
            password_hash TEXT
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

    def add_scan_profile(self, name, network_range, ports):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO scan_profiles (name, network_range, ports) VALUES (?, ?, ?)", (name, network_range, ports))
        self.conn.commit()

    def get_scan_profiles(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, network_range, ports FROM scan_profiles")
        return cursor.fetchall()

    def update_scan_profile(self, old_name, new_name, network_range, ports):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE scan_profiles SET name = ?, network_range = ?, ports = ? WHERE name = ?", (new_name, network_range, ports, old_name))
        self.conn.commit()

import hashlib

    def delete_scan_profile(self, name):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM scan_profiles WHERE name = ?", (name,))
        self.conn.commit()

    def set_password(self, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.cursor()
        # Clear existing password
        cursor.execute("DELETE FROM password")
        cursor.execute("INSERT INTO password (password_hash) VALUES (?)", (password_hash,))
        self.conn.commit()

    def check_password(self, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash FROM password")
        result = cursor.fetchone()
        if result is None:
            return True # No password set
        return result[0] == password_hash
