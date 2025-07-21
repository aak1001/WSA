import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QTabWidget, QLabel, QPushButton, QLineEdit, QMenu, QDialog, QFormLayout, QDialogButtonBox, QComboBox
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

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Password")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout = QFormLayout()
        form_layout.addRow("Password:", self.password_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])

        self.set_password_button = QPushButton("Set Password")
        self.set_password_button.clicked.connect(self.set_password)

        form_layout = QFormLayout()
        form_layout.addRow("Theme:", self.theme_combo)
        form_layout.addRow(self.set_password_button)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def set_password(self):
        dialog = PasswordDialog(self)
        if dialog.exec_():
            password = dialog.password_input.text()
            self.parent().db.set_password(password)

class ScanProfileEditorDialog(QDialog):
    def __init__(self, parent=None, profile=None):
        super().__init__(parent)
        self.setWindowTitle("Scan Profile")

        self.name_input = QLineEdit()
        self.network_range_input = QLineEdit()
        self.ports_input = QLineEdit()

        if profile:
            self.name_input.setText(profile[0])
            self.network_range_input.setText(profile[1])
            self.ports_input.setText(profile[2])

        form_layout = QFormLayout()
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Network Range:", self.network_range_input)
        form_layout.addRow("Ports:", self.ports_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

class ScanProfilesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scan Profiles")
        self.db = parent.db

        self.profiles_list = QListWidget()
        self.load_profiles()

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_profile)
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_profile)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_profile)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)

        layout = QVBoxLayout()
        layout.addWidget(self.profiles_list)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_profiles(self):
        self.profiles_list.clear()
        profiles = self.db.get_scan_profiles()
        for profile in profiles:
            self.profiles_list.addItem(profile[0])

    def add_profile(self):
        dialog = ScanProfileEditorDialog(self)
        if dialog.exec_():
            name = dialog.name_input.text()
            network_range = dialog.network_range_input.text()
            ports = dialog.ports_input.text()
            self.db.add_scan_profile(name, network_range, ports)
            self.load_profiles()

    def edit_profile(self):
        selected_item = self.profiles_list.currentItem()
        if not selected_item:
            return

        profile_name = selected_item.text()
        profiles = self.db.get_scan_profiles()
        profile = next((p for p in profiles if p[0] == profile_name), None)

        if profile:
            dialog = ScanProfileEditorDialog(self, profile)
            if dialog.exec_():
                new_name = dialog.name_input.text()
                network_range = dialog.network_range_input.text()
                ports = dialog.ports_input.text()
                self.db.update_scan_profile(profile_name, new_name, network_range, ports)
                self.load_profiles()

    def delete_profile(self):
        selected_item = self.profiles_list.currentItem()
        if not selected_item:
            return

        profile_name = selected_item.text()
        self.db.delete_scan_profile(profile_name)
        self.load_profiles()

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

        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.clicked.connect(self.open_settings)
        sidebar_layout.addWidget(self.settings_button)

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
        self.profile_combo = QComboBox()
        self.load_scan_profiles()
        top_layout.addWidget(self.profile_combo)

        top_layout.addWidget(self.network_input)
        top_layout.addWidget(scan_button)

        scan_profiles_button = QPushButton("Scan Profiles")
        scan_profiles_button.clicked.connect(self.open_scan_profiles)
        top_layout.addWidget(scan_profiles_button)

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

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_():
            theme = dialog.theme_combo.currentText()
            self.set_theme(theme)

    def set_theme(self, theme):
        if theme == "Dark":
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; }
                QTabWidget::pane { border: 1px solid #444; }
                QTabBar::tab { background: #3c3c3c; color: white; }
                QTabBar::tab:selected { background: #555; }
                QTableWidget { background-color: #3c3c3c; color: white; }
                QHeaderView::section { background-color: #555; color: white; }
                QPushButton { background-color: #555; color: white; border: 1px solid #444; }
                QLineEdit { background-color: #555; color: white; border: 1px solid #444; }
                QLabel { color: white; }
            """)
        else:
            self.setStyleSheet("")

    def open_scan_profiles(self):
        dialog = ScanProfilesDialog(self)
        dialog.exec_()
        self.load_scan_profiles()

    def load_scan_profiles(self):
        self.profile_combo.clear()
        self.profile_combo.addItem("Default")
        profiles = self.db.get_scan_profiles()
        for profile in profiles:
            self.profile_combo.addItem(profile[0])

    def scan_devices(self):
        profile_name = self.profile_combo.currentText()
        if profile_name == "Default":
            network = self.network_input.text()
            ports = None
        else:
            profiles = self.db.get_scan_profiles()
            profile = next((p for p in profiles if p[0] == profile_name), None)
            if profile:
                network = profile[1]
                ports = profile[2]
            else: # Should not happen
                network = self.network_input.text()
                ports = None

        devices = self.scanner.discover_devices(network)
        for device in devices:
            details = self.scanner.get_device_details(device['ip'])
            device.update(details)
            self.db.add_or_update_device(device)

        self.load_devices()
        self.db.log_event("Scan", f"Scanned network {network} with profile {profile_name}")
        self.load_logs()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    db = Database()
    if db.check_password(""): # This is a bit of a hack to check if a password is set
        main_win = MainWindow()
        main_win.show()
    else:
        dialog = PasswordDialog()
        if dialog.exec_():
            if db.check_password(dialog.password_input.text()):
                main_win = MainWindow()
                main_win.show()
            else:
                sys.exit()
        else:
            sys.exit()

    sys.exit(app.exec_())
