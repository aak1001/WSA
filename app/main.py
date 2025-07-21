import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QTabWidget, QLabel, QPushButton, QLineEdit, QMenu, QDialog, QFormLayout, QDialogButtonBox
from PyQt5.QtCore import Qt
from network_scanner import NetworkScanner
from database import Database
from connection import Connection
from printer_manager import PrinterManager
from cisco_manager import CiscoManager

class CredentialsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Credentials")

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        form_layout = QFormLayout()
        form_layout.addRow("Username:", self.username)
        form_layout.addRow("Password:", self.password)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Portable LAN Management Tool")
        self.setGeometry(100, 100, 1200, 800)

        self.scanner = NetworkScanner()
        self.db = Database()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)

        # Sidebar
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar.setFixedWidth(200)

        sidebar_layout.addWidget(QLabel("🏠 Dashboard"))
        sidebar_layout.addWidget(QLabel("🖥️ Devices"))
        sidebar_layout.addWidget(QLabel("☎️ PBX Systems"))
        sidebar_layout.addWidget(QLabel("📡 DMR Radios"))
        sidebar_layout.addWidget(QLabel("🖨️ Printers"))
        sidebar_layout.addWidget(QLabel("📊 Logs & History"))
        sidebar_layout.addWidget(QLabel("⚙️ Settings"))

        main_layout.addWidget(sidebar)

        # Main Content Area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_devices_tab(), "Devices")
        self.tabs.addTab(self.create_pbx_tab(), "PBX Systems")
        self.tabs.addTab(QWidget(), "DMR Radios")
        self.tabs.addTab(self.create_printers_tab(), "Printers")
        self.tabs.addTab(self.create_logs_tab(), "Logs & History")

        content_layout.addWidget(self.tabs)
        main_layout.addWidget(content_area)

        self.load_devices()
        self.load_logs()

    def create_devices_tab(self):
        devices_tab = QWidget()
        layout = QVBoxLayout(devices_tab)

        top_layout = QHBoxLayout()
        self.network_input = QLineEdit("192.168.1.1/24")
        scan_button = QPushButton("Scan")
        scan_button.clicked.connect(self.scan_devices)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.filter_devices)
        top_layout.addWidget(self.network_input)
        top_layout.addWidget(scan_button)
        top_layout.addWidget(self.search_input)
        layout.addLayout(top_layout)

        self.device_table = QTableWidget()
        self.device_table.setColumnCount(7)
        self.device_table.setHorizontalHeaderLabels(["IP", "MAC", "Hostname", "OS", "Custom Name", "Notes", "Tags"])
        self.device_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.device_table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.device_table)

        return devices_tab

    def scan_devices(self):
        network = self.network_input.text()
        devices = self.scanner.discover_devices(network)
        for device in devices:
            details = self.scanner.get_device_details(device['ip'])
            device.update(details)
            self.db.add_or_update_device(device)

        self.load_devices()

    def load_devices(self):
        self.device_table.setRowCount(0)
        devices = self.db.get_all_devices()
        for i, device in enumerate(devices):
            self.device_table.insertRow(i)
            self.device_table.setItem(i, 0, QTableWidgetItem(device[0]))
            self.device_table.setItem(i, 1, QTableWidgetItem(device[1]))
            self.device_table.setItem(i, 2, QTableWidgetItem(device[2]))
            self.device_table.setItem(i, 3, QTableWidgetItem(device[3]))
            self.device_table.setItem(i, 4, QTableWidgetItem(device[4]))
            self.device_table.setItem(i, 5, QTableWidgetItem(device[5]))
            self.device_table.setItem(i, 6, QTableWidgetItem(device[6]))

    def show_context_menu(self, pos):
        row = self.device_table.rowAt(pos.y())
        if row < 0:
            return

        ip_address = self.device_table.item(row, 0).text()

        menu = QMenu()

        http_action = menu.addAction("HTTP / HTTPS")
        http_action.triggered.connect(lambda: self.open_web(ip_address))

        ssh_action = menu.addAction("Telnet / SSH")
        ssh_action.triggered.connect(lambda: self.connect_ssh(ip_address))

        rdp_action = menu.addAction("RDP / WinRM")
        rdp_action.triggered.connect(lambda: self.connect_rdp(ip_address))

        menu.addAction("SNMP / SIP / RTP")
        menu.exec_(self.device_table.mapToGlobal(pos))

    def open_web(self, ip_address):
        import webbrowser
        webbrowser.open(f"http://{ip_address}")

    def connect_ssh(self, ip_address):
        dialog = CredentialsDialog(self)
        if dialog.exec_():
            username = dialog.username.text()
            password = dialog.password.text()
            conn = Connection(ip_address, username, password)
            # In a real app, you'd open a terminal window here.
            # For now, we just print the client object.
            print(conn.ssh_connect())

    def connect_rdp(self, ip_address):
        conn = Connection(ip_address, "", "")
        conn.rdp_connect()

    def create_printers_tab(self):
        printers_tab = QWidget()
        layout = QVBoxLayout(printers_tab)

        add_layout = QHBoxLayout()
        self.printer_ip_input = QLineEdit("Printer IP")
        add_button = QPushButton("Add Printer")
        add_button.clicked.connect(self.add_printer)
        add_layout.addWidget(self.printer_ip_input)
        add_layout.addWidget(add_button)
        layout.addLayout(add_layout)

        self.printer_table = QTableWidget()
        self.printer_table.setColumnCount(5)
        self.printer_table.setHorizontalHeaderLabels(["IP", "Model", "Page Count", "Toner Level", "Status"])
        layout.addWidget(self.printer_table)

        return printers_tab

    def add_printer(self):
        ip_address = self.printer_ip_input.text()
        printer_manager = PrinterManager(ip_address)
        details = printer_manager.get_printer_details()

        row_position = self.printer_table.rowCount()
        self.printer_table.insertRow(row_position)
        self.printer_table.setItem(row_position, 0, QTableWidgetItem(ip_address))
        self.printer_table.setItem(row_position, 1, QTableWidgetItem(details.get('model', 'N/A')))
        self.printer_table.setItem(row_position, 2, QTableWidgetItem(details.get('page_count', 'N/A')))
        self.printer_table.setItem(row_position, 3, QTableWidgetItem(details.get('toner_level', 'N/A')))
        self.printer_table.setItem(row_position, 4, QTableWidgetItem(details.get('status', 'N/A')))

    def create_pbx_tab(self):
        pbx_tab = QWidget()
        layout = QVBoxLayout(pbx_tab)

        add_layout = QHBoxLayout()
        self.pbx_ip_input = QLineEdit("PBX IP")
        add_button = QPushButton("Add PBX")
        add_button.clicked.connect(self.add_pbx)
        add_layout.addWidget(self.pbx_ip_input)
        add_layout.addWidget(add_button)
        layout.addLayout(add_layout)

        self.pbx_table = QTableWidget()
        self.pbx_table.setColumnCount(4)
        self.pbx_table.setHorizontalHeaderLabels(["IP", "System Name", "Description", "Uptime"])
        layout.addWidget(self.pbx_table)

        return pbx_tab

    def add_pbx(self):
        ip_address = self.pbx_ip_input.text()
        cisco_manager = CiscoManager(ip_address)
        info = cisco_manager.get_device_info()

        row_position = self.pbx_table.rowCount()
        self.pbx_table.insertRow(row_position)
        self.pbx_table.setItem(row_position, 0, QTableWidgetItem(ip_address))
        self.pbx_table.setItem(row_position, 1, QTableWidgetItem(info.get('sysName', 'N/A')))
        self.pbx_table.setItem(row_position, 2, QTableWidgetItem(info.get('sysDescr', 'N/A')))
        self.pbx_table.setItem(row_position, 3, QTableWidgetItem(info.get('sysUpTime', 'N/A')))
        self.db.log_event("PBX", f"Added PBX {ip_address}")
        self.load_logs()

    def create_logs_tab(self):
        logs_tab = QWidget()
        layout = QVBoxLayout(logs_tab)

        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(3)
        self.logs_table.setHorizontalHeaderLabels(["Timestamp", "Event Type", "Message"])
        layout.addWidget(self.logs_table)

        return logs_tab

    def load_logs(self):
        self.logs_table.setRowCount(0)
        logs = self.db.get_logs()
        for i, log in enumerate(logs):
            self.logs_table.insertRow(i)
            self.logs_table.setItem(i, 0, QTableWidgetItem(log[0]))
            self.logs_table.setItem(i, 1, QTableWidgetItem(log[1]))
            self.logs_table.setItem(i, 2, QTableWidgetItem(log[2]))

    def scan_devices(self):
        network = self.network_input.text()
        devices = self.scanner.discover_devices(network)
        for device in devices:
            details = self.scanner.get_device_details(device['ip'])
            device.update(details)
            self.db.add_or_update_device(device)

        self.load_devices()
        self.db.log_event("Scan", f"Scanned network {network}")
        self.load_logs()

    def filter_devices(self, text):
        for i in range(self.device_table.rowCount()):
            match = False
            for j in range(self.device_table.columnCount()):
                item = self.device_table.item(i, j)
                if item is not None and text.lower() in item.text().lower():
                    match = True
                    break
            self.device_table.setRowHidden(i, not match)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
