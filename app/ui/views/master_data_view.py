"""
Master Data Management View Widget for NQS POS v2.0
Handles CRUD operations for Customers, Discount Tiers, Sales Representatives, and Geographical Areas.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QDialog, QFormLayout, QComboBox, QMessageBox, QDoubleSpinBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from app.core.models import (
    get_all_customers, add_customer, update_customer, delete_customer,
    get_all_sales_reps, add_sales_rep, update_sales_rep, delete_sales_rep,
    get_all_areas, add_area, update_area, delete_area,
    get_all_discount_tiers, add_discount_tier, update_discount_tier, delete_discount_tier
)


# ==========================================
# CUSTOMER DIALOG
# ==========================================
class CustomerDialog(QDialog):
    def __init__(self, areas: list, discount_tiers: list, cust_data: dict = None, parent=None):
        super().__init__(parent)
        self.areas = areas
        self.discount_tiers = discount_tiers
        self.cust_data = cust_data
        self.setWindowTitle("Edit Customer" if cust_data else "Add New Customer")
        self.setFixedWidth(420)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(12)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Customer / Pharmacy Name")

        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Contact Phone")

        self.input_address = QLineEdit()
        self.input_address.setPlaceholderText("Warehouse / Shop Address")

        self.combo_area = QComboBox()
        self.combo_area.addItem("-- Select Geographical Area --", None)
        for a in self.areas:
            self.combo_area.addItem(a['name'], a['id'])

        self.combo_tier = QComboBox()
        if not self.discount_tiers:
            self.combo_tier.addItem("Standard (0%)", (0.0, None))
        else:
            for t in self.discount_tiers:
                self.combo_tier.addItem(f"{t['name']} ({t['percentage']:.1f}%)", (t['percentage'], t['id']))

        form.addRow("Customer Name *:", self.input_name)
        form.addRow("Phone Number:", self.input_phone)
        form.addRow("Address:", self.input_address)
        form.addRow("Geographical Area *:", self.combo_area)
        form.addRow("Discount Tier *:", self.combo_tier)

        layout.addLayout(form)

        if self.cust_data:
            self.input_name.setText(self.cust_data.get('name', ''))
            self.input_phone.setText(self.cust_data.get('phone', ''))
            self.input_address.setText(self.cust_data.get('address', ''))
            
            # Select area
            area_id = self.cust_data.get('area_id')
            if area_id:
                idx = self.combo_area.findData(area_id)
                if idx >= 0:
                    self.combo_area.setCurrentIndex(idx)

            # Select tier
            tier_id = self.cust_data.get('discount_tier_id')
            tier_val = float(self.cust_data.get('discount_tier', 0.0))
            
            found_idx = -1
            for i in range(self.combo_tier.count()):
                pct, tid = self.combo_tier.itemData(i)
                if tid == tier_id or (tid is None and pct == tier_val):
                    found_idx = i
                    break
            if found_idx >= 0:
                self.combo_tier.setCurrentIndex(found_idx)

        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("Save Customer")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self.accept)
        btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    def get_data(self) -> dict:
        pct, tid = self.combo_tier.itemData(self.combo_tier.currentIndex())
        return {
            'name': self.input_name.text().strip(),
            'phone': self.input_phone.text().strip(),
            'address': self.input_address.text().strip(),
            'area_id': self.combo_area.currentData(),
            'discount_tier': float(pct),
            'discount_tier_id': tid
        }


# ==========================================
# DISCOUNT TIER DIALOG
# ==========================================
class DiscountTierDialog(QDialog):
    def __init__(self, tier_data: dict = None, parent=None):
        super().__init__(parent)
        self.tier_data = tier_data
        self.setWindowTitle("Edit Discount Tier" if tier_data else "Add New Discount Tier")
        self.setFixedWidth(360)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(12)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Tier Name (e.g. Gold, Preferred)")

        self.input_percentage = QDoubleSpinBox()
        self.input_percentage.setRange(0.0, 100.0)
        self.input_percentage.setDecimals(1)
        self.input_percentage.setSuffix("%")

        form.addRow("Tier Name *:", self.input_name)
        form.addRow("Discount Percentage *:", self.input_percentage)

        layout.addLayout(form)

        if self.tier_data:
            self.input_name.setText(self.tier_data.get('name', ''))
            self.input_percentage.setValue(float(self.tier_data.get('percentage', 0.0)))

        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("Save Tier")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self.accept)
        btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    def get_data(self) -> dict:
        return {
            'name': self.input_name.text().strip(),
            'percentage': self.input_percentage.value()
        }


# ==========================================
# SALES REP DIALOG
# ==========================================
class SalesRepDialog(QDialog):
    def __init__(self, rep_data: dict = None, parent=None):
        super().__init__(parent)
        self.rep_data = rep_data
        self.setWindowTitle("Edit Sales Rep" if rep_data else "Add New Sales Rep")
        self.setFixedWidth(380)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(12)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Sales Representative Full Name")

        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Mobile / Phone Number")

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Email Address")

        form.addRow("Rep Name *:", self.input_name)
        form.addRow("Phone Number:", self.input_phone)
        form.addRow("Email Address:", self.input_email)

        layout.addLayout(form)

        if self.rep_data:
            self.input_name.setText(self.rep_data.get('name', ''))
            self.input_phone.setText(self.rep_data.get('phone', ''))
            self.input_email.setText(self.rep_data.get('email', ''))

        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("Save Rep")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self.accept)
        btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    def get_data(self) -> dict:
        return {
            'name': self.input_name.text().strip(),
            'phone': self.input_phone.text().strip(),
            'email': self.input_email.text().strip()
        }


# ==========================================
# AREA DIALOG
# ==========================================
class AreaDialog(QDialog):
    def __init__(self, area_data: dict = None, parent=None):
        super().__init__(parent)
        self.area_data = area_data
        self.setWindowTitle("Edit Area" if area_data else "Add New Area")
        self.setFixedWidth(360)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(12)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Area Name (e.g. Saddar Zone A)")

        self.input_region = QLineEdit()
        self.input_region.setPlaceholderText("City / District Region")

        form.addRow("Area Name *:", self.input_name)
        form.addRow("City / Region:", self.input_region)

        layout.addLayout(form)

        if self.area_data:
            self.input_name.setText(self.area_data.get('name', ''))
            self.input_region.setText(self.area_data.get('region', ''))

        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("Save Area")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self.accept)
        btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    def get_data(self) -> dict:
        return {
            'name': self.input_name.text().strip(),
            'region': self.input_region.text().strip()
        }


# ==========================================
# MAIN MASTER DATA VIEW WIDGET
# ==========================================
class MasterDataView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Title
        title_box = QVBoxLayout()
        page_title = QLabel("Master Data Administration")
        page_title.setProperty("class", "SectionHeader")
        page_title.setStyleSheet("font-size: 20px;")
        sub_title = QLabel("Configure Customers, Customer Discount Tiers, Sales Representatives, and Areas")
        sub_title.setStyleSheet("color: #94A3B8; font-size: 12px;")
        title_box.addWidget(page_title)
        title_box.addWidget(sub_title)
        main_layout.addLayout(title_box)

        # Tabs
        self.tab_widget = QTabWidget()

        # Tab 1: Customers
        self.tab_customers = QWidget()
        self.init_customers_tab()
        self.tab_widget.addTab(self.tab_customers, "👥 Customers Management")

        # Tab 2: Discount Tiers
        self.tab_tiers = QWidget()
        self.init_tiers_tab()
        self.tab_widget.addTab(self.tab_tiers, "🏷️ Discount Tiers")

        # Tab 3: Sales Reps
        self.tab_reps = QWidget()
        self.init_reps_tab()
        self.tab_widget.addTab(self.tab_reps, "👔 Sales Representatives")

        # Tab 4: Areas
        self.tab_areas = QWidget()
        self.init_areas_tab()
        self.tab_widget.addTab(self.tab_areas, "📍 Geographical Areas")

        main_layout.addWidget(self.tab_widget)

    # ------------------------------------------
    # CUSTOMERS TAB LOGIC
    # ------------------------------------------
    def init_customers_tab(self):
        layout = QVBoxLayout(self.tab_customers)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        top_bar = QHBoxLayout()
        self.search_cust = QLineEdit()
        self.search_cust.setPlaceholderText("🔍 Filter customers by name or phone...")
        self.search_cust.textChanged.connect(self.load_customers)
        top_bar.addWidget(self.search_cust)

        btn_add_cust = QPushButton("+ Add Customer")
        btn_add_cust.setProperty("class", "PrimaryBtn")
        btn_add_cust.clicked.connect(self.open_add_customer)
        top_bar.addWidget(btn_add_cust)

        layout.addLayout(top_bar)

        self.table_customers = QTableWidget()
        self.table_customers.setColumnCount(6)
        self.table_customers.setHorizontalHeaderLabels([
            "#", "Customer Name", "Phone", "Geographical Area", "Discount Tier", "Actions"
        ])
        self.table_customers.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_customers.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_customers)

        self.load_customers()

    def load_customers(self):
        query = self.search_cust.text().strip()
        customers = get_all_customers(query)
        self.table_customers.setRowCount(len(customers))

        for row_idx, c in enumerate(customers):
            self.table_customers.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table_customers.setItem(row_idx, 1, QTableWidgetItem(c['name']))
            self.table_customers.setItem(row_idx, 2, QTableWidgetItem(c['phone'] or "-"))
            self.table_customers.setItem(row_idx, 3, QTableWidgetItem(c['area_name'] or "Unassigned"))

            tier_display = f"{c.get('tier_name') or 'Tier'} ({c['discount_tier']:.1f}%)"
            tier_item = QTableWidgetItem(tier_display)
            tier_item.setForeground(Qt.GlobalColor.cyan)
            tier_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_customers.setItem(row_idx, 4, tier_item)

            actions = QWidget()
            act_l = QHBoxLayout(actions)
            act_l.setContentsMargins(4, 2, 4, 2)
            act_l.setSpacing(6)

            btn_e = QPushButton("Edit")
            btn_e.setProperty("class", "SecondaryBtn")
            btn_e.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_e.clicked.connect(lambda _, cust=c: self.open_edit_customer(cust))
            act_l.addWidget(btn_e)

            btn_d = QPushButton("Delete")
            btn_d.setProperty("class", "DangerBtn")
            btn_d.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_d.clicked.connect(lambda _, c_id=c['id'], c_name=c['name']: self.delete_customer_action(c_id, c_name))
            act_l.addWidget(btn_d)

            self.table_customers.setCellWidget(row_idx, 5, actions)

    def open_add_customer(self):
        areas = get_all_areas()
        tiers = get_all_discount_tiers()
        dlg = CustomerDialog(areas=areas, discount_tiers=tiers, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Validation Error", "Customer name is required.")
                return
            try:
                add_customer(data['name'], data['phone'], data['address'], data['area_id'], data['discount_tier'], data['discount_tier_id'])
                self.load_customers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add customer: {e}")

    def open_edit_customer(self, cust_data: dict):
        areas = get_all_areas()
        tiers = get_all_discount_tiers()
        dlg = CustomerDialog(areas=areas, discount_tiers=tiers, cust_data=cust_data, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Validation Error", "Customer name is required.")
                return
            try:
                update_customer(cust_data['id'], data['name'], data['phone'], data['address'], data['area_id'], data['discount_tier'], data['discount_tier_id'])
                self.load_customers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update customer: {e}")

    def delete_customer_action(self, cust_id: int, cust_name: str):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete customer '{cust_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_customer(cust_id)
                self.load_customers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete customer: {e}")

    # ------------------------------------------
    # DISCOUNT TIERS TAB LOGIC
    # ------------------------------------------
    def init_tiers_tab(self):
        layout = QVBoxLayout(self.tab_tiers)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        top_bar = QHBoxLayout()
        lbl_info = QLabel("Configure standard customer discount tiers (e.g. 0%, 4%, 7%, 12%) applied to Trade Price (TP).")
        lbl_info.setStyleSheet("color: #94A3B8; font-size: 12px;")
        top_bar.addWidget(lbl_info)
        top_bar.addStretch()

        btn_add_tier = QPushButton("+ Add Discount Tier")
        btn_add_tier.setProperty("class", "PrimaryBtn")
        btn_add_tier.clicked.connect(self.open_add_tier)
        top_bar.addWidget(btn_add_tier)

        layout.addLayout(top_bar)

        self.table_tiers = QTableWidget()
        self.table_tiers.setColumnCount(4)
        self.table_tiers.setHorizontalHeaderLabels(["#", "Tier Name", "Discount Percentage", "Actions"])
        self.table_tiers.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_tiers.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_tiers)

        self.load_tiers()

    def load_tiers(self):
        tiers = get_all_discount_tiers()
        self.table_tiers.setRowCount(len(tiers))

        for row_idx, t in enumerate(tiers):
            self.table_tiers.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table_tiers.setItem(row_idx, 1, QTableWidgetItem(t['name']))
            
            pct_item = QTableWidgetItem(f"{t['percentage']:.1f}%")
            pct_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_tiers.setItem(row_idx, 2, pct_item)

            actions = QWidget()
            act_l = QHBoxLayout(actions)
            act_l.setContentsMargins(4, 2, 4, 2)
            act_l.setSpacing(6)

            btn_e = QPushButton("Edit")
            btn_e.setProperty("class", "SecondaryBtn")
            btn_e.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_e.clicked.connect(lambda _, tier=t: self.open_edit_tier(tier))
            act_l.addWidget(btn_e)

            btn_d = QPushButton("Delete")
            btn_d.setProperty("class", "DangerBtn")
            btn_d.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_d.clicked.connect(lambda _, t_id=t['id'], t_name=t['name']: self.delete_tier_action(t_id, t_name))
            act_l.addWidget(btn_d)

            self.table_tiers.setCellWidget(row_idx, 3, actions)

    def open_add_tier(self):
        dlg = DiscountTierDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Validation Error", "Tier name is required.")
                return
            try:
                add_discount_tier(data['name'], data['percentage'])
                self.load_tiers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add tier: {e}")

    def open_edit_tier(self, tier_data: dict):
        dlg = DiscountTierDialog(tier_data=tier_data, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Validation Error", "Tier name is required.")
                return
            try:
                update_discount_tier(tier_data['id'], data['name'], data['percentage'])
                self.load_tiers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update tier: {e}")

    def delete_tier_action(self, tier_id: int, tier_name: str):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete discount tier '{tier_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_discount_tier(tier_id)
                self.load_tiers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete tier: {e}")

    # ------------------------------------------
    # SALES REPS TAB LOGIC
    # ------------------------------------------
    def init_reps_tab(self):
        layout = QVBoxLayout(self.tab_reps)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        btn_add_rep = QPushButton("+ Add Sales Rep")
        btn_add_rep.setProperty("class", "PrimaryBtn")
        btn_add_rep.clicked.connect(self.open_add_rep)
        top_bar.addWidget(btn_add_rep)
        layout.addLayout(top_bar)

        self.table_reps = QTableWidget()
        self.table_reps.setColumnCount(5)
        self.table_reps.setHorizontalHeaderLabels(["#", "Sales Rep Name", "Phone Number", "Email Address", "Actions"])
        self.table_reps.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_reps.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_reps)

        self.load_reps()

    def load_reps(self):
        reps = get_all_sales_reps()
        self.table_reps.setRowCount(len(reps))

        for row_idx, r in enumerate(reps):
            self.table_reps.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table_reps.setItem(row_idx, 1, QTableWidgetItem(r['name']))
            self.table_reps.setItem(row_idx, 2, QTableWidgetItem(r['phone'] or "-"))
            self.table_reps.setItem(row_idx, 3, QTableWidgetItem(r['email'] or "-"))

            actions = QWidget()
            act_l = QHBoxLayout(actions)
            act_l.setContentsMargins(4, 2, 4, 2)
            act_l.setSpacing(6)

            btn_e = QPushButton("Edit")
            btn_e.setProperty("class", "SecondaryBtn")
            btn_e.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_e.clicked.connect(lambda _, rep=r: self.open_edit_rep(rep))
            act_l.addWidget(btn_e)

            btn_d = QPushButton("Delete")
            btn_d.setProperty("class", "DangerBtn")
            btn_d.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_d.clicked.connect(lambda _, r_id=r['id'], r_name=r['name']: self.delete_rep_action(r_id, r_name))
            act_l.addWidget(btn_d)

            self.table_reps.setCellWidget(row_idx, 4, actions)

    def open_add_rep(self):
        dlg = SalesRepDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Validation Error", "Sales Rep name is required.")
                return
            try:
                add_sales_rep(data['name'], data['phone'], data['email'])
                self.load_reps()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add sales rep: {e}")

    def open_edit_rep(self, rep_data: dict):
        dlg = SalesRepDialog(rep_data=rep_data, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Validation Error", "Sales Rep name is required.")
                return
            try:
                update_sales_rep(rep_data['id'], data['name'], data['phone'], data['email'])
                self.load_reps()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update sales rep: {e}")

    def delete_rep_action(self, rep_id: int, rep_name: str):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete sales rep '{rep_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_sales_rep(rep_id)
                self.load_reps()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete sales rep: {e}")

    # ------------------------------------------
    # AREAS TAB LOGIC
    # ------------------------------------------
    def init_areas_tab(self):
        layout = QVBoxLayout(self.tab_areas)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        btn_add_area = QPushButton("+ Add Geographical Area")
        btn_add_area.setProperty("class", "PrimaryBtn")
        btn_add_area.clicked.connect(self.open_add_area)
        top_bar.addWidget(btn_add_area)
        layout.addLayout(top_bar)

        self.table_areas = QTableWidget()
        self.table_areas.setColumnCount(4)
        self.table_areas.setHorizontalHeaderLabels(["#", "Area Name", "Region / Zone", "Actions"])
        self.table_areas.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_areas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_areas)

        self.load_areas()

    def load_areas(self):
        areas = get_all_areas()
        self.table_areas.setRowCount(len(areas))

        for row_idx, a in enumerate(areas):
            self.table_areas.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table_areas.setItem(row_idx, 1, QTableWidgetItem(a['name']))
            self.table_areas.setItem(row_idx, 2, QTableWidgetItem(a['region'] or "-"))

            actions = QWidget()
            act_l = QHBoxLayout(actions)
            act_l.setContentsMargins(4, 2, 4, 2)
            act_l.setSpacing(6)

            btn_e = QPushButton("Edit")
            btn_e.setProperty("class", "SecondaryBtn")
            btn_e.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_e.clicked.connect(lambda _, area=a: self.open_edit_area(area))
            act_l.addWidget(btn_e)

            btn_d = QPushButton("Delete")
            btn_d.setProperty("class", "DangerBtn")
            btn_d.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_d.clicked.connect(lambda _, a_id=a['id'], a_name=a['name']: self.delete_area_action(a_id, a_name))
            act_l.addWidget(btn_d)

            self.table_areas.setCellWidget(row_idx, 3, actions)

    def open_add_area(self):
        dlg = AreaDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Validation Error", "Area name is required.")
                return
            try:
                add_area(data['name'], data['region'])
                self.load_areas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add area: {e}")

    def open_edit_area(self, area_data: dict):
        dlg = AreaDialog(area_data=area_data, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Validation Error", "Area name is required.")
                return
            try:
                update_area(area_data['id'], data['name'], data['region'])
                self.load_areas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update area: {e}")

    def delete_area_action(self, area_id: int, area_name: str):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete area '{area_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_area(area_id)
                self.load_areas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete area: {e}")
