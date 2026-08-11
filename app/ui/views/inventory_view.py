"""
Inventory Management View Widget for NQS POS v2.0
Handles product CRUD operations, stock updates, reorder thresholds, and low-stock alerts.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QDoubleSpinBox, QSpinBox, QMessageBox,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.core.models import (
    get_all_products, add_product, update_product,
    delete_product, update_product_stock
)


class ProductDialog(QDialog):
    def __init__(self, product_data: dict = None, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        self.setWindowTitle("Edit Product" if product_data else "Add New Product")
        self.setFixedWidth(400)
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

        self.lbl_tp_preview = QLabel("Base TP (MRP - 15%): PKR 0.00")
        self.lbl_tp_preview.setStyleSheet("color: #10B981; font-weight: bold; font-size: 12px;")

        self.input_stock = QSpinBox()
        self.input_stock.setRange(0, 999999)
        self.input_stock.setValue(100)

        self.input_reorder = QSpinBox()
        self.input_reorder.setRange(0, 99999)
        self.input_reorder.setValue(15)

        form.addRow("Product Name *:", self.input_name)
        form.addRow("Maximum Retail Price (MRP) *:", self.input_mrp)
        form.addRow("", self.lbl_tp_preview)
        form.addRow("Current Stock Quantity *:", self.input_stock)
        form.addRow("Reorder Level Alert *:", self.input_reorder)

        layout.addLayout(form)

        if self.product_data:
            self.input_name.setText(self.product_data.get('name', ''))
            self.input_mrp.setValue(self.product_data.get('mrp', 0.0))
            self.input_stock.setValue(self.product_data.get('stock', 0))
            self.input_reorder.setValue(self.product_data.get('reorder_level', 10))
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
        tp = mrp * 0.85
        self.lbl_tp_preview.setText(f"Base TP (MRP - 15%): PKR {tp:,.2f}")

    def get_data(self) -> dict:
        return {
            'name': self.input_name.text().strip(),
            'mrp': self.input_mrp.value(),
            'stock': self.input_stock.value(),
            'reorder_level': self.input_reorder.value()
        }


class InventoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Title
        hdr_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        page_title = QLabel("Inventory & Stock Control")
        page_title.setProperty("class", "SectionHeader")
        page_title.setStyleSheet("font-size: 20px;")
        sub_title = QLabel("Manage pharmaceutical product master data, stock counts, and reorder levels")
        sub_title.setStyleSheet("color: #94A3B8; font-size: 12px;")
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
        self.input_search.setPlaceholderText("🔍 Filter products by name...")
        self.input_search.textChanged.connect(self.load_products)
        filter_layout.addWidget(self.input_search)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setProperty("class", "SecondaryBtn")
        btn_refresh.clicked.connect(self.load_products)
        filter_layout.addWidget(btn_refresh)

        main_layout.addWidget(filter_frame)

        # Products Table
        self.table_products = QTableWidget()
        self.table_products.setColumnCount(7)
        self.table_products.setHorizontalHeaderLabels([
            "#", "Product Name", "MRP (PKR)", "Base TP (MRP-15%)", "Stock Level", "Reorder Level", "Actions"
        ])
        self.table_products.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_products.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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
            self.table_products.setItem(row_idx, 3, QTableWidgetItem(f"{p['tp']:,.2f}"))

            stock_item = QTableWidgetItem(str(p['stock']))
            if p['stock'] <= p['reorder_level']:
                stock_item.setForeground(Qt.GlobalColor.red)
                stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_products.setItem(row_idx, 4, stock_item)

            self.table_products.setItem(row_idx, 5, QTableWidgetItem(str(p['reorder_level'])))

            # Actions Layout
            actions_widget = QWidget()
            act_layout = QHBoxLayout(actions_widget)
            act_layout.setContentsMargins(4, 2, 4, 2)
            act_layout.setSpacing(6)

            btn_edit = QPushButton("Edit")
            btn_edit.setProperty("class", "SecondaryBtn")
            btn_edit.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            btn_edit.clicked.connect(lambda _, prod=p: self.open_edit_dialog(prod))
            act_layout.addWidget(btn_edit)

            btn_del = QPushButton("Delete")
            btn_del.setProperty("class", "DangerBtn")
            btn_del.setStyleSheet("padding: 4px 8px; font-size: 11px;")
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
                add_product(data['name'], data['mrp'], data['stock'], data['reorder_level'])
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
                update_product(product_data['id'], data['name'], data['mrp'], data['stock'], data['reorder_level'])
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
