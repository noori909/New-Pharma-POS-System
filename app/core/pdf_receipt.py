"""
ReportLab PDF Invoice Receipt Generator for NQS POS v2.0
Generates high-quality branded customer receipts for printing and archiving.
"""

import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.core.models import get_setting
from app.core.database import get_app_data_dir


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
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#64748B')
    )
    header_right_style = ParagraphStyle(
        'HeaderRight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        alignment=2, # Right aligned
        textColor=colors.HexColor('#2563EB')
    )
    section_label = ParagraphStyle(
        'SecLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#475569')
    )
    section_val = ParagraphStyle(
        'SecVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0F172A')
    )
    table_hdr = ParagraphStyle(
        'TblHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )
    table_hdr_right = ParagraphStyle(
        'TblHdrRight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=2,
        textColor=colors.white
    )
    table_cell = ParagraphStyle(
        'TblCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    table_cell_right = ParagraphStyle(
        'TblCellRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=2,
        textColor=colors.HexColor('#1E293B')
    )
    total_label = ParagraphStyle(
        'TotLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )
    total_val = ParagraphStyle(
        'TotVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        alignment=2,
        textColor=colors.HexColor('#2563EB')
    )

    story = []

    # Business Info
    biz_name = get_setting('business_name', 'NQS Pharmaceutical Distributors')
    biz_address = get_setting('business_address', 'Warehouse Operations, Main Industrial Estate')
    biz_phone = get_setting('business_phone', '+92-300-1234567')

    # Header Table
    header_data = [
        [
            Paragraph(f"<b>{biz_name}</b><br/>{biz_address}<br/>Phone: {biz_phone}", subtitle_style),
            Paragraph(f"SALES RECEIPT<br/><font size=10 color='#64748B'>{invoice_data.get('invoice_number', '')}</font>", header_right_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[3.8*inch, 3.4*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#CBD5E1'), spaceAfter=12))

    # Meta Info Box (Customer & Sales Details)
    created_at = invoice_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    cust_name = invoice_data.get('customer_name', 'Walk-in Customer')
    cust_phone = invoice_data.get('customer_phone', '')
    cust_address = invoice_data.get('customer_address', '')
    rep_name = invoice_data.get('sales_rep_name', 'Default Rep')
    area_name = invoice_data.get('area_name', 'General')
    disc_tier = invoice_data.get('discount_tier', 0.0)

    meta_left = f"<b>BILL TO:</b> {cust_name}<br/>"
    if cust_phone:
        meta_left += f"<b>Phone:</b> {cust_phone}<br/>"
    if cust_address:
        meta_left += f"<b>Address:</b> {cust_address}<br/>"
    meta_left += f"<b>Area:</b> {area_name}"

    meta_right = f"<b>Invoice Date:</b> {created_at}<br/>"
    meta_right += f"<b>Sales Representative:</b> {rep_name}<br/>"
    meta_right += f"<b>Customer Discount Tier:</b> {disc_tier:.1f}%"

    meta_table_data = [
        [Paragraph(meta_left, section_val), Paragraph(meta_right, section_val)]
    ]
    meta_table = Table(meta_table_data, colWidths=[3.6*inch, 3.6*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Items Table Headers
    items_data = [
        [
            Paragraph("#", table_hdr),
            Paragraph("Item Description", table_hdr),
            Paragraph("MRP", table_hdr_right),
            Paragraph("Base TP", table_hdr_right),
            Paragraph("Disc %", table_hdr_right),
            Paragraph("Rate", table_hdr_right),
            Paragraph("Qty", table_hdr_right),
            Paragraph("Total (PKR)", table_hdr_right)
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
        colWidths=[0.3*inch, 2.4*inch, 0.75*inch, 0.75*inch, 0.65*inch, 0.75*inch, 0.5*inch, 1.1*inch]
    )
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(items_table)
    story.append(Spacer(1, 12))

    # Totals Summary Box
    subtotal = float(invoice_data.get('subtotal', 0.0))
    discount_amount = float(invoice_data.get('discount_amount', 0.0))
    grand_total = float(invoice_data.get('grand_total', 0.0))

    totals_data = [
        [Paragraph("Subtotal (Base Trade Price):", total_label), Paragraph(f"PKR {subtotal:,.2f}", total_val)],
        [Paragraph(f"Customer Discount Savings ({disc_tier:.1f}%):", total_label), Paragraph(f"- PKR {discount_amount:,.2f}", ParagraphStyle('GreenVal', parent=total_val, textColor=colors.HexColor('#16A34A')))],
        [Paragraph("<b>NET AMOUNT DUE:</b>", ParagraphStyle('GrandHdr', parent=total_label, fontSize=11, leading=14)), Paragraph(f"<b>PKR {grand_total:,.2f}</b>", ParagraphStyle('GrandVal', parent=total_val, fontSize=13, leading=16, textColor=colors.HexColor('#1D4ED8')))]
    ]

    totals_table = Table(totals_data, colWidths=[2.5*inch, 1.8*inch])
    totals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 1), 0.5, colors.HexColor('#CBD5E1')),
    ]))

    summary_wrapper_data = [
        [Paragraph("<font color='#64748B' size=8>Payment Terms: Cash/Online Transfer upon receipt.<br/>No profit calculations attached.</font>", styles['Normal']), totals_table]
    ]
    summary_wrapper = Table(summary_wrapper_data, colWidths=[2.9*inch, 4.3*inch])
    summary_wrapper.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(summary_wrapper)
    story.append(Spacer(1, 20))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=10))
    footer_text = "<b>NQS POS v2.0</b> • Single-Workstation Secondary Pharma Distribution System<br/>This is a computer-generated invoice receipt. No signature required."
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, leading=11, alignment=1, textColor=colors.HexColor('#94A3B8'))))

    doc.build(story)
    return output_path
