"""
Main Window & Navigation Shell for NQS POS v2.0
Assembles sidebar navigation, top header bar, view stack, theme toggles, and 10 PM EOD background timer.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QLabel, QPushButton, QStackedWidget, QButtonGroup, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QTime, QDate
from app.ui.styles import DARK_THEME_QSS, LIGHT_THEME_QSS
from app.ui.views.dashboard_view import DashboardView
from app.ui.views.pos_view import POSView
from app.ui.views.inventory_view import InventoryView
from app.ui.views.master_data_view import MasterDataView
from app.ui.views.reports_view import ReportsView
from app.ui.views.settings_view import SettingsView
from app.core.models import get_setting, set_setting
from app.services.backup_manager import create_local_backup
from app.services.eod_postman import dispatch_eod_email, check_and_run_eod_startup_check


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NQS POS v2.0 - New Pharma POS System")
        self.resize(1280, 800)

        # Run startup check for missed yesterday EOD email
        try:
            check_and_run_eod_startup_check()
        except Exception as e:
            print(f"Startup EOD check error: {e}")

        self.init_ui()
        self.setup_eod_timer()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. SIDEBAR NAVIGATION
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("SidebarFrame")
        self.sidebar_frame.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(8)

        # App Brand Header
        brand_box = QVBoxLayout()
        brand_title = QLabel("NQS POS v2.0")
        brand_title.setObjectName("AppTitleLabel")
        brand_sub = QLabel("Pharma Distribution System")
        brand_sub.setObjectName("SubTitleLabel")
        brand_box.addWidget(brand_title)
        brand_box.addWidget(brand_sub)
        sidebar_layout.addLayout(brand_box)
        sidebar_layout.addSpacing(16)

        # Nav Buttons Group
        self.nav_button_group = QButtonGroup(self)
        self.nav_button_group.setExclusive(True)

        self.btn_nav_dashboard = self.create_nav_button("📊 Dashboard", 0)
        self.btn_nav_pos = self.create_nav_button("⚡ New Sale / POS", 1)
        self.btn_nav_inventory = self.create_nav_button("📦 Inventory & Stock", 2)
        self.btn_nav_master = self.create_nav_button("👥 Master Data", 3)
        self.btn_nav_reports = self.create_nav_button("📈 BI Reports", 4)
        self.btn_nav_settings = self.create_nav_button("⚙️ Settings & Backup", 5)

        sidebar_layout.addWidget(self.btn_nav_dashboard)
        sidebar_layout.addWidget(self.btn_nav_pos)
        sidebar_layout.addWidget(self.btn_nav_inventory)
        sidebar_layout.addWidget(self.btn_nav_master)
        sidebar_layout.addWidget(self.btn_nav_reports)
        sidebar_layout.addWidget(self.btn_nav_settings)
        sidebar_layout.addStretch()

        # Sidebar Footer Status
        lbl_version = QLabel("Single-Workstation Build v2.0")
        lbl_version.setStyleSheet("color: #64748B; font-size: 10px; padding: 4px;")
        sidebar_layout.addWidget(lbl_version)

        main_layout.addWidget(self.sidebar_frame)

        # 2. RIGHT CONTAINER (HEADER + STACKED VIEWS)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header Frame
        self.header_frame = QFrame()
        self.header_frame.setObjectName("HeaderFrame")
        self.header_frame.setFixedHeight(54)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(20, 0, 20, 0)

        self.lbl_clock = QLabel()
        self.lbl_clock.setStyleSheet("font-weight: bold; color: #94A3B8; font-size: 12px;")
        header_layout.addWidget(self.lbl_clock)
        header_layout.addStretch()

        # Theme Toggle Button
        self.btn_theme_toggle = QPushButton("🌙 Dark")
        self.btn_theme_toggle.setProperty("class", "SecondaryBtn")
        self.btn_theme_toggle.setStyleSheet("padding: 5px 12px; font-size: 12px;")
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.btn_theme_toggle)

        right_layout.addWidget(self.header_frame)

        # View Stack
        self.view_stack = QStackedWidget()

        self.dashboard_view = DashboardView()
        self.dashboard_view.navigate_signal.connect(self.navigate_to_key)
        self.view_stack.addWidget(self.dashboard_view) # Index 0

        self.pos_view = POSView()
        self.pos_view.invoice_created_signal.connect(self.dashboard_view.load_data)
        self.view_stack.addWidget(self.pos_view) # Index 1

        self.inventory_view = InventoryView()
        self.view_stack.addWidget(self.inventory_view) # Index 2

        self.master_data_view = MasterDataView()
        self.view_stack.addWidget(self.master_data_view) # Index 3

        self.reports_view = ReportsView()
        self.view_stack.addWidget(self.reports_view) # Index 4

        self.settings_view = SettingsView()
        self.settings_view.theme_changed_signal.connect(self.apply_theme)
        self.view_stack.addWidget(self.settings_view) # Index 5

        right_layout.addWidget(self.view_stack)

        main_layout.addWidget(right_container)

        # Apply saved theme & initial nav
        current_theme = get_setting('theme', 'dark')
        self.apply_theme(current_theme)
        self.btn_nav_dashboard.setChecked(True)

        # Start Live Clock Timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_live_clock)
        self.clock_timer.start(1000)
        self.update_live_clock()

    def create_nav_button(self, title: str, index: int) -> QPushButton:
        btn = QPushButton(title)
        btn.setProperty("class", "NavButton")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.switch_view(index))
        self.nav_button_group.addButton(btn, index)
        return btn

    def switch_view(self, index: int):
        self.view_stack.setCurrentIndex(index)
        if index == 0:
            self.dashboard_view.load_data()
        elif index == 1:
            self.pos_view.reload_master_data()
        elif index == 2:
            self.inventory_view.load_products()
        elif index == 4:
            self.reports_view.load_all_reports()

    def navigate_to_key(self, key: str):
        key_map = {'dashboard': 0, 'pos': 1, 'inventory': 2, 'master': 3, 'reports': 4, 'settings': 5}
        idx = key_map.get(key, 0)
        btn = self.nav_button_group.button(idx)
        if btn:
            btn.setChecked(True)
        self.switch_view(idx)

    def update_live_clock(self):
        now_str = QDate.currentDate().toString("dddd, MMMM d, yyyy") + " • " + QTime.currentTime().toString("hh:mm:ss AP")
        self.lbl_clock.setText(now_str)

    def apply_theme(self, theme_name: str):
        if theme_name == 'light':
            self.setStyleSheet(LIGHT_THEME_QSS)
            self.btn_theme_toggle.setText("☀️ Light")
        else:
            self.setStyleSheet(DARK_THEME_QSS)
            self.btn_theme_toggle.setText("🌙 Dark")

    def toggle_theme(self):
        curr_theme = get_setting('theme', 'dark')
        new_theme = 'light' if curr_theme == 'dark' else 'dark'
        set_setting('theme', new_theme)
        self.apply_theme(new_theme)

    def setup_eod_timer(self):
        """Timer checking for 10:00 PM EOD dispatch."""
        self.eod_timer = QTimer(self)
        self.eod_timer.timeout.connect(self.check_10pm_eod)
        self.eod_timer.start(60000) # Check every 60 seconds

    def check_10pm_eod(self):
        now = QTime.currentTime()
        if now.hour() == 22 and now.minute() == 0:
            today_str = QDate.currentDate().toString("yyyy-MM-dd")
            last_eod = get_setting('last_eod_date', '')
            if last_eod != today_str:
                print("10:00 PM EOD Trigger Fired! Executing Postman logic...")
                dispatch_eod_email(report_date=today_str)

    def closeEvent(self, event):
        """Automatically creates local timestamped ZIP backup on app exit."""
        try:
            create_local_backup()
            print("Automatic exit backup completed.")
        except Exception as e:
            print(f"Error during exit backup: {e}")
        event.accept()
