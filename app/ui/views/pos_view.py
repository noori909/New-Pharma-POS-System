"""
Sales & Invoicing Engine View Widget for NQS POS v2.0
Handles real-time product search, automatic TP calculation (MRP - 15%), customer tier discounts,
cart management, atomic perpetual invoice sequence generation, and PDF receipts.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QSpinBox, QMessageBox, QCompleter, QGroupBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel
from app.core.models import (
    get_all_customers, get_all_sales_reps, get_all_products,
    get_customer_by_id, preview_next_invoice_number, create_invoice
)
from app.core.pricing import calculate_tp, calculate_final_rate, calculate_line_total, compute_cart_summary
from app.core.pdf_receipt import generate_invoice_pdf
import os
import subprocess


class POSView(QWidget):
    invoice_created_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cart_items = []
        self.products_list = []
        self.customers_list = []
        self.sales_reps_list = []
        self.selected_customer = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Bar
        hdr_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        page_title = QLabel("Sales & Invoicing Engine")
        page_title.setProperty("class", "SectionHeader")
        page_title.setStyleSheet("font-size: 20px;")
        sub_title = QLabel("Process instant customer invoices with automated Trade Price & Tier Discounts")
        sub_title.setStyleSheet("color: #94A3B8; font-size: 12px;")
        title_box.addWidget(page_title)
        title_box.addWidget(sub_title)
        hdr_layout.addLayout(title_box)
        hdr_layout.addStretch()

        # Projected Invoice Number Box
        inv_no_box = QFrame()
        inv_no_box.setProperty("class", "CardFrame")
        inv_no_layout = QVBoxLayout(inv_no_box)
        inv_no_layout.setContentsMargins(12, 6, 12, 6)
        inv_no_lbl_title = QLabel("INVOICE NUMBER")
        inv_no_lbl_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #94A3B8;")
        self.lbl_next_inv_no = QLabel("NQS-100-DD-MM-YY")
        self.lbl_next_inv_no.setStyleSheet("font-size: 16px; font-weight: bold; color: #38BDF8;")
        inv_no_layout.addWidget(inv_no_lbl_title)
        inv_no_layout.addWidget(self.lbl_next_inv_no)
        hdr_layout.addWidget(inv_no_box)

        main_layout.addLayout(hdr_layout)

        # Top Control Row: Customer & Sales Rep Selectors
        selectors_frame = QFrame()
        selectors_frame.setProperty("class", "CardFrame")
        selectors_layout = QHBoxLayout(selectors_frame)
        selectors_layout.setContentsMargins(16, 14, 16, 14)
        selectors_layout.setSpacing(20)

        # Customer Select
        cust_box = QVBoxLayout()
        lbl_cust = QLabel("Select Customer *")
        lbl_cust.setStyleSheet("font-weight: bold; color: #94A3B8; font-size: 11px;")
        self.combo_customer = QComboBox()
        self.combo_customer.setPlaceholderText("Select Customer...")
        self.combo_customer.currentIndexChanged.connect(self.on_customer_changed)
        cust_box.addWidget(lbl_cust)
        cust_box.addWidget(self.combo_customer)
        selectors_layout.addLayout(cust_box, 3)

        # Customer Info Pill
        self.lbl_cust_info = QLabel("Area: - | Discount Tier: 0%")
        self.lbl_cust_info.setStyleSheet("color: #38BDF8; font-weight: bold; font-size: 12px; background: #0F172A; padding: 8px 12px; border-radius: 6px; border: 1px solid #334155;")
        selectors_layout.addWidget(self.lbl_cust_info, 2)

        # Sales Rep Select
        rep_box = QVBoxLayout()
        lbl_rep = QLabel("Select Sales Representative *")
        lbl_rep.setStyleSheet("font-weight: bold; color: #94A3B8; font-size: 11px;")
        self.combo_rep = QComboBox()
        self.combo_rep.setPlaceholderText("Select Sales Rep...")
        rep_box.addWidget(lbl_rep)
        rep_box.addWidget(self.combo_rep)
        selectors_layout.addLayout(rep_box, 3)

        main_layout.addWidget(selectors_frame)

        # Middle Row: Product Search & Add to Cart
        search_frame = QFrame()
        search_frame.setProperty("class", "CardFrame")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(16, 12, 16, 12)
        search_layout.setSpacing(14)

        prod_box = QVBoxLayout()
        lbl_prod = QLabel("Search Product by Name / Code")
        lbl_prod.setStyleSheet("font-weight: bold; color: #94A3B8; font-size: 11px;")
        self.combo_product = QComboBox()
        self.combo_product.setEditable(True)
        self.combo_product.setPlaceholderText("Type product name to search...")
        self.combo_product.currentIndexChanged.connect(self.on_product_selected)
        prod_box.addWidget(lbl_prod)
        prod_box.addWidget(self.combo_product)
        search_layout.addLayout(prod_box, 4)

        # MRP Display
        mrp_box = QVBoxLayout()
        lbl_mrp_t = QLabel("MRP (PKR)")
        lbl_mrp_t.setStyleSheet("font-weight: bold; color: #94A3B8; font-size: 11px;")
        self.lbl_prod_mrp = QLabel("0.00")
        self.lbl_prod_mrp.setStyleSheet("font-size: 14px; font-weight: bold; padding: 6px; color: #F8FAFC;")
        mrp_box.addWidget(lbl_mrp_t)
        mrp_box.addWidget(self.lbl_prod_mrp)
        search_layout.addLayout(mrp_box, 1)

        # Base TP Display
        tp_box = QVBoxLayout()
        lbl_tp_t = QLabel("Base TP (MRP - 15%)")
        lbl_tp_t.setStyleSheet("font-weight: bold; color: #94A3B8; font-size: 11px;")
        self.lbl_prod_tp = QLabel("0.00")
        self.lbl_prod_tp.setStyleSheet("font-size: 14px; font-weight: bold; color: #10B981; padding: 6px;")
        tp_box.addWidget(lbl_tp_t)
        tp_box.addWidget(self.lbl_prod_tp)
        search_layout.addLayout(tp_box, 1)

        # Stock Display
        stock_box = QVBoxLayout()
        lbl_stk_t = QLabel("In Stock")
        lbl_stk_t.setStyleSheet("font-weight: bold; color: #94A3B8; font-size: 11px;")
        self.lbl_prod_stock = QLabel("0")
        self.lbl_prod_stock.setStyleSheet("font-size: 14px; font-weight: bold; padding: 6px;")
        stock_box.addWidget(lbl_stk_t)
        stock_box.addWidget(self.lbl_prod_stock)
        search_layout.addLayout(stock_box, 1)

        # Qty Input
        qty_box = QVBoxLayout()
        lbl_qty = QLabel("Quantity")
        lbl_qty.setStyleSheet("font-weight: bold; color: #94A3B8; font-size: 11px;")
        self.spin_qty = QSpinBox()
        self.spin_qty.setRange(1, 99999)
        self.spin_qty.setValue(1)
        qty_box.addWidget(lbl_qty)
        qty_box.addWidget(self.spin_qty)
        search_layout.addLayout(qty_box, 1)

        # Add Button
        btn_add = QPushButton("+ Add to Invoice")
        btn_add.setProperty("class", "PrimaryBtn")
        btn_add.setStyleSheet("margin-top: 14px; padding: 9px 16px;")
        btn_add.clicked.connect(self.add_product_to_cart)
        search_layout.addWidget(btn_add, 1.5)

        main_layout.addWidget(search_frame)

        # Main Body: Cart Table (Left) + Totals Box & Submit (Right)
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        # Cart Table
        self.table_cart = QTableWidget()
        self.table_cart.setColumnCount(8)
        self.table_cart.setHorizontalHeaderLabels([
            "#", "Product Name", "MRP", "Base TP", "Disc %", "Final Rate", "Qty", "Total (PKR)"
        ])
        self.table_cart.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_cart.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        body_layout.addWidget(self.table_cart, 3)

        # Right Summary Box
        summary_frame = QFrame()
        summary_frame.setProperty("class", "CardFrame")
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(18, 18, 18, 18)
        summary_layout.setSpacing(14)

        summary_title = QLabel("INVOICE FINANCIAL SUMMARY")
        summary_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #94A3B8; border-bottom: 1px solid #334155; padding-bottom: 6px;")
        summary_layout.addWidget(summary_title)

        # Subtotal
        sub_layout = QHBoxLayout()
        lbl_sub_t = QLabel("Subtotal (Base TP):")
        self.lbl_subtotal = QLabel("PKR 0.00")
        self.lbl_subtotal.setStyleSheet("font-weight: bold;")
        sub_layout.addWidget(lbl_sub_t)
        sub_layout.addStretch()
        sub_layout.addWidget(self.lbl_subtotal)
        summary_layout.addLayout(sub_layout)

        # Total Discount Savings
        disc_layout = QHBoxLayout()
        lbl_disc_t = QLabel("Customer Tier Discount:")
        self.lbl_discount = QLabel("- PKR 0.00")
        self.lbl_discount.setStyleSheet("font-weight: bold; color: #10B981;")
        disc_layout.addWidget(lbl_disc_t)
        disc_layout.addStretch()
        disc_layout.addWidget(self.lbl_discount)
        summary_layout.addLayout(disc_layout)

        # Line Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #334155;")
        summary_layout.addWidget(sep)

        # Grand Total
        gt_layout = QHBoxLayout()
        lbl_gt_t = QLabel("NET AMOUNT DUE:")
        lbl_gt_t.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.lbl_grand_total = QLabel("PKR 0.00")
        self.lbl_grand_total.setStyleSheet("font-size: 20px; font-weight: 800; color: #38BDF8;")
        gt_layout.addWidget(lbl_gt_t)
        gt_layout.addStretch()
        gt_layout.addWidget(self.lbl_grand_total)
        summary_layout.addLayout(gt_layout)

        summary_layout.addStretch()

        # Submit & Print Invoice Button
        self.btn_save_invoice = QPushButton("💾 Save Invoice & Print PDF")
        self.btn_save_invoice.setProperty("class", "SuccessBtn")
        self.btn_save_invoice.setStyleSheet("font-size: 14px; padding: 12px;")
        self.btn_save_invoice.clicked.connect(self.save_and_print_invoice)
        summary_layout.addWidget(self.btn_save_invoice)

        btn_clear = QPushButton("Clear Cart")
        btn_clear.setProperty("class", "SecondaryBtn")
        btn_clear.clicked.connect(self.clear_cart)
        summary_layout.addWidget(btn_clear)

        body_layout.addWidget(summary_frame, 1.3)

        main_layout.addLayout(body_layout)

        # Initial Setup
        self.reload_master_data()

    def reload_master_data(self):
        # Update projected invoice number
        self.lbl_next_inv_no.setText(preview_next_invoice_number())

        # Load Customers
        self.customers_list = get_all_customers()
        self.combo_customer.blockSignals(True)
        self.combo_customer.clear()
        self.combo_customer.addItem("-- Select Customer --", None)
        for c in self.customers_list:
            display_text = f"{c['name']} ({c.get('area_name') or 'No Area'}) [{c['discount_tier']:.0f}% Disc]"
            self.combo_customer.addItem(display_text, c['id'])
        self.combo_customer.blockSignals(False)

        # Load Sales Reps
        self.sales_reps_list = get_all_sales_reps()
        self.combo_rep.blockSignals(True)
        self.combo_rep.clear()
        self.combo_rep.addItem("-- Select Sales Rep --", None)
        for r in self.sales_reps_list:
            self.combo_rep.addItem(r['name'], r['id'])
        self.combo_rep.blockSignals(False)

        # Load Products
        self.products_list = get_all_products()
        self.combo_product.blockSignals(True)
        self.combo_product.clear()
        self.combo_product.addItem("-- Select / Type Product --", None)
        for p in self.products_list:
            self.combo_product.addItem(f"{p['name']} (MRP: {p['mrp']:.2f} | Stock: {p['stock']})", p['id'])
        self.combo_product.blockSignals(False)

    def on_customer_changed(self):
        cust_id = self.combo_customer.currentData()
        if not cust_id:
            self.selected_customer = None
            self.lbl_cust_info.setText("Area: - | Discount Tier: 0%")
            self.update_cart_calculations()
            return

        cust = get_customer_by_id(cust_id)
        if cust:
            self.selected_customer = cust
            area = cust.get('area_name') or 'Unassigned'
            disc = cust.get('discount_tier', 0.0)
            self.lbl_cust_info.setText(f"Area: {area} | Discount Tier: {disc:.1f}%")
            self.update_cart_calculations()

    def on_product_selected(self):
        prod_id = self.combo_product.currentData()
        if not prod_id:
            self.lbl_prod_mrp.setText("0.00")
            self.lbl_prod_tp.setText("0.00")
            self.lbl_prod_stock.setText("0")
            return

        for p in self.products_list:
            if p['id'] == prod_id:
                self.lbl_prod_mrp.setText(f"{p['mrp']:,.2f}")
                self.lbl_prod_tp.setText(f"{p['tp']:,.2f}")
                self.lbl_prod_stock.setText(str(p['stock']))

                if p['stock'] <= 0:
                    self.lbl_prod_stock.setStyleSheet("font-size: 14px; font-weight: bold; color: #EF4444;")
                elif p['stock'] <= p['reorder_level']:
                    self.lbl_prod_stock.setStyleSheet("font-size: 14px; font-weight: bold; color: #F59E0B;")
                else:
                    self.lbl_prod_stock.setStyleSheet("font-size: 14px; font-weight: bold; color: #10B981;")
                break

    def add_product_to_cart(self):
        prod_id = self.combo_product.currentData()
        if not prod_id:
            QMessageBox.warning(self, "Product Selection Required", "Please select a product to add.")
            return

        qty = self.spin_qty.value()
        if qty <= 0:
            return

        target_prod = None
        for p in self.products_list:
            if p['id'] == prod_id:
                target_prod = p
                break

        if not target_prod:
            return

        # Check stock
        existing_qty_in_cart = sum(item['quantity'] for item in self.cart_items if item['product_id'] == prod_id)
        if (existing_qty_in_cart + qty) > target_prod['stock']:
            QMessageBox.warning(
                self, "Insufficient Stock",
                f"Cannot add {qty} units of '{target_prod['name']}'. Available stock is {target_prod['stock']}."
            )
            return

        # Check if item already in cart
        found = False
        for item in self.cart_items:
            if item['product_id'] == prod_id:
                item['quantity'] += qty
                found = True
                break

        if not found:
            self.cart_items.append({
                'product_id': target_prod['id'],
                'name': target_prod['name'],
                'mrp': target_prod['mrp'],
                'tp': target_prod['tp'],
                'quantity': qty
            })

        self.update_cart_calculations()

    def update_cart_calculations(self):
        disc_tier = self.selected_customer.get('discount_tier', 0.0) if self.selected_customer else 0.0

        processed_cart = []
        for idx, item in enumerate(self.cart_items, start=1):
            mrp = item['mrp']
            tp = calculate_tp(mrp)
            final_rate = calculate_final_rate(tp, disc_tier)
            total = calculate_line_total(final_rate, item['quantity'])

            processed_cart.append({
                'product_id': item['product_id'],
                'name': item['name'],
                'mrp': mrp,
                'tp': tp,
                'discount_percent': disc_tier,
                'final_rate': final_rate,
                'quantity': item['quantity'],
                'total': total
            })

        # Render Table
        self.table_cart.setRowCount(len(processed_cart))
        for row_idx, item in enumerate(processed_cart):
            self.table_cart.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.table_cart.setItem(row_idx, 1, QTableWidgetItem(item['name']))
            self.table_cart.setItem(row_idx, 2, QTableWidgetItem(f"{item['mrp']:,.2f}"))
            self.table_cart.setItem(row_idx, 3, QTableWidgetItem(f"{item['tp']:,.2f}"))
            self.table_cart.setItem(row_idx, 4, QTableWidgetItem(f"{item['discount_percent']:.1f}%"))
            self.table_cart.setItem(row_idx, 5, QTableWidgetItem(f"{item['final_rate']:,.2f}"))

            # Qty SpinBox
            spin = QSpinBox()
            spin.setRange(1, 99999)
            spin.setValue(item['quantity'])
            spin.valueChanged.connect(lambda val, idx=row_idx: self.on_cart_qty_changed(idx, val))
            self.table_cart.setCellWidget(row_idx, 6, spin)

            self.table_cart.setItem(row_idx, 7, QTableWidgetItem(f"{item['total']:,.2f}"))

        # Compute Summary
        summary = compute_cart_summary(processed_cart)
        self.lbl_subtotal.setText(f"PKR {summary['subtotal']:,.2f}")
        self.lbl_discount.setText(f"- PKR {summary['discount_amount']:,.2f}")
        self.lbl_grand_total.setText(f"PKR {summary['grand_total']:,.2f}")

    def on_cart_qty_changed(self, index: int, new_qty: int):
        if 0 <= index < len(self.cart_items):
            self.cart_items[index]['quantity'] = new_qty
            self.update_cart_calculations()

    def clear_cart(self):
        self.cart_items.clear()
        self.update_cart_calculations()

    def save_and_print_invoice(self):
        cust_id = self.combo_customer.currentData()
        rep_id = self.combo_rep.currentData()

        if not cust_id:
            QMessageBox.warning(self, "Customer Required", "Please select a Customer for this invoice.")
            return

        if not rep_id:
            QMessageBox.warning(self, "Sales Rep Required", "Please select a Sales Representative.")
            return

        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Cannot create invoice with an empty cart.")
            return

        try:
            invoice_dict = create_invoice(cust_id, rep_id, self.cart_items)
            
            # Generate PDF
            pdf_path = generate_invoice_pdf(invoice_dict)

            # Success Popup
            QMessageBox.information(
                self, "Invoice Created",
                f"Invoice '{invoice_dict['invoice_number']}' processed successfully!\nGrand Total: PKR {invoice_dict['grand_total']:,.2f}"
            )

            # Open PDF automatically
            if os.name == 'nt':
                os.startfile(pdf_path)
            else:
                subprocess.Popen(['xdg-open', pdf_path])

            # Clear cart & reload
            self.clear_cart()
            self.reload_master_data()
            self.invoice_created_signal.emit()

        except Exception as e:
            QMessageBox.critical(self, "Error Creating Invoice", f"Failed to save invoice: {e}")
