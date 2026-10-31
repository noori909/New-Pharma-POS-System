"""
ReportLab PDF Invoice Receipt Generator for New Quetta Surgical and Medicine Distribution
Generates high-quality branded customer receipts for printing and archiving.
Compliant with Section 23(1) of the Drug Act 1976 warranty specifications.
"""

import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.core.models import get_setting
from app.core.database import get_app_data_dir


def amount_in_words(amount: float) -> str:
    """Converts a numeric amount to Pakistani Rupee text."""
    try:
        n = int(round(amount))
        if n <= 0:
            return "--Rupees Zero Only--"
        
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
                "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
                "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

        def helper(num: int) -> str:
            if num == 0:
                return ""
            elif num < 20:
                return ones[num] + " "
            elif num < 100:
                return tens[num // 10] + (" " + ones[num % 10] if num % 10 != 0 else "") + " "
            elif num < 1000:
                return ones[num // 100] + " Hundred " + helper(num % 100)
            elif num < 100000:
                return helper(num // 1000) + "Thousand " + helper(num % 1000)
            elif num < 10000000:
                return helper(num // 100000) + "Lakh " + helper(num % 100000)
            else:
                return helper(num // 10000000) + "Crore " + helper(num % 10000000)

        res = helper(n).strip()
        return f"--Rupees {res} Only--"
    except Exception:
        return ""


def generate_invoice_pdf(invoice_data: dict, output_path: str = None) -> str:
    """
    Generates a professional branded PDF invoice receipt.
    Returns absolute path to the generated PDF file.
    """
    if not output_path:
        receipts_dir = get_app_data_dir() / "receipts"
        receipts_dir.mkdir(parents=True, exist_ok=True)
        safe_inv_num = invoice_data.get('invoice_number', 'receipt').replace('/', '-').replace('\\', '-')
        output_path = str(receipts_dir / f"Invoice_{safe_inv_num}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=26,
        bottomMargin=26
    )

    styles = getSampleStyleSheet()

    # Typography Styles
    store_title_style = ParagraphStyle(
        'StoreTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=1, # Centered
        textColor=colors.HexColor('#0F172A')
    )
    store_sub_style = ParagraphStyle(
        'StoreSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        alignment=1,
        textColor=colors.HexColor('#334155')
    )
    invoice_banner_style = ParagraphStyle(
        'InvBanner',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        alignment=1,
        textColor=colors.HexColor('#0F172A')
    )
    section_val = ParagraphStyle(
        'SecVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#0F172A')
    )
    section_val_right = ParagraphStyle(
        'SecValRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        alignment=2,
        textColor=colors.HexColor('#0F172A')
    )
    table_hdr = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )
    table_hdr_right = ParagraphStyle(
        'TblHdrRight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=2,
        textColor=colors.white
    )
    table_cell = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0F172A')
    )
    table_cell_right = ParagraphStyle(
        'TblCellRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=2,
        textColor=colors.HexColor('#0F172A')
    )
    total_label = ParagraphStyle(
        'TotLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    total_val = ParagraphStyle(
        'TotVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        alignment=2,
        textColor=colors.HexColor('#0F172A')
    )
    warranty_title = ParagraphStyle(
        'WarTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0F172A')
    )
    warranty_body = ParagraphStyle(
        'WarBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.8,
        alignment=4, # Justified
        textColor=colors.HexColor('#334155')
    )

    story = []

    # 1. STORE HEADER
    biz_name = get_setting('business_name', 'New Quetta Surgical and Medicine Distribution')
    biz_address = get_setting('business_address', 'Ramzan Plaza Near Saleem Complex, Ptail Bagh. Quetta.')
    biz_phone = get_setting('business_phone', '0334-2045896')
    biz_email = get_setting('business_email', 'newquettamedicalandsurgical@gmail.com')

    header_text = f"<b>{biz_name}</b>"
    sub_text = f"{biz_address}<br/>Phone: <b>{biz_phone}</b> | E-Mail: <b>{biz_email}</b>"

    story.append(Paragraph(header_text, store_title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(sub_text, store_sub_style))
    story.append(Spacer(1, 6))

    # SALE INVOICE BANNER
    banner_table = Table([[Paragraph("<b>SALE INVOICE</b>", invoice_banner_style)]], colWidths=[535])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 6))

    # 2. META INFO BOX (Invoice details, Payment Mode, Customer)
    inv_number = invoice_data.get('invoice_number', '')
    created_at = invoice_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    payment_mode = (invoice_data.get('payment_mode') or 'Cash').upper()
    cust_name = invoice_data.get('customer_name', 'Walk-in Customer')
    cust_phone = invoice_data.get('customer_phone', '')
    cust_address = invoice_data.get('customer_address', '')
    rep_name = invoice_data.get('sales_rep_name', 'Counter')
    area_name = invoice_data.get('area_name', 'General')

    # Color badge for Payment Mode
    pm_color = '#15803D' if payment_mode == 'CASH' else '#B91C1C'

    meta_left = f"<b>Invoice #:</b> {inv_number}<br/>"
    meta_left += f"<b>Date:</b> {created_at}<br/>"
    meta_left += f"<b>Payment Mode:</b> <font color='{pm_color}'><b>{payment_mode}</b></font><br/>"
    meta_left += f"<b>Sales Representative:</b> {rep_name}"

    meta_right = f"<b>Customer:</b> {cust_name}<br/>"
    if cust_phone:
        meta_right += f"<b>Phone:</b> {cust_phone}<br/>"
    if cust_address:
        meta_right += f"<b>Address:</b> {cust_address}<br/>"
    meta_right += f"<b>Area:</b> {area_name}"

    meta_table_data = [
        [Paragraph(meta_left, section_val), Paragraph(meta_right, section_val)]
    ]
    meta_table = Table(meta_table_data, colWidths=[265, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # 3. ITEMS TABLE
    # Note: Customer discount tier is removed from receipt as requested; Disc % shows on item line
    items_data = [
        [
            Paragraph("Sr.", table_hdr),
            Paragraph("Item Description", table_hdr),
            Paragraph("MRP", table_hdr_right),
            Paragraph("Base TP", table_hdr_right),
            Paragraph("Disc %", table_hdr_right),
            Paragraph("Rate", table_hdr_right),
            Paragraph("Qty", table_hdr_right),
            Paragraph("Net Amount", table_hdr_right)
        ]
    ]

    items = invoice_data.get('items', [])
    for idx, itm in enumerate(items, start=1):
        mrp = float(itm.get('mrp', 0.0))
        tp = float(itm.get('tp', 0.0))
        disc_pct = float(itm.get('discount_percent', 0.0))
        rate = float(itm.get('final_rate', 0.0))
        qty = int(itm.get('quantity', 0))
        tot = float(itm.get('total_price', 0.0))

        items_data.append([
            Paragraph(str(idx), table_cell),
            Paragraph(str(itm.get('product_name', '')), table_cell),
            Paragraph(f"{mrp:,.2f}", table_cell_right),
            Paragraph(f"{tp:,.2f}", table_cell_right),
            Paragraph(f"{disc_pct:.1f}%", table_cell_right),
            Paragraph(f"{rate:,.2f}", table_cell_right),
            Paragraph(str(qty), table_cell_right),
            Paragraph(f"{tot:,.2f}", table_cell_right),
        ])

    items_table = Table(
        items_data,
        colWidths=[24, 185, 54, 54, 46, 54, 34, 84]
    )
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 4.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(items_table)
    story.append(Spacer(1, 8))

    # 4. TOTALS FINANCIAL SUMMARY
    subtotal = float(invoice_data.get('subtotal', 0.0))
    discount_amount = float(invoice_data.get('discount_amount', 0.0))
    grand_total = float(invoice_data.get('grand_total', 0.0))
    words_text = amount_in_words(grand_total)

    totals_data = [
        [Paragraph("Gross Amount (Subtotal):", total_label), Paragraph(f"PKR {subtotal:,.2f}", total_val)],
        [Paragraph("Discount Amount:", total_label), Paragraph(f"- PKR {discount_amount:,.2f}", ParagraphStyle('GreenVal', parent=total_val, textColor=colors.HexColor('#16A34A')))],
        [Paragraph("<b>Net Total (Amount Due):</b>", ParagraphStyle('GrandHdr', parent=total_label, fontSize=9.5, leading=12)), Paragraph(f"<b>PKR {grand_total:,.2f}</b>", ParagraphStyle('GrandVal', parent=total_val, fontSize=11, leading=14, textColor=colors.HexColor('#1D4ED8')))]
    ]

    totals_table = Table(totals_data, colWidths=[150, 120])
    totals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 4.5),
        ('LINEBELOW', (0, 0), (-1, 1), 0.5, colors.HexColor('#E2E8F0')),
    ]))

    summary_left_text = f"<b>Payment Mode:</b> {payment_mode}<br/><b>Amount in Words:</b><br/>{words_text}"
    summary_wrapper_data = [
        [Paragraph(summary_left_text, section_val), totals_table]
    ]
    summary_wrapper = Table(summary_wrapper_data, colWidths=[265, 270])
    summary_wrapper.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(summary_wrapper)
    story.append(Spacer(1, 12))

    # 5. LEGAL WARRANTY UNDER DRUG ACT 1976 (FORM 2A) & SIGNATURE
    default_warranty = (
        "Warranty: Under section 23(1) of the drug act 1976, I Nazir Ahmed being a person resident in Pakistan "
        "Carrying business at Ramzan plaza Patail Bagh Quetta under the name of New Quetta Surgical and Medicine Distribution "
        "being an authorized distributor do hereby give this warranty that drugs described in this invoice bill as sold by us "
        "do not contrivance in any way the provisions of section 23 of drug act 1976."
    )
    warranty_text = get_setting('warranty_text', default_warranty)

    legal_warranty_content = [
        Paragraph("<b>FORM 2A: Warranty under Section 23(1)(i) of the Drugs Act, 1976:</b>", warranty_title),
        Spacer(1, 2),
        Paragraph(warranty_text, warranty_body),
        Spacer(1, 4),
        Paragraph("<font size=6.5 color='#64748B'>Note: For near expiry items, we must be informed within reasonable notice period. Ensure stock is received in intact condition.</font>", warranty_body)
    ]

    sig_block = [
        Spacer(1, 14),
        HRFlowable(width="80%", thickness=1, color=colors.HexColor('#64748B'), hAlign='RIGHT', spaceAfter=4),
        Paragraph(f"<b>For {biz_name}</b>", ParagraphStyle('SigHdr', parent=styles['Normal'], fontSize=7.5, leading=9.5, alignment=2, textColor=colors.HexColor('#0F172A'))),
        Paragraph("Authorized Signature & Stamp", ParagraphStyle('SigSub', parent=styles['Normal'], fontSize=6.5, leading=8.5, alignment=2, textColor=colors.HexColor('#64748B')))
    ]

    bottom_table_data = [
        [legal_warranty_content, sig_block]
    ]
    bottom_table = Table(bottom_table_data, colWidths=[360, 175])
    bottom_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    story.append(bottom_table)
    story.append(Spacer(1, 8))

    # Footer line
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=4))
    footer_text = f"<b>{biz_name}</b> • {biz_address} • Phone: {biz_phone}"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, leading=9, alignment=1, textColor=colors.HexColor('#64748B'))))

    doc.build(story)
    return output_path
