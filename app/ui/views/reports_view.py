"""
Business Intelligence & Strategic Reporting View Widget for NQS POS v2.0
Generates breakdown reports by Sales Rep, Geographical Area, and Product Performance with PDF exports.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QDateEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import QDate, Qt
from app.core.models import (
    get_sales_by_sales_rep, get_sales_by_area, get_sales_by_product
)
from app.core.pdf_report import generate_bi_report_pdf
import os
import subprocess


class ReportsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Title
        title_box = QVBoxLayout()
        page_title = QLabel("Business Intelligence & Strategic Reports")
        page_title.setProperty("class", "SectionHeader")
        page_title.setStyleSheet("font-size: 20px;")
        sub_title = QLabel("Analyze sales performance by Representative, Geographical Area, and Product Velocity")
        sub_title.setStyleSheet("color: #94A3B8; font-size: 12px;")
        title_box.addWidget(page_title)
        title_box.addWidget(sub_title)
        main_layout.addLayout(title_box)

        # Filter Card (Date Range + Presets + Export Button)
        filter_frame = QFrame()
        filter_frame.setProperty("class", "CardFrame")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(16)

        # From Date
        from_box = QVBoxLayout()
        lbl_from = QLabel("From Date")
        lbl_from.setStyleSheet("font-size: 11px; font-weight: bold; color: #94A3B8;")
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setDate(QDate.currentDate().addDays(-30)) # Default last 30 days
        from_box.addWidget(lbl_from)
        from_box.addWidget(self.date_from)
        filter_layout.addLayout(from_box)

        # To Date
        to_box = QVBoxLayout()
        lbl_to = QLabel("To Date")
        lbl_to.setStyleSheet("font-size: 11px; font-weight: bold; color: #94A3B8;")
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setDate(QDate.currentDate())
        to_box.addWidget(lbl_to)
        to_box.addWidget(self.date_to)
        filter_layout.addLayout(to_box)

        btn_apply = QPushButton("Apply Filter")
        btn_apply.setProperty("class", "PrimaryBtn")
        btn_apply.clicked.connect(self.load_all_reports)
        filter_layout.addWidget(btn_apply)

        # Presets
        btn_today = QPushButton("Today")
        btn_today.setProperty("class", "SecondaryBtn")
        btn_today.clicked.connect(self.set_preset_today)
        filter_layout.addWidget(btn_today)

        btn_month = QPushButton("This Month")
        btn_month.setProperty("class", "SecondaryBtn")
        btn_month.clicked.connect(self.set_preset_month)
        filter_layout.addWidget(btn_month)

        filter_layout.addStretch()

        # PDF Export Button
        btn_export = QPushButton("📄 Export Report PDF")
        btn_export.setProperty("class", "SuccessBtn")
        btn_export.clicked.connect(self.export_current_report_pdf)
        filter_layout.addWidget(btn_export)

        main_layout.addWidget(filter_frame)

        # Report Tabs
        self.tab_widget = QTabWidget()

        # Tab 1: Sales Reps
        self.tab_rep = QWidget()
        self.init_rep_tab()
        self.tab_widget.addTab(self.tab_rep, "👔 Sales by Sales Rep")

        # Tab 2: Areas
        self.tab_area = QWidget()
        self.init_area_tab()
        self.tab_widget.addTab(self.tab_area, "📍 Sales by Area")

        # Tab 3: Products
        self.tab_product = QWidget()
        self.init_product_tab()
        self.tab_widget.addTab(self.tab_product, "📦 Sales by Product")

        main_layout.addWidget(self.tab_widget)

        self.load_all_reports()

    def set_preset_today(self):
        today = QDate.currentDate()
        self.date_from.setDate(today)
        self.date_to.setDate(today)
        self.load_all_reports()

    def set_preset_month(self):
        today = QDate.currentDate()
        first_of_month = QDate(today.year(), today.month(), 1)
        self.date_from.setDate(first_of_month)
        self.date_to.setDate(today)
        self.load_all_reports()

    def get_date_strings(self):
        d_from = self.date_from.date().toString("yyyy-MM-dd")
        d_to = self.date_to.date().toString("yyyy-MM-dd")
        display_range = f"{self.date_from.date().toString('dd/MM/yyyy')} to {self.date_to.date().toString('dd/MM/yyyy')}"
        return d_from, d_to, display_range

    def init_rep_tab(self):
        layout = QVBoxLayout(self.tab_rep)
        layout.setContentsMargins(16, 16, 16, 16)
        self.table_rep = QTableWidget()
        self.table_rep.setColumnCount(4)
        self.table_rep.setHorizontalHeaderLabels(["#", "Sales Representative Name", "Total Invoices Generated", "Total Revenue (PKR)"])
        self.table_rep.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_rep.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_rep)

    def init_area_tab(self):
        layout = QVBoxLayout(self.tab_area)
        layout.setContentsMargins(16, 16, 16, 16)
        self.table_area = QTableWidget()
        self.table_area.setColumnCount(4)
        self.table_area.setHorizontalHeaderLabels(["#", "Geographical Area", "Total Invoices Generated", "Total Revenue (PKR)"])
        self.table_area.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_area.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_area)

    def init_product_tab(self):
        layout = QVBoxLayout(self.tab_product)
        layout.setContentsMargins(16, 16, 16, 16)
        self.table_product = QTableWidget()
        self.table_product.setColumnCount(4)
        self.table_product.setHorizontalHeaderLabels(["#", "Product Name", "Total Quantity Sold", "Total Revenue Generated (PKR)"])
        self.table_product.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_product.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_product)

    def load_all_reports(self):
        d_from, d_to, _ = self.get_date_strings()

        # 1. Sales Reps Report
        rep_rows = get_sales_by_sales_rep(d_from, d_to)
        self.table_rep.setRowCount(len(rep_rows))
        for idx, r in enumerate(rep_rows):
            self.table_rep.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
            self.table_rep.setItem(idx, 1, QTableWidgetItem(r['sales_rep_name']))
            self.table_rep.setItem(idx, 2, QTableWidgetItem(str(r['total_invoices'])))
            self.table_rep.setItem(idx, 3, QTableWidgetItem(f"{r['total_revenue']:,.2f}"))

        # 2. Area Report
        area_rows = get_sales_by_area(d_from, d_to)
        self.table_area.setRowCount(len(area_rows))
        for idx, r in enumerate(area_rows):
            self.table_area.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
            self.table_area.setItem(idx, 1, QTableWidgetItem(r['area_name']))
            self.table_area.setItem(idx, 2, QTableWidgetItem(str(r['total_invoices'])))
            self.table_area.setItem(idx, 3, QTableWidgetItem(f"{r['total_revenue']:,.2f}"))

        # 3. Product Report
        prod_rows = get_sales_by_product(d_from, d_to)
        self.table_product.setRowCount(len(prod_rows))
        for idx, r in enumerate(prod_rows):
            self.table_product.setItem(idx, 0, QTableWidgetItem(str(idx + 1)))
            self.table_product.setItem(idx, 1, QTableWidgetItem(r['product_name']))
            self.table_product.setItem(idx, 2, QTableWidgetItem(str(r['total_quantity_sold'])))
            self.table_product.setItem(idx, 3, QTableWidgetItem(f"{r['total_revenue']:,.2f}"))

    def export_current_report_pdf(self):
        d_from, d_to, display_range = self.get_date_strings()
        curr_tab = self.tab_widget.currentIndex()

        if curr_tab == 0:
            report_type = "rep"
            rows = get_sales_by_sales_rep(d_from, d_to)
        elif curr_tab == 1:
            report_type = "area"
            rows = get_sales_by_area(d_from, d_to)
        else:
            report_type = "product"
            rows = get_sales_by_product(d_from, d_to)

        if not rows:
            QMessageBox.warning(self, "No Data", "There is no data to export for the selected date range.")
            return

        try:
            pdf_path = generate_bi_report_pdf(report_type, display_range, rows)
            QMessageBox.information(self, "Report Exported", f"BI PDF Report exported successfully to:\n{pdf_path}")
            if os.name == 'nt':
                os.startfile(pdf_path)
            else:
                subprocess.Popen(['xdg-open', pdf_path])
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to generate report PDF: {e}")
