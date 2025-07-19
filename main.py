import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QStatusBar, QPushButton, QMenu, QMessageBox, QLineEdit, QHBoxLayout, QProgressBar, QTabWidget, QLabel
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from scanner import get_devices, port_scan
from database import create_database, log_event
from telecom import check_sip_status

class ScanThread(QThread):
    devices_found = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)

    def __init__(self, ip_range):
        super().__init__()
        self.ip_range = ip_range
        self.is_running = True

    def run(self):
        try:
            # This is a simplified progress calculation. A more accurate calculation would require knowing the number of hosts in the IP range.
            for i in range(100):
                if not self.is_running:
                    break
                time.sleep(0.05)
                self.progress_updated.emit(i + 1)

            if self.is_running:
                devices = get_devices(self.ip_range)
                self.devices_found.emit(devices)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.is_running = False

class PortScanThread(QThread):
    ports_found = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, ip, ports):
        super().__init__()
        self.ip = ip
        self.ports = ports

    def run(self):
        try:
            open_ports = port_scan(self.ip, self.ports)
            self.ports_found.emit(open_ports)
        except Exception as e:
            self.error_occurred.emit(str(e))

class SipCheckThread(QThread):
    status_found = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port

    def run(self):
        try:
            status = check_sip_status(self.ip, self.port)
            self.status_found.emit(status)
        except Exception as e:
            self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LAN Monitor")
        self.setGeometry(100, 100, 800, 600)

        create_database()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Network Tab
        self.network_tab = QWidget()
        self.tabs.addTab(self.network_tab, "Network")
        self.network_layout = QVBoxLayout()
        self.network_tab.setLayout(self.network_layout)

        self.scan_layout = QHBoxLayout()
        self.ip_range_input = QLineEdit("192.168.1.1/24")
        self.scan_layout.addWidget(self.ip_range_input)
        self.scan_button = QPushButton("Scan Network")
        self.scan_button.clicked.connect(self.start_scan)
        self.scan_layout.addWidget(self.scan_button)
        self.stop_scan_button = QPushButton("Stop Scan")
        self.stop_scan_button.clicked.connect(self.stop_scan)
        self.stop_scan_button.setEnabled(False)
        self.scan_layout.addWidget(self.stop_scan_button)
        self.network_layout.addLayout(self.scan_layout)

        self.progress_bar = QProgressBar()
        self.network_layout.addWidget(self.progress_bar)

        self.device_table = QTableWidget()
        self.device_table.setColumnCount(6)
        self.device_table.setHorizontalHeaderLabels(["IP Address", "MAC Address", "Hostname", "Vendor", "OS", "Ping"])
        self.device_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.device_table.customContextMenuRequested.connect(self.show_context_menu)
        self.network_layout.addWidget(self.device_table)

        # Telecom Tab
        self.telecom_tab = QWidget()
        self.tabs.addTab(self.telecom_tab, "Telecom")
        self.telecom_layout = QVBoxLayout()
        self.telecom_tab.setLayout(self.telecom_layout)

        self.sip_check_layout = QHBoxLayout()
        self.sip_ip_input = QLineEdit("192.168.1.1")
        self.sip_check_layout.addWidget(self.sip_ip_input)
        self.sip_port_input = QLineEdit("5060")
        self.sip_check_layout.addWidget(self.sip_port_input)
        self.sip_check_button = QPushButton("Check SIP Status")
        self.sip_check_button.clicked.connect(self.start_sip_check)
        self.sip_check_layout.addWidget(self.sip_check_button)
        self.telecom_layout.addLayout(self.sip_check_layout)

        self.sip_status_label = QLabel("SIP Status: Unknown")
        self.telecom_layout.addWidget(self.sip_status_label)


        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def start_scan(self):
        self.status_bar.showMessage("Scanning...")
        self.scan_button.setEnabled(False)
        self.stop_scan_button.setEnabled(True)
        self.progress_bar.setValue(0)
        ip_range = self.ip_range_input.text()
        log_event("Scan started", details=f"IP range: {ip_range}")
        self.scan_thread = ScanThread(ip_range)
        self.scan_thread.devices_found.connect(self.update_table)
        self.scan_thread.error_occurred.connect(self.show_error)
        self.scan_thread.progress_updated.connect(self.update_progress)
        self.scan_thread.finished.connect(self.scan_finished)
        self.scan_thread.start()

    def stop_scan(self):
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.status_bar.showMessage("Scan stopped.")
            log_event("Scan stopped")
            self.scan_button.setEnabled(True)
            self.stop_scan_button.setEnabled(False)

    def scan_finished(self):
        self.scan_button.setEnabled(True)
        self.stop_scan_button.setEnabled(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_table(self, devices):
        self.device_table.setRowCount(len(devices))
        for i, device in enumerate(devices):
            self.device_table.setItem(i, 0, QTableWidgetItem(device["ip"]))
            self.device_table.setItem(i, 1, QTableWidgetItem(device["mac"]))
            self.device_table.setItem(i, 2, QTableWidgetItem(device["hostname"]))
            self.device_table.setItem(i, 3, QTableWidgetItem(device["vendor"]))
            self.device_table.setItem(i, 4, QTableWidgetItem(device["os"]))
            self.device_table.setItem(i, 5, QTableWidgetItem(device["ping"]))
            log_event("Device found", ip_address=device["ip"], mac_address=device["mac"], details=f"Hostname: {device['hostname']}, Vendor: {device['vendor']}, OS: {device['os']}")
        self.status_bar.showMessage(f"Scan complete. Found {len(devices)} devices.")
        log_event("Scan finished", details=f"Found {len(devices)} devices")


    def show_context_menu(self, pos):
        row = self.device_table.rowAt(pos.y())
        if row >= 0:
            menu = QMenu()
            scan_action = menu.addAction("Scan Ports")
            action = menu.exec(self.device_table.mapToGlobal(pos))
            if action == scan_action:
                ip = self.device_table.item(row, 0).text()
                self.start_port_scan(ip)

    def start_port_scan(self, ip):
        self.status_bar.showMessage(f"Scanning ports on {ip}...")
        log_event("Port scan started", ip_address=ip)
        self.port_scan_thread = PortScanThread(ip, range(1, 1025))
        self.port_scan_thread.ports_found.connect(self.show_port_scan_results)
        self.port_scan_thread.error_occurred.connect(self.show_error)
        self.port_scan_thread.start()

    def show_port_scan_results(self, open_ports):
        self.status_bar.showMessage("Port scan complete.")
        log_event("Port scan finished", details=f"Found {len(open_ports)} open ports")
        if open_ports:
            QMessageBox.information(self, "Open Ports", f"Open ports: {', '.join(map(str, open_ports))}")
        else:
            QMessageBox.information(self, "Open Ports", "No open ports found.")

    def start_sip_check(self):
        ip = self.sip_ip_input.text()
        port = int(self.sip_port_input.text())
        self.status_bar.showMessage(f"Checking SIP status on {ip}:{port}...")
        log_event("SIP check started", ip_address=ip, details=f"Port: {port}")
        self.sip_check_thread = SipCheckThread(ip, port)
        self.sip_check_thread.status_found.connect(self.update_sip_status)
        self.sip_check_thread.error_occurred.connect(self.show_error)
        self.sip_check_thread.start()

    def update_sip_status(self, status):
        self.sip_status_label.setText(f"SIP Status: {status}")
        self.status_bar.showMessage("SIP status check complete.")
        log_event("SIP check finished", details=f"Status: {status}")

    def show_error(self, message):
        self.status_bar.showMessage("Error")
        QMessageBox.critical(self, "Error", message)
        log_event("Error", details=message)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
