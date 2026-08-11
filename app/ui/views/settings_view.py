"""
Settings, Configuration & Disaster Recovery View Widget for NQS POS v2.0
Manages general options, Gmail Postman SMTP credentials, Google Drive OAuth authentication, and database backups.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QFormLayout, QMessageBox, QFileDialog, QSpinBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.core.models import get_setting, set_setting
from app.services.backup_manager import (
    create_local_backup, list_local_backups, restore_database_from_backup
)
from app.services.gdrive_sync import (
    is_gdrive_configured, authenticate_gdrive, upload_backup_to_gdrive, get_credentials_path
)
from app.services.eod_postman import dispatch_eod_email
import shutil
from pathlib import Path


class SettingsView(QWidget):
    theme_changed_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Title
        title_box = QVBoxLayout()
        page_title = QLabel("System Settings & Disaster Recovery")
        page_title.setProperty("class", "SectionHeader")
        page_title.setStyleSheet("font-size: 20px;")
        sub_title = QLabel("Configure email reporting, Google Drive OAuth sync, and local backups")
        sub_title.setStyleSheet("color: #94A3B8; font-size: 12px;")
        title_box.addWidget(page_title)
        title_box.addWidget(sub_title)
        main_layout.addLayout(title_box)

        # Settings Tabs
        self.tab_widget = QTabWidget()

        # Tab 1: General & Theme
        self.tab_general = QWidget()
        self.init_general_tab()
        self.tab_widget.addTab(self.tab_general, "⚙️ General & Branding")

        # Tab 2: Email & Postman
        self.tab_email = QWidget()
        self.init_email_tab()
        self.tab_widget.addTab(self.tab_email, "✉️ E.O.D Postman Email")

        # Tab 3: Backup & Cloud Restore
        self.tab_backup = QWidget()
        self.init_backup_tab()
        self.tab_widget.addTab(self.tab_backup, "🛡️ Triple-Layer Disaster Recovery")

        main_layout.addWidget(self.tab_widget)

    # ------------------------------------------
    # GENERAL TAB LOGIC
    # ------------------------------------------
    def init_general_tab(self):
        layout = QVBoxLayout(self.tab_general)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        form_frame = QFrame()
        form_frame.setProperty("class", "CardFrame")
        form = QFormLayout(form_frame)
        form.setContentsMargins(20, 20, 20, 20)
        form.setSpacing(14)

        self.input_biz_name = QLineEdit()
        self.input_biz_address = QLineEdit()
        self.input_biz_phone = QLineEdit()

        self.spin_next_seq = QSpinBox()
        self.spin_next_seq.setRange(1, 999999)

        form.addRow("Business / Warehouse Name:", self.input_biz_name)
        form.addRow("Business Address:", self.input_biz_address)
        form.addRow("Contact Phone:", self.input_biz_phone)
        form.addRow("Next Perpetual Invoice Counter:", self.spin_next_seq)

        layout.addWidget(form_frame)

        # Theme Switcher Box
        theme_frame = QFrame()
        theme_frame.setProperty("class", "CardFrame")
        theme_layout = QHBoxLayout(theme_frame)
        theme_layout.setContentsMargins(20, 16, 20, 16)

        lbl_theme = QLabel("Application Visual Color Theme:")
        lbl_theme.setStyleSheet("font-weight: bold; font-size: 13px;")
        theme_layout.addWidget(lbl_theme)
        theme_layout.addStretch()

        btn_dark = QPushButton("🌙 Dark Theme")
        btn_dark.setProperty("class", "SecondaryBtn")
        btn_dark.clicked.connect(lambda: self.switch_theme("dark"))
        theme_layout.addWidget(btn_dark)

        btn_light = QPushButton("☀️ Light Theme")
        btn_light.setProperty("class", "SecondaryBtn")
        btn_light.clicked.connect(lambda: self.switch_theme("light"))
        theme_layout.addWidget(btn_light)

        layout.addWidget(theme_frame)

        btn_save = QPushButton("Save General Settings")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self.save_general_settings)
        layout.addWidget(btn_save)

        layout.addStretch()
        self.load_general_settings()

    def load_general_settings(self):
        self.input_biz_name.setText(get_setting('business_name', 'NQS Pharmaceutical Distributors'))
        self.input_biz_address.setText(get_setting('business_address', 'Warehouse Operations'))
        self.input_biz_phone.setText(get_setting('business_phone', '+92-300-1234567'))

        seq_str = get_setting('next_invoice_seq', '100')
        try:
            self.spin_next_seq.setValue(int(seq_str))
        except ValueError:
            self.spin_next_seq.setValue(100)

    def save_general_settings(self):
        set_setting('business_name', self.input_biz_name.text().strip())
        set_setting('business_address', self.input_biz_address.text().strip())
        set_setting('business_phone', self.input_biz_phone.text().strip())
        set_setting('next_invoice_seq', str(self.spin_next_seq.value()))
        QMessageBox.information(self, "Settings Saved", "General settings saved successfully.")

    def switch_theme(self, theme_name: str):
        set_setting('theme', theme_name)
        self.theme_changed_signal.emit(theme_name)
        QMessageBox.information(self, "Theme Applied", f"Switched to {theme_name.capitalize()} Theme.")

    # ------------------------------------------
    # EMAIL & POSTMAN TAB LOGIC
    # ------------------------------------------
    def init_email_tab(self):
        layout = QVBoxLayout(self.tab_email)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        form_frame = QFrame()
        form_frame.setProperty("class", "CardFrame")
        form = QFormLayout(form_frame)
        form.setContentsMargins(20, 20, 20, 20)
        form.setSpacing(14)

        self.input_smtp_email = QLineEdit()
        self.input_smtp_email.setPlaceholderText("e.g. nqs.warehouse@gmail.com")

        self.input_smtp_pwd = QLineEdit()
        self.input_smtp_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_smtp_pwd.setPlaceholderText("Gmail App Password (16-character code)")

        self.input_recipients = QLineEdit()
        self.input_recipients.setPlaceholderText("e.g. boss@nqs.com, manager@nqs.com (comma separated)")

        form.addRow("Sender Gmail Address *:", self.input_smtp_email)
        form.addRow("Gmail App Password *:", self.input_smtp_pwd)
        form.addRow("Stakeholders Recipient Emails *:", self.input_recipients)

        layout.addWidget(form_frame)

        btn_box = QHBoxLayout()
        btn_save_email = QPushButton("Save Email Settings")
        btn_save_email.setProperty("class", "PrimaryBtn")
        btn_save_email.clicked.connect(self.save_email_settings)
        btn_box.addWidget(btn_save_email)

        btn_test_email = QPushButton("📧 Test Send E.O.D Email Now")
        btn_test_email.setProperty("class", "SecondaryBtn")
        btn_test_email.clicked.connect(self.test_send_email)
        btn_box.addWidget(btn_test_email)

        layout.addLayout(btn_box)
        layout.addStretch()
        self.load_email_settings()

    def load_email_settings(self):
        self.input_smtp_email.setText(get_setting('smtp_email', ''))
        self.input_smtp_pwd.setText(get_setting('smtp_password', ''))
        self.input_recipients.setText(get_setting('recipient_emails', ''))

    def save_email_settings(self):
        set_setting('smtp_email', self.input_smtp_email.text().strip())
        set_setting('smtp_password', self.input_smtp_pwd.text().strip())
        set_setting('recipient_emails', self.input_recipients.text().strip())
        QMessageBox.information(self, "Email Settings Saved", "Gmail EOD Postman credentials saved.")

    def test_send_email(self):
        self.save_email_settings()
        res = dispatch_eod_email()
        if res.get('success'):
            QMessageBox.information(self, "Success", f"Test E.O.D email dispatched successfully to recipients!")
        else:
            QMessageBox.critical(self, "Dispatch Error", f"Failed to send email: {res.get('error')}")

    # ------------------------------------------
    # BACKUP & DISASTER RECOVERY TAB LOGIC
    # ------------------------------------------
    def init_backup_tab(self):
        layout = QVBoxLayout(self.tab_backup)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Top Section: Google Drive Status & Config
        gdrive_box = QFrame()
        gdrive_box.setProperty("class", "CardFrame")
        gdrive_l = QVBoxLayout(gdrive_box)
        gdrive_l.setContentsMargins(16, 14, 16, 14)
        gdrive_l.setSpacing(10)

        gd_title = QLabel("☁️ Cloud Vault (Google Drive OAuth2 Mirroring)")
        gd_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #38BDF8;")
        gdrive_l.addWidget(gd_title)

        self.lbl_gdrive_status = QLabel("Google Drive Sync Status: Checking...")
        gdrive_l.addWidget(self.lbl_gdrive_status)

        gd_btns = QHBoxLayout()

        btn_import_cred = QPushButton("Select credentials.json File")
        btn_import_cred.setProperty("class", "SecondaryBtn")
        btn_import_cred.clicked.connect(self.import_gdrive_credentials)
        gd_btns.addWidget(btn_import_cred)

        btn_auth_gdrive = QPushButton("🔑 Authenticate via Browser")
        btn_auth_gdrive.setProperty("class", "PrimaryBtn")
        btn_auth_gdrive.clicked.connect(self.auth_gdrive_action)
        gd_btns.addWidget(btn_auth_gdrive)

        btn_test_upload = QPushButton("☁️ Upload Backup to Drive Now")
        btn_test_upload.setProperty("class", "SuccessBtn")
        btn_test_upload.clicked.connect(self.test_upload_gdrive)
        gd_btns.addWidget(btn_test_upload)

        gdrive_l.addLayout(gd_btns)
        layout.addWidget(gdrive_box)

        # Middle Section: Local Backups List & Manual Backup Button
        local_box = QFrame()
        local_box.setProperty("class", "CardFrame")
        local_l = QVBoxLayout(local_box)
        local_l.setContentsMargins(16, 14, 16, 14)
        local_l.setSpacing(12)

        loc_hdr = QHBoxLayout()
        loc_title = QLabel("💾 Time-Stamped Local ZIP Backups (30-Day Auto Retention)")
        loc_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        loc_hdr.addWidget(loc_title)
        loc_hdr.addStretch()

        btn_create_backup = QPushButton("+ Create Local Backup Now")
        btn_create_backup.setProperty("class", "SuccessBtn")
        btn_create_backup.clicked.connect(self.create_backup_action)
        loc_hdr.addWidget(btn_create_backup)
        local_l.addLayout(loc_hdr)

        self.table_backups = QTableWidget()
        self.table_backups.setColumnCount(4)
        self.table_backups.setHorizontalHeaderLabels(["Archive Filename", "Created Date & Time", "Size (KB)", "Restore"])
        self.table_backups.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_backups.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        local_l.addWidget(self.table_backups)

        layout.addWidget(local_box)

        self.refresh_backup_status()

    def refresh_backup_status(self):
        # Update GDrive Status
        if is_gdrive_configured():
            self.lbl_gdrive_status.setText("Google Drive Sync Status: ✅ Configured & Ready")
            self.lbl_gdrive_status.setStyleSheet("color: #10B981; font-weight: bold;")
        else:
            self.lbl_gdrive_status.setText("Google Drive Sync Status: ⚠️ Not Authenticated (Import credentials.json first)")
            self.lbl_gdrive_status.setStyleSheet("color: #F59E0B; font-weight: bold;")

        # Load Local Backups
        backups = list_local_backups()
        self.table_backups.setRowCount(len(backups))

        for idx, b in enumerate(backups):
            self.table_backups.setItem(idx, 0, QTableWidgetItem(b['filename']))
            self.table_backups.setItem(idx, 1, QTableWidgetItem(b['created_at']))
            self.table_backups.setItem(idx, 2, QTableWidgetItem(f"{b['size_kb']} KB"))

            btn_restore = QPushButton("Restore DB")
            btn_restore.setProperty("class", "DangerBtn")
            btn_restore.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_restore.clicked.connect(lambda _, fp=b['filepath']: self.restore_backup_action(fp))
            self.table_backups.setCellWidget(idx, 3, btn_restore)

    def import_gdrive_credentials(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Google Client credentials.json", "", "JSON Files (*.json)")
        if file_path:
            try:
                dest = get_credentials_path()
                shutil.copy(file_path, dest)
                QMessageBox.information(self, "Credentials Imported", f"Imported credentials.json successfully.")
                self.refresh_backup_status()
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import credentials: {e}")

    def auth_gdrive_action(self):
        try:
            ok = authenticate_gdrive()
            if ok:
                QMessageBox.information(self, "Authenticated", "Google Drive authorized successfully!")
                self.refresh_backup_status()
            else:
                QMessageBox.warning(self, "Auth Error", "Could not complete Google Drive authorization.")
        except Exception as e:
            QMessageBox.critical(self, "Auth Error", str(e))

    def create_backup_action(self):
        try:
            zip_path = create_local_backup()
            QMessageBox.information(self, "Backup Created", f"Local ZIP backup created successfully:\n{zip_path}")
            self.refresh_backup_status()
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to create backup: {e}")

    def test_upload_gdrive(self):
        try:
            zip_path = create_local_backup()
            res = upload_backup_to_gdrive(zip_path)
            if res.get('success'):
                QMessageBox.information(self, "Cloud Mirror Success", f"Backup mirrored to Google Drive successfully!")
            else:
                QMessageBox.warning(self, "Upload Warning", f"Drive upload failed: {res.get('error')}")
        except Exception as e:
            QMessageBox.critical(self, "Upload Error", str(e))

    def restore_backup_action(self, zip_filepath: str):
        reply = QMessageBox.question(
            self, "Confirm Database Restoration",
            "WARNING: Restoring the database will overwrite active data with the backup archive.\nAre you sure you want to proceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                restore_database_from_backup(zip_filepath)
                QMessageBox.information(self, "Restored", "Database restored successfully. Please restart the application.")
            except Exception as e:
                QMessageBox.critical(self, "Restore Error", f"Failed to restore database: {e}")
