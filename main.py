import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QStatusBar, QPushButton, QMenu, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from scanner import get_devices, port_scan
from database import create_database, log_event

class ScanThread(QThread):
    devices_found = pyqtSignal(list)

    def __init__(self, ip_range):
        super().__init__()
        self.ip_range = ip_range

    def run(self):
        devices = get_devices(self.ip_range)
        self.devices_found.emit(devices)

class PortScanThread(QThread):
    ports_found = pyqtSignal(list)

    def __init__(self, ip, ports):
        super().__init__()
        self.ip = ip
        self.ports = ports

    def run(self):
        open_ports = port_scan(self.ip, self.ports)
        self.ports_found.emit(open_ports)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LAN Monitor")
        self.setGeometry(100, 100, 800, 600)

        create_database()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.scan_button = QPushButton("Scan Network")
        self.scan_button.clicked.connect(self.start_scan)
        self.layout.addWidget(self.scan_button)

        self.device_table = QTableWidget()
        self.device_table.setColumnCount(5)
        self.device_table.setHorizontalHeaderLabels(["IP Address", "MAC Address", "Hostname", "Vendor", "Ping"])
        self.device_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.device_table.customContextMenuRequested.connect(self.show_context_menu)
        self.layout.addWidget(self.device_table)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def start_scan(self):
        self.status_bar.showMessage("Scanning...")
        log_event("Scan started")
        self.scan_thread = ScanThread("192.168.1.1/24")
        self.scan_thread.devices_found.connect(self.update_table)
        self.scan_thread.start()

    def update_table(self, devices):
        self.device_table.setRowCount(len(devices))
        for i, device in enumerate(devices):
            self.device_table.setItem(i, 0, QTableWidgetItem(device["ip"]))
            self.device_table.setItem(i, 1, QTableWidgetItem(device["mac"]))
            self.device_table.setItem(i, 2, QTableWidgetItem(device["hostname"]))
            self.device_table.setItem(i, 3, QTableWidgetItem(device["vendor"]))
            self.device_table.setItem(i, 4, QTableWidgetItem(device["ping"]))
            log_event("Device found", ip_address=device["ip"], mac_address=device["mac"], details=f"Hostname: {device['hostname']}, Vendor: {device['vendor']}")
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
        self.port_scan_thread.start()

    def show_port_scan_results(self, open_ports):
        self.status_bar.showMessage("Port scan complete.")
        log_event("Port scan finished", details=f"Found {len(open_ports)} open ports")
        if open_ports:
            QMessageBox.information(self, "Open Ports", f"Open ports: {', '.join(map(str, open_ports))}")
        else:
            QMessageBox.information(self, "Open Ports", "No open ports found.")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
