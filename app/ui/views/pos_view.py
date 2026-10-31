"""
Sales & Invoicing Engine View Widget for New Quetta Surgical and Medicine Distribution (NQS POS v2.0)
Handles product search, selectable Trade Price (TP = MRP - 15%) vs MRP, customizable discount percentages,
Cash vs Credit payment mode selection, cart management, atomic perpetual invoice sequence generation, and PDF receipts.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QComboBox,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QSpinBox, QDoubleSpinBox, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
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
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(10)

        # Header Bar
        hdr_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        page_title = QLabel("Sales & Invoicing Engine")
        page_title.setProperty("class", "SectionHeader")
        page_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        sub_title = QLabel("New Quetta Surgical and Medicine Distribution • Instant Invoicing & Billing")
        sub_title.setProperty("class", "SubHeader")
        sub_title.setStyleSheet("font-size: 12px;")
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
        inv_no_lbl_title.setProperty("class", "CardTitle")
        inv_no_lbl_title.setStyleSheet("font-size: 10px; font-weight: bold;")
        self.lbl_next_inv_no = QLabel("NQS-001-DD-MM-YY")
        self.lbl_next_inv_no.setStyleSheet("font-size: 15px; font-weight: bold; color: #0284C7;")
        inv_no_layout.addWidget(inv_no_lbl_title)
        inv_no_layout.addWidget(self.lbl_next_inv_no)
        hdr_layout.addWidget(inv_no_box)

        main_layout.addLayout(hdr_layout)

        # Top Control Row: Customer, Payment Mode & Sales Rep Selectors
        selectors_frame = QFrame()
        selectors_frame.setProperty("class", "CardFrame")
        selectors_layout = QHBoxLayout(selectors_frame)
        selectors_layout.setContentsMargins(14, 8, 14, 8)
        selectors_layout.setSpacing(12)

        # Customer Select
        cust_box = QVBoxLayout()
        lbl_cust = QLabel("Select Customer *")
        lbl_cust.setProperty("class", "FieldLabel")
        self.combo_customer = QComboBox()
        self.combo_customer.setPlaceholderText("Select Customer...")
        self.combo_customer.currentIndexChanged.connect(self.on_customer_changed)
        cust_box.addWidget(lbl_cust)
        cust_box.addWidget(self.combo_customer)
        selectors_layout.addLayout(cust_box, 3)

        # Customer Info Pill
        self.lbl_cust_info = QLabel("Area: - | Discount: 0%")
        self.lbl_cust_info.setStyleSheet("font-weight: bold; font-size: 12px; color: #0284C7; padding: 6px 10px; border-radius: 6px; border: 1px solid #CBD5E1;")
        selectors_layout.addWidget(self.lbl_cust_info, 2)

        # Payment Mode Select (Cash / Credit)
        pay_box = QVBoxLayout()
        lbl_pay = QLabel("Payment Mode *")
        lbl_pay.setProperty("class", "FieldLabel")
        self.combo_payment_mode = QComboBox()
        self.combo_payment_mode.addItem("Cash", "Cash")
        self.combo_payment_mode.addItem("Credit", "Credit")
        self.combo_payment_mode.currentIndexChanged.connect(self.on_payment_mode_changed)
        pay_box.addWidget(lbl_pay)
        pay_box.addWidget(self.combo_payment_mode)
        selectors_layout.addLayout(pay_box, 2)

        # Sales Rep Select
        rep_box = QVBoxLayout()
        lbl_rep = QLabel("Select Sales Representative *")
        lbl_rep.setProperty("class", "FieldLabel")
        self.combo_rep = QComboBox()
        self.combo_rep.setPlaceholderText("Select Sales Rep...")
        rep_box.addWidget(lbl_rep)
        rep_box.addWidget(self.combo_rep)
        selectors_layout.addLayout(rep_box, 3)

        main_layout.addWidget(selectors_frame)

        # Middle Section: Product Search, Selectable TP/MRP, Discount %, Qty & Add to Cart
        # Structured in 2 clean, spacious rows to eliminate congestion and guarantee readable inputs
        search_frame = QFrame()
        search_frame.setProperty("class", "CardFrame")
        search_vbox = QVBoxLayout(search_frame)
        search_vbox.setContentsMargins(14, 10, 14, 10)
        search_vbox.setSpacing(8)

        # Row 1: Product Selection & Clear Rate Type Dropdown
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(14)

        prod_box = QVBoxLayout()
        lbl_prod = QLabel("Search Product by Name")
        lbl_prod.setProperty("class", "FieldLabel")
        self.combo_product = QComboBox()
        self.combo_product.setEditable(True)
        self.combo_product.setPlaceholderText("Type product name to search catalog...")
        self.combo_product.currentIndexChanged.connect(self.on_product_selected)
        prod_box.addWidget(lbl_prod)
        prod_box.addWidget(self.combo_product)
        row1_layout.addLayout(prod_box, 4)

        pricing_box = QVBoxLayout()
        lbl_pricing_rule = QLabel("Rate Type (Trade Price vs Retail MRP)")
        lbl_pricing_rule.setProperty("class", "FieldLabel")
        self.combo_pricing_rule = QComboBox()
        self.combo_pricing_rule.setMinimumWidth(240)
        self.combo_pricing_rule.addItem("Trade Price (TP = MRP - 15%)", True)
        self.combo_pricing_rule.addItem("Retail Price (Sold at MRP)", False)
        self.combo_pricing_rule.currentIndexChanged.connect(self.on_pricing_rule_changed)
        pricing_box.addWidget(lbl_pricing_rule)
        pricing_box.addWidget(self.combo_pricing_rule)
        row1_layout.addLayout(pricing_box, 2)

        search_vbox.addLayout(row1_layout)

        # Row 2: Financial Metrics, Generous SpinBoxes & Add to Cart Button
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(12)

        # MRP Display
        mrp_box = QVBoxLayout()
        lbl_mrp_t = QLabel("MRP (PKR)")
        lbl_mrp_t.setProperty("class", "FieldLabel")
        self.lbl_prod_mrp = QLabel("0.00")
        self.lbl_prod_mrp.setProperty("class", "ValueLabel")
        self.lbl_prod_mrp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_prod_mrp.setStyleSheet("font-size: 13px; font-weight: bold; padding: 5px; border: 1px solid #475569; border-radius: 6px; min-width: 85px;")
        mrp_box.addWidget(lbl_mrp_t)
        mrp_box.addWidget(self.lbl_prod_mrp)
        row2_layout.addLayout(mrp_box)

        # Base Rate Display
        base_rate_box = QVBoxLayout()
        lbl_base_rate_t = QLabel("Base Rate (PKR)")
        lbl_base_rate_t.setProperty("class", "FieldLabel")
        self.lbl_prod_base_price = QLabel("0.00")
        self.lbl_prod_base_price.setProperty("class", "ValueLabel")
        self.lbl_prod_base_price.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_prod_base_price.setStyleSheet("font-size: 13px; font-weight: bold; color: #16A34A; padding: 5px; border: 1px solid #475569; border-radius: 6px; min-width: 95px;")
        base_rate_box.addWidget(lbl_base_rate_t)
        base_rate_box.addWidget(self.lbl_prod_base_price)
        row2_layout.addLayout(base_rate_box)

        # Discount % Input (Spacious with 105px width)
        disc_box = QVBoxLayout()
        lbl_disc_input = QLabel("Disc %")
        lbl_disc_input.setProperty("class", "FieldLabel")
        self.spin_discount = QDoubleSpinBox()
        self.spin_discount.setRange(0.0, 100.0)
        self.spin_discount.setDecimals(1)
        self.spin_discount.setSingleStep(0.5)
        self.spin_discount.setSuffix("%")
        self.spin_discount.setValue(0.0)
        self.spin_discount.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_discount.setMinimumWidth(105)
        self.spin_discount.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.spin_discount.valueChanged.connect(self.update_add_preview_rate)
        disc_box.addWidget(lbl_disc_input)
        disc_box.addWidget(self.spin_discount)
        row2_layout.addLayout(disc_box)

        # Stock Display
        stock_box = QVBoxLayout()
        lbl_stk_t = QLabel("Stock")
        lbl_stk_t.setProperty("class", "FieldLabel")
        self.lbl_prod_stock = QLabel("0")
        self.lbl_prod_stock.setProperty("class", "ValueLabel")
        self.lbl_prod_stock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_prod_stock.setStyleSheet("font-size: 13px; font-weight: bold; padding: 5px; border: 1px solid #475569; border-radius: 6px; min-width: 75px;")
        stock_box.addWidget(lbl_stk_t)
        stock_box.addWidget(self.lbl_prod_stock)
        row2_layout.addLayout(stock_box)

        # Qty Input (Spacious with 100px width)
        qty_box = QVBoxLayout()
        lbl_qty = QLabel("Quantity")
        lbl_qty.setProperty("class", "FieldLabel")
        self.spin_qty = QSpinBox()
        self.spin_qty.setRange(1, 99999)
        self.spin_qty.setValue(1)
        self.spin_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_qty.setMinimumWidth(100)
        self.spin_qty.setStyleSheet("font-size: 13px; font-weight: bold;")
        qty_box.addWidget(lbl_qty)
        qty_box.addWidget(self.spin_qty)
        row2_layout.addLayout(qty_box)

        # Add Button
        btn_add_box = QVBoxLayout()
        lbl_add_spacer = QLabel(" ")
        lbl_add_spacer.setProperty("class", "FieldLabel")
        btn_add = QPushButton("+ Add to Cart")
        btn_add.setProperty("class", "PrimaryBtn")
        btn_add.setMinimumWidth(140)
        btn_add.setFixedHeight(34)
        btn_add.clicked.connect(self.add_product_to_cart)
        btn_add_box.addWidget(lbl_add_spacer)
        btn_add_box.addWidget(btn_add)
        row2_layout.addLayout(btn_add_box)

        row2_layout.addStretch()
        search_vbox.addLayout(row2_layout)

        main_layout.addWidget(search_frame)

        # Main Body: Cart Table (Left) + Totals Box & Submit (Right)
        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        # Cart Table with comfortable, un-congested column widths and row height
        self.table_cart = QTableWidget()
        self.table_cart.setColumnCount(10)
        self.table_cart.setHorizontalHeaderLabels([
            "#", "Product Name", "MRP", "Rate Type", "Base Price", "Disc %", "Final Rate", "Qty", "Total (PKR)", "Action"
        ])
        self.table_cart.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_cart.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_cart.verticalHeader().setDefaultSectionSize(36)

        # Explicit widths to guarantee zero congestion inside cells
        self.table_cart.setColumnWidth(0, 38)   # #
        # Col 1: Product Name is Stretch
        self.table_cart.setColumnWidth(2, 85)   # MRP
        self.table_cart.setColumnWidth(3, 105)  # Rate Type
        self.table_cart.setColumnWidth(4, 85)   # Base Price
        self.table_cart.setColumnWidth(5, 85)   # Disc %
        self.table_cart.setColumnWidth(6, 85)   # Final Rate
        self.table_cart.setColumnWidth(7, 80)   # Qty
        self.table_cart.setColumnWidth(8, 105)  # Total (PKR)
        self.table_cart.setColumnWidth(9, 75)   # Action

        body_layout.addWidget(self.table_cart, 3)

        # Right Summary Box
        summary_frame = QFrame()
        summary_frame.setProperty("class", "CardFrame")
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(14, 14, 14, 14)
        summary_layout.setSpacing(10)

        summary_title = QLabel("INVOICE FINANCIAL SUMMARY")
        summary_title.setProperty("class", "CardTitle")
        summary_title.setStyleSheet("font-weight: bold; font-size: 13px; padding-bottom: 6px;")
        summary_layout.addWidget(summary_title)

        # Payment Mode Badge
        self.lbl_payment_display = QLabel("Payment Mode: CASH")
        self.lbl_payment_display.setStyleSheet("font-weight: bold; font-size: 12px; color: #16A34A; padding: 4px 8px; border-radius: 4px; border: 1px solid #CBD5E1;")
        summary_layout.addWidget(self.lbl_payment_display)

        # Subtotal
        sub_layout = QHBoxLayout()
        lbl_sub_t = QLabel("Gross Amount (Subtotal):")
        lbl_sub_t.setProperty("class", "SubHeader")
        self.lbl_subtotal = QLabel("PKR 0.00")
        self.lbl_subtotal.setProperty("class", "ValueLabel")
        self.lbl_subtotal.setStyleSheet("font-weight: bold;")
        sub_layout.addWidget(lbl_sub_t)
        sub_layout.addStretch()
        sub_layout.addWidget(self.lbl_subtotal)
        summary_layout.addLayout(sub_layout)

        # Total Discount Savings
        disc_layout = QHBoxLayout()
        lbl_disc_t = QLabel("Total Discount Amount:")
        lbl_disc_t.setProperty("class", "SubHeader")
        self.lbl_discount = QLabel("- PKR 0.00")
        self.lbl_discount.setStyleSheet("font-weight: bold; color: #16A34A;")
        disc_layout.addWidget(lbl_disc_t)
        disc_layout.addStretch()
        disc_layout.addWidget(self.lbl_discount)
        summary_layout.addLayout(disc_layout)

        # Line Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #CBD5E1;")
        summary_layout.addWidget(sep)

        # Grand Total
        gt_layout = QHBoxLayout()
        lbl_gt_t = QLabel("NET AMOUNT DUE:")
        lbl_gt_t.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.lbl_grand_total = QLabel("PKR 0.00")
        self.lbl_grand_total.setStyleSheet("font-size: 19px; font-weight: 800; color: #0284C7;")
        gt_layout.addWidget(lbl_gt_t)
        gt_layout.addStretch()
        gt_layout.addWidget(self.lbl_grand_total)
        summary_layout.addLayout(gt_layout)

        summary_layout.addStretch()

        # Submit & Print Invoice Button (Zero Emojis)
        self.btn_save_invoice = QPushButton("Save Invoice & Print PDF")
        self.btn_save_invoice.setProperty("class", "SuccessBtn")
        self.btn_save_invoice.setStyleSheet("font-size: 13px; font-weight: bold; padding: 11px;")
        self.btn_save_invoice.clicked.connect(self.save_and_print_invoice)
        summary_layout.addWidget(self.btn_save_invoice)

        btn_clear = QPushButton("Clear Cart")
        btn_clear.setProperty("class", "SecondaryBtn")
        btn_clear.clicked.connect(self.clear_cart)
        summary_layout.addWidget(btn_clear)

        body_layout.addWidget(summary_frame, 1)

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
            display_text = f"{c['name']} ({c.get('area_name') or 'No Area'}) [{c['discount_tier']:.1f}% Disc]"
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
            rule_str = "TP" if p.get('has_tp', True) else "MRP"
            self.combo_product.addItem(f"{p['name']} (MRP: {p['mrp']:.2f} | {rule_str} | Stock: {p['stock']})", p['id'])
        self.combo_product.blockSignals(False)

    def on_customer_changed(self):
        cust_id = self.combo_customer.currentData()
        if not cust_id:
            self.selected_customer = None
            self.lbl_cust_info.setText("Area: - | Discount: 0.0%")
            self.spin_discount.setValue(0.0)
            self.update_cart_calculations()
            return

        cust = get_customer_by_id(cust_id)
        if cust:
            self.selected_customer = cust
            area = cust.get('area_name') or 'General'
            disc = float(cust.get('discount_tier', 0.0))
            self.lbl_cust_info.setText(f"Area: {area} | Customer Discount: {disc:.1f}%")
            self.spin_discount.setValue(disc)
            self.update_cart_calculations()

    def on_payment_mode_changed(self):
        mode = self.combo_payment_mode.currentText().upper()
        if mode == "CASH":
            self.lbl_payment_display.setText("Payment Mode: CASH")
            self.lbl_payment_display.setStyleSheet("font-weight: bold; font-size: 12px; color: #16A34A; padding: 4px 8px; border-radius: 4px; border: 1px solid #CBD5E1;")
        else:
            self.lbl_payment_display.setText("Payment Mode: CREDIT")
            self.lbl_payment_display.setStyleSheet("font-weight: bold; font-size: 12px; color: #DC2626; padding: 4px 8px; border-radius: 4px; border: 1px solid #CBD5E1;")

    def on_product_selected(self):
        prod_id = self.combo_product.currentData()
        if not prod_id:
            self.lbl_prod_mrp.setText("0.00")
            self.lbl_prod_base_price.setText("0.00")
            self.lbl_prod_stock.setText("0")
            return

        for p in self.products_list:
            if p['id'] == prod_id:
                mrp = float(p['mrp'])
                has_tp = bool(p.get('has_tp', True))

                # Update pricing rule combo
                self.combo_pricing_rule.blockSignals(True)
                self.combo_pricing_rule.setCurrentIndex(0 if has_tp else 1)
                self.combo_pricing_rule.blockSignals(False)

                base_price = calculate_tp(mrp, has_tp=has_tp)

                self.lbl_prod_mrp.setText(f"{mrp:,.2f}")
                self.lbl_prod_base_price.setText(f"{base_price:,.2f}")
                self.lbl_prod_stock.setText(str(p['stock']))

                if p['stock'] <= 0:
                    self.lbl_prod_stock.setStyleSheet("font-size: 13px; font-weight: bold; color: #DC2626; padding: 4px;")
                elif p['stock'] <= p['reorder_level']:
                    self.lbl_prod_stock.setStyleSheet("font-size: 13px; font-weight: bold; color: #D97706; padding: 4px;")
                else:
                    self.lbl_prod_stock.setStyleSheet("font-size: 13px; font-weight: bold; color: #16A34A; padding: 4px;")

                break

    def on_pricing_rule_changed(self):
        self.update_add_preview_rate()

    def update_add_preview_rate(self):
        prod_id = self.combo_product.currentData()
        if not prod_id:
            return
        for p in self.products_list:
            if p['id'] == prod_id:
                mrp = float(p['mrp'])
                has_tp = bool(self.combo_pricing_rule.currentData())
                base_price = calculate_tp(mrp, has_tp=has_tp)
                self.lbl_prod_base_price.setText(f"{base_price:,.2f}")
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

        has_tp = bool(self.combo_pricing_rule.currentData())
        disc_pct = float(self.spin_discount.value())
        mrp = float(target_prod['mrp'])
        tp = calculate_tp(mrp, has_tp=has_tp)

        # Check if identical product + has_tp is already in cart
        found = False
        for item in self.cart_items:
            if item['product_id'] == prod_id and item['has_tp'] == has_tp:
                item['quantity'] += qty
                item['discount_percent'] = disc_pct
                found = True
                break

        if not found:
            self.cart_items.append({
                'product_id': target_prod['id'],
                'name': target_prod['name'],
                'mrp': mrp,
                'has_tp': has_tp,
                'tp': tp,
                'discount_percent': disc_pct,
                'quantity': qty
            })

        self.update_cart_calculations()

    def update_cart_calculations(self):
        processed_cart = []
        for idx, item in enumerate(self.cart_items):
            mrp = float(item['mrp'])
            has_tp = bool(item.get('has_tp', True))
            tp = calculate_tp(mrp, has_tp=has_tp)
            disc_pct = float(item.get('discount_percent', 0.0))
            final_rate = calculate_final_rate(tp, disc_pct)
            total = calculate_line_total(final_rate, item['quantity'])

            item['tp'] = tp
            item['final_rate'] = final_rate
            item['total'] = total

            processed_cart.append({
                'product_id': item['product_id'],
                'name': item['name'],
                'mrp': mrp,
                'has_tp': has_tp,
                'tp': tp,
                'discount_percent': disc_pct,
                'final_rate': final_rate,
                'quantity': item['quantity'],
                'total': total
            })

        # Render Table
        self.table_cart.setRowCount(len(processed_cart))
        for row_idx, item in enumerate(processed_cart):
            # 0: Sr
            item_sr = QTableWidgetItem(str(row_idx + 1))
            item_sr.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_cart.setItem(row_idx, 0, item_sr)

            # 1: Name
            self.table_cart.setItem(row_idx, 1, QTableWidgetItem(item['name']))

            # 2: MRP
            item_mrp = QTableWidgetItem(f"{item['mrp']:,.2f}")
            item_mrp.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_cart.setItem(row_idx, 2, item_mrp)

            # 3: Rate Type ComboBox (TP vs MRP)
            combo_type = QComboBox()
            combo_type.addItem("TP (-15%)", True)
            combo_type.addItem("MRP", False)
            combo_type.setCurrentIndex(0 if item['has_tp'] else 1)
            combo_type.currentIndexChanged.connect(lambda _, idx=row_idx, cb=combo_type: self.on_cart_tp_changed(idx, cb.currentData()))
            self.table_cart.setCellWidget(row_idx, 3, combo_type)

            # 4: Base TP / Rate
            item_tp = QTableWidgetItem(f"{item['tp']:,.2f}")
            item_tp.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_cart.setItem(row_idx, 4, item_tp)

            # 5: Disc % DoubleSpinBox
            spin_d = QDoubleSpinBox()
            spin_d.setRange(0.0, 100.0)
            spin_d.setDecimals(1)
            spin_d.setSingleStep(0.5)
            spin_d.setSuffix("%")
            spin_d.setValue(item['discount_percent'])
            spin_d.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin_d.valueChanged.connect(lambda val, idx=row_idx: self.on_cart_disc_changed(idx, val))
            self.table_cart.setCellWidget(row_idx, 5, spin_d)

            # 6: Final Rate
            item_fr = QTableWidgetItem(f"{item['final_rate']:,.2f}")
            item_fr.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table_cart.setItem(row_idx, 6, item_fr)

            # 7: Qty SpinBox
            spin_q = QSpinBox()
            spin_q.setRange(1, 99999)
            spin_q.setValue(item['quantity'])
            spin_q.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin_q.valueChanged.connect(lambda val, idx=row_idx: self.on_cart_qty_changed(idx, val))
            self.table_cart.setCellWidget(row_idx, 7, spin_q)

            # 8: Line Total
            item_tot = QTableWidgetItem(f"{item['total']:,.2f}")
            item_tot.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_tot.setForeground(Qt.GlobalColor.darkGreen)
            self.table_cart.setItem(row_idx, 8, item_tot)

            # 9: Remove Button
            btn_remove = QPushButton("Remove")
            btn_remove.setProperty("class", "DangerBtn")
            btn_remove.clicked.connect(lambda _, idx=row_idx: self.on_cart_item_removed(idx))
            self.table_cart.setCellWidget(row_idx, 9, btn_remove)

        # Compute Summary
        summary = compute_cart_summary(processed_cart)
        self.lbl_subtotal.setText(f"PKR {summary['subtotal']:,.2f}")
        self.lbl_discount.setText(f"- PKR {summary['discount_amount']:,.2f}")
        self.lbl_grand_total.setText(f"PKR {summary['grand_total']:,.2f}")

    def on_cart_tp_changed(self, index: int, has_tp: bool):
        if 0 <= index < len(self.cart_items):
            self.cart_items[index]['has_tp'] = has_tp
            self.update_cart_calculations()

    def on_cart_disc_changed(self, index: int, new_disc: float):
        if 0 <= index < len(self.cart_items):
            self.cart_items[index]['discount_percent'] = new_disc
            self.update_cart_calculations()

    def on_cart_qty_changed(self, index: int, new_qty: int):
        if 0 <= index < len(self.cart_items):
            self.cart_items[index]['quantity'] = new_qty
            self.update_cart_calculations()

    def on_cart_item_removed(self, index: int):
        if 0 <= index < len(self.cart_items):
            del self.cart_items[index]
            self.update_cart_calculations()

    def clear_cart(self):
        self.cart_items.clear()
        self.update_cart_calculations()

    def save_and_print_invoice(self):
        cust_id = self.combo_customer.currentData()
        rep_id = self.combo_rep.currentData()
        payment_mode = self.combo_payment_mode.currentText()

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
            invoice_dict = create_invoice(cust_id, rep_id, self.cart_items, payment_mode=payment_mode)
            
            # Generate PDF receipt
            pdf_path = generate_invoice_pdf(invoice_dict)

            # Success Popup
            QMessageBox.information(
                self, "Invoice Created",
                f"Invoice '{invoice_dict['invoice_number']}' processed successfully!\nPayment Mode: {payment_mode}\nGrand Total: PKR {invoice_dict['grand_total']:,.2f}"
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
