"""
Dashboard View Widget for NQS POS v2.0
Displays real-time KPIs, prominent Low Stock Alerts table, and quick restock dialog.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QMessageBox, QDialog, QFormLayout, QLineEdit, QSpinBox,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.ui.components.stat_card import StatCard
from app.core.models import (
    get_dashboard_summary, get_low_stock_products,
    update_product_stock, get_invoice_by_id, get_product_by_id
)
from app.core.pdf_receipt import generate_invoice_pdf
import os
import subprocess


class QuickRestockDialog(QDialog):
    def __init__(self, product_id: int, product_name: str, current_stock: int, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle("⚠️ Quick Restock - Low Stock Alert")
        self.setFixedWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(14)

        # Product Name (Read-Only)
        self.lbl_prod_name = QLineEdit(product_name)
        self.lbl_prod_name.setReadOnly(True)
        self.lbl_prod_name.setStyleSheet("background-color: #0F172A; color: #38BDF8; font-weight: bold;")

        # Current Stock (Read-Only)
        self.lbl_curr_stock = QLineEdit(str(current_stock))
        self.lbl_curr_stock.setReadOnly(True)
        self.lbl_curr_stock.setStyleSheet("background-color: #0F172A; color: #EF4444; font-weight: bold;")

        # New Stock Input Field (Total Stock After Restock)
        self.spin_new_stock = QSpinBox()
        self.spin_new_stock.setRange(0, 999999)
        self.spin_new_stock.setValue(current_stock + 50)

        form.addRow("Product Name:", self.lbl_prod_name)
        form.addRow("Current Stock:", self.lbl_curr_stock)
        form.addRow("New Stock Level *:", self.spin_new_stock)

        layout.addLayout(form)

        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setProperty("class", "SecondaryBtn")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_save = QPushButton("💾 Save Stock")
        btn_save.setProperty("class", "SuccessBtn")
        btn_save.clicked.connect(self.accept)
        btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    def get_new_stock(self) -> int:
        return self.spin_new_stock.value()


class DashboardView(QWidget):
    navigate_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header Title & Quick Actions
        hdr_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        page_title = QLabel("Dashboard Overview")
        page_title.setProperty("class", "SectionHeader")
        page_title.setStyleSheet("font-size: 20px;")
        sub_title = QLabel("Real-time warehouse operational metrics and low-stock alerts")
        sub_title.setStyleSheet("color: #94A3B8; font-size: 12px;")
        title_box.addWidget(page_title)
        title_box.addWidget(sub_title)
        hdr_layout.addLayout(title_box)
        hdr_layout.addStretch()

        btn_new_sale = QPushButton("+ New Sale")
        btn_new_sale.setProperty("class", "PrimaryBtn")
        btn_new_sale.clicked.connect(lambda: self.navigate_signal.emit("pos"))
        hdr_layout.addWidget(btn_new_sale)

        btn_restock = QPushButton("+ Add Stock")
        btn_restock.setProperty("class", "SecondaryBtn")
        btn_restock.clicked.connect(lambda: self.navigate_signal.emit("inventory"))
        hdr_layout.addWidget(btn_restock)

        main_layout.addLayout(hdr_layout)

        # Top KPI Stat Cards Grid
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(16)

        self.card_revenue = StatCard("Today's Revenue", "PKR 0.00", "Total collected today", "#2563EB")
        self.card_invoices = StatCard("Today's Invoices", "0", "Invoices processed", "#10B981")
        self.card_products = StatCard("Active Products", "0", "Total items in master data", "#38BDF8")
        self.card_low_stock = StatCard("Low Stock Alerts", "0", "Items below reorder level", "#EF4444")

        kpi_layout.addWidget(self.card_revenue)
        kpi_layout.addWidget(self.card_invoices)
        kpi_layout.addWidget(self.card_products)
        kpi_layout.addWidget(self.card_low_stock)

        main_layout.addLayout(kpi_layout)

        # Middle Area: Low Stock Alert Table & Recent Invoices
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        # Left Column: Low Stock Alerts
        low_stock_box = QFrame()
        low_stock_box.setProperty("class", "CardFrame")
        low_stock_inner = QVBoxLayout(low_stock_box)
        low_stock_inner.setContentsMargins(16, 16, 16, 16)
        low_stock_inner.setSpacing(12)

        ls_header = QHBoxLayout()
        ls_title = QLabel("🚨 Low Stock Inventory Alerts")
        ls_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #EF4444;")
        ls_header.addWidget(ls_title)
        ls_header.addStretch()

        btn_refresh_ls = QPushButton("Refresh")
        btn_refresh_ls.setProperty("class", "SecondaryBtn")
        btn_refresh_ls.setStyleSheet("padding: 4px 10px; font-size: 11px;")
        btn_refresh_ls.clicked.connect(self.load_data)
        ls_header.addWidget(btn_refresh_ls)
        low_stock_inner.addLayout(ls_header)

        self.table_low_stock = QTableWidget()
        self.table_low_stock.setColumnCount(5)
        self.table_low_stock.setHorizontalHeaderLabels(["Product Name", "MRP (PKR)", "Base TP", "Stock", "Action"])
        self.table_low_stock.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_low_stock.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        low_stock_inner.addWidget(self.table_low_stock)

        content_layout.addWidget(low_stock_box, 3)

        # Right Column: Recent Invoices
        recent_box = QFrame()
        recent_box.setProperty("class", "CardFrame")
        recent_inner = QVBoxLayout(recent_box)
        recent_inner.setContentsMargins(16, 16, 16, 16)
        recent_inner.setSpacing(12)

        rc_title = QLabel("🧾 Recent Sales Invoices")
        rc_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #38BDF8;")
        recent_inner.addWidget(rc_title)

        self.table_recent_invoices = QTableWidget()
        self.table_recent_invoices.setColumnCount(4)
        self.table_recent_invoices.setHorizontalHeaderLabels(["Invoice #", "Customer", "Total", "PDF"])
        self.table_recent_invoices.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_recent_invoices.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        recent_inner.addWidget(self.table_recent_invoices)

        content_layout.addWidget(recent_box, 2)

        main_layout.addLayout(content_layout)

        # Initial Load
        self.load_data()

    def load_data(self):
        summary = get_dashboard_summary()

        # Update Stat Cards
        self.card_revenue.set_value(f"PKR {summary['today_revenue']:,.2f}")
        self.card_invoices.set_value(str(summary['today_invoices_count']))
        self.card_products.set_value(str(summary['total_products_count']))
        self.card_low_stock.set_value(str(summary['low_stock_count']))

        # Load Low Stock Table
        low_stock_items = get_low_stock_products()
        self.table_low_stock.setRowCount(len(low_stock_items))

        for row_idx, item in enumerate(low_stock_items):
            self.table_low_stock.setItem(row_idx, 0, QTableWidgetItem(f"⚠️ {item['name']}"))
            self.table_low_stock.setItem(row_idx, 1, QTableWidgetItem(f"{item['mrp']:,.2f}"))
            self.table_low_stock.setItem(row_idx, 2, QTableWidgetItem(f"{item['tp']:,.2f}"))

            stock_item = QTableWidgetItem(f"{item['stock']} / {item['reorder_level']}")
            stock_item.setForeground(Qt.GlobalColor.red)
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_low_stock.setItem(row_idx, 3, stock_item)

            # Red warning button for Quick Restock
            btn_restock = QPushButton("🔴 Quick Restock")
            btn_restock.setProperty("class", "DangerBtn")
            btn_restock.setStyleSheet("padding: 4px 10px; font-size: 11px; font-weight: bold;")
            btn_restock.clicked.connect(lambda _, p_id=item['id'], p_name=item['name'], curr_stk=item['stock']: self.open_quick_restock_dialog(p_id, p_name, curr_stk))
            self.table_low_stock.setCellWidget(row_idx, 4, btn_restock)

        # Load Recent Invoices Table
        recent_invs = summary['recent_invoices']
        self.table_recent_invoices.setRowCount(len(recent_invs))

        for row_idx, inv in enumerate(recent_invs):
            self.table_recent_invoices.setItem(row_idx, 0, QTableWidgetItem(inv['invoice_number']))
            self.table_recent_invoices.setItem(row_idx, 1, QTableWidgetItem(inv['customer_name']))
            self.table_recent_invoices.setItem(row_idx, 2, QTableWidgetItem(f"{inv['grand_total']:,.2f}"))

            btn_pdf = QPushButton("PDF")
            btn_pdf.setProperty("class", "SecondaryBtn")
            btn_pdf.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn_pdf.clicked.connect(lambda _, i_id=inv['id']: self.print_receipt_by_id(i_id))
            self.table_recent_invoices.setCellWidget(row_idx, 3, btn_pdf)

    def open_quick_restock_dialog(self, product_id: int, product_name: str, current_stock: int):
        dlg = QuickRestockDialog(product_id, product_name, current_stock, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_stock = dlg.get_new_stock()
            try:
                update_product_stock(product_id, new_stock)
                QMessageBox.information(self, "Stock Saved", f"Updated stock for '{product_name}' to {new_stock} units.")
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update stock: {e}")

    def print_receipt_by_id(self, invoice_id: int):
        inv_data = get_invoice_by_id(invoice_id)
        if not inv_data:
            QMessageBox.warning(self, "Error", "Invoice not found.")
            return

        try:
            pdf_path = generate_invoice_pdf(inv_data)
            if os.name == 'nt':
                os.startfile(pdf_path)
            else:
                subprocess.Popen(['xdg-open', pdf_path])
        except Exception as e:
            QMessageBox.critical(self, "PDF Error", f"Failed to generate PDF receipt: {e}")
