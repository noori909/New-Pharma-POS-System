"""
Inventory Management View Widget for New Quetta Surgical and Medicine Distribution (NQS POS v2.0)
Handles product CRUD operations, selectable Trade Price vs MRP rules, stock updates, reorder thresholds, and low-stock alerts.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QDoubleSpinBox, QSpinBox, QCheckBox, QMessageBox,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.core.models import (
    get_all_products, add_product, update_product,
    delete_product, update_product_stock
)
from app.core.pricing import calculate_tp


class ProductDialog(QDialog):
    def __init__(self, product_data: dict = None, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        self.setWindowTitle("Edit Product" if product_data else "Add New Product")
        self.setFixedWidth(420)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(12)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("e.g., Amoxicillin 500mg Suspension")

        self.input_mrp = QDoubleSpinBox()
        self.input_mrp.setRange(0.0, 999999.00)
        self.input_mrp.setDecimals(2)
        self.input_mrp.setSingleStep(10.0)
        self.input_mrp.valueChanged.connect(self.update_tp_preview)

        self.check_has_tp = QCheckBox("Apply Trade Price (TP = MRP - 15%)")
        self.check_has_tp.setChecked(True)
        self.check_has_tp.toggled.connect(self.update_tp_preview)

        self.lbl_tp_preview = QLabel("Base Price: PKR 0.00 (Trade Price)")
        self.lbl_tp_preview.setStyleSheet("color: #16A34A; font-weight: bold; font-size: 12px;")

        self.input_stock = QSpinBox()
        self.input_stock.setRange(0, 999999)
        self.input_stock.setValue(100)

        self.input_reorder = QSpinBox()
        self.input_reorder.setRange(0, 99999)
        self.input_reorder.setValue(15)

        form.addRow("Product Name *:", self.input_name)
        form.addRow("Maximum Retail Price (MRP) *:", self.input_mrp)
        form.addRow("Pricing Rule:", self.check_has_tp)
        form.addRow("", self.lbl_tp_preview)
        form.addRow("Current Stock Quantity *:", self.input_stock)
        form.addRow("Reorder Level Alert *:", self.input_reorder)

        layout.addLayout(form)

        if self.product_data:
            self.input_name.setText(self.product_data.get('name', ''))
            self.input_mrp.setValue(self.product_data.get('mrp', 0.0))
            self.check_has_tp.setChecked(bool(self.product_data.get('has_tp', True)))
            self.input_stock.setValue(self.product_data.get('stock', 0))
            self.input_reorder.setValue(self.product_data.get('reorder_level', 10))
            self.update_tp_preview()
        else:
            self.update_tp_preview()

        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("Save Product")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.clicked.connect(self.accept)
        btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    def update_tp_preview(self):
        mrp = self.input_mrp.value()
        has_tp = self.check_has_tp.isChecked()
        tp = calculate_tp(mrp, has_tp=has_tp)
        if has_tp:
            self.lbl_tp_preview.setText(f"Base Price: PKR {tp:,.2f} (Trade Price = MRP - 15%)")
            self.lbl_tp_preview.setStyleSheet("color: #16A34A; font-weight: bold; font-size: 12px;")
        else:
            self.lbl_tp_preview.setText(f"Base Price: PKR {tp:,.2f} (Sold at full MRP)")
            self.lbl_tp_preview.setStyleSheet("color: #0284C7; font-weight: bold; font-size: 12px;")

    def get_data(self) -> dict:
        return {
            'name': self.input_name.text().strip(),
            'mrp': self.input_mrp.value(),
            'has_tp': self.check_has_tp.isChecked(),
            'stock': self.input_stock.value(),
            'reorder_level': self.input_reorder.value()
        }


class InventoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(12)

        # Header Title
        hdr_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        page_title = QLabel("Inventory & Stock Control")
        page_title.setProperty("class", "SectionHeader")
        page_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        sub_title = QLabel("New Quetta Surgical and Medicine Distribution • Catalog, Stock & Pricing Control")
        sub_title.setProperty("class", "SubHeader")
        sub_title.setStyleSheet("font-size: 12px;")
        title_box.addWidget(page_title)
        title_box.addWidget(sub_title)
        hdr_layout.addLayout(title_box)
        hdr_layout.addStretch()

        btn_add_product = QPushButton("+ Add New Product")
        btn_add_product.setProperty("class", "PrimaryBtn")
        btn_add_product.clicked.connect(self.open_add_dialog)
        hdr_layout.addWidget(btn_add_product)

        main_layout.addLayout(hdr_layout)

        # Filter & Search Bar
        filter_frame = QFrame()
        filter_frame.setProperty("class", "CardFrame")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(14, 10, 14, 10)

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Filter products by name...")
        self.input_search.textChanged.connect(self.load_products)
        filter_layout.addWidget(self.input_search)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setProperty("class", "SecondaryBtn")
        btn_refresh.clicked.connect(self.load_products)
        filter_layout.addWidget(btn_refresh)

        main_layout.addWidget(filter_frame)

        # Products Table with generous, un-clipped column widths
        self.table_products = QTableWidget()
        self.table_products.setColumnCount(7)
        self.table_products.setHorizontalHeaderLabels([
            "Sr.", "Product Name", "MRP (PKR)", "Pricing Rule / Rate", "Stock Level", "Reorder Level", "Actions"
        ])
        self.table_products.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_products.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_products.verticalHeader().setDefaultSectionSize(36)

        # Explicit widths to guarantee zero text clipping on buttons
        self.table_products.setColumnWidth(0, 45)   # Sr.
        # Col 1: Product Name is Stretch
        self.table_products.setColumnWidth(2, 95)   # MRP (PKR)
        self.table_products.setColumnWidth(3, 140)  # Pricing Rule / Rate
        self.table_products.setColumnWidth(4, 90)   # Stock Level
        self.table_products.setColumnWidth(5, 95)   # Reorder Level
        self.table_products.setColumnWidth(6, 145)  # Actions (Guarantees room for Edit & Delete)

        main_layout.addWidget(self.table_products)

        self.load_products()

    def load_products(self):
        query = self.input_search.text().strip()
        products = get_all_products(query)

        self.table_products.setRowCount(len(products))

        for row_idx, p in enumerate(products):
            self.table_products.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table_products.setItem(row_idx, 1, QTableWidgetItem(p['name']))
            self.table_products.setItem(row_idx, 2, QTableWidgetItem(f"{p['mrp']:,.2f}"))
            
            rule_str = f"{p['tp']:,.2f} (TP)" if p.get('has_tp', True) else f"{p['tp']:,.2f} (MRP)"
            self.table_products.setItem(row_idx, 3, QTableWidgetItem(rule_str))

            stock_item = QTableWidgetItem(str(p['stock']))
            if p['stock'] <= p['reorder_level']:
                stock_item.setForeground(Qt.GlobalColor.red)
                stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_products.setItem(row_idx, 4, stock_item)

            self.table_products.setItem(row_idx, 5, QTableWidgetItem(str(p['reorder_level'])))

            # Actions Layout (Fixed size buttons with guaranteed readable text)
            actions_widget = QWidget()
            act_layout = QHBoxLayout(actions_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(6)

            btn_edit = QPushButton("Edit")
            btn_edit.setProperty("class", "SecondaryBtn")
            btn_edit.setFixedWidth(58)
            btn_edit.setStyleSheet("padding: 3px 6px; font-size: 11px; font-weight: 600;")
            btn_edit.clicked.connect(lambda _, prod=p: self.open_edit_dialog(prod))
            act_layout.addWidget(btn_edit)

            btn_del = QPushButton("Delete")
            btn_del.setProperty("class", "DangerBtn")
            btn_del.setFixedWidth(64)
            btn_del.setStyleSheet("padding: 3px 6px; font-size: 11px; font-weight: 600;")
            btn_del.clicked.connect(lambda _, p_id=p['id'], p_name=p['name']: self.delete_product_action(p_id, p_name))
            act_layout.addWidget(btn_del)

            self.table_products.setCellWidget(row_idx, 6, actions_widget)

    def open_add_dialog(self):
        dlg = ProductDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Validation Error", "Product Name cannot be empty.")
                return
            try:
                add_product(data['name'], data['mrp'], data['stock'], data['reorder_level'], has_tp=data['has_tp'])
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add product: {e}")

    def open_edit_dialog(self, product_data: dict):
        dlg = ProductDialog(product_data=product_data, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data['name']:
                QMessageBox.warning(self, "Validation Error", "Product Name cannot be empty.")
                return
            try:
                update_product(product_data['id'], data['name'], data['mrp'], data['stock'], data['reorder_level'], has_tp=data['has_tp'])
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update product: {e}")

    def delete_product_action(self, product_id: int, product_name: str):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete product '{product_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_product(product_id)
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete product: {e}")
