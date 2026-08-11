"""
ReportLab PDF Business Intelligence Report Generator for NQS POS v2.0
Generates exportable PDF reports for Sales by Rep, Sales by Area, and Sales by Product.
"""

from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.core.models import get_setting, get_app_data_dir


def generate_bi_report_pdf(report_type: str, date_range_str: str, data_rows: list, output_path: str = None) -> str:
    """
    Generates a PDF business intelligence report.
    report_type: "rep", "area", or "product"
    """
    if not output_path:
        reports_dir = get_app_data_dir() / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = str(reports_dir / f"Report_{report_type}_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Title Map
    titles_map = {
        'rep': ('SALES PERFORMANCE BY SALES REPRESENTATIVE', ['#', 'Sales Representative', 'Total Invoices', 'Revenue Generated (PKR)']),
        'area': ('SALES PERFORMANCE BY GEOGRAPHICAL AREA', ['#', 'Geographical Area', 'Total Invoices', 'Revenue Generated (PKR)']),
        'product': ('PRODUCT MOVEMENT & SALES PERFORMANCE', ['#', 'Product Name', 'Total Quantity Sold', 'Revenue Generated (PKR)'])
    }

    report_title, headers = titles_map.get(report_type.lower(), ('BUSINESS INTELLIGENCE REPORT', ['#', 'Name', 'Count', 'Revenue (PKR)']))

    title_style = ParagraphStyle(
        'RptTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A')
    )
    subtitle_style = ParagraphStyle(
        'RptSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#475569')
    )
    hdr_cell = ParagraphStyle(
        'HdrCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )
    hdr_cell_right = ParagraphStyle(
        'HdrCellRight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=2,
        textColor=colors.white
    )
    body_cell = ParagraphStyle(
        'BdyCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    body_cell_right = ParagraphStyle(
        'BdyCellRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=2,
        textColor=colors.HexColor('#1E293B')
    )

    story = []

    # Header
    biz_name = get_setting('business_name', 'NQS Pharmaceutical Distributors')
    story.append(Paragraph(f"<b>{biz_name}</b>", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"{report_title}<br/><font color='#2563EB'><b>Filter Date Range:</b> {date_range_str}</font>", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#CBD5E1'), spaceAfter=14))

    # Data Table
    table_data = [[
        Paragraph(headers[0], hdr_cell),
        Paragraph(headers[1], hdr_cell),
        Paragraph(headers[2], hdr_cell_right),
        Paragraph(headers[3], hdr_cell_right),
    ]]

    total_count = 0
    total_rev = 0.0

    for idx, row in enumerate(data_rows, start=1):
        if report_type == 'rep':
            name = str(row.get('sales_rep_name', ''))
            count = int(row.get('total_invoices', 0))
            rev = float(row.get('total_revenue', 0.0))
        elif report_type == 'area':
            name = str(row.get('area_name', ''))
            count = int(row.get('total_invoices', 0))
            rev = float(row.get('total_revenue', 0.0))
        else: # product
            name = str(row.get('product_name', ''))
            count = int(row.get('total_quantity_sold', 0))
            rev = float(row.get('total_revenue', 0.0))

        total_count += count
        total_rev += rev

        table_data.append([
            Paragraph(str(idx), body_cell),
            Paragraph(name, body_cell),
            Paragraph(f"{count:,}", body_cell_right),
            Paragraph(f"PKR {rev:,.2f}", body_cell_right)
        ])

    # Summary Row
    table_data.append([
        Paragraph("", body_cell),
        Paragraph("<b>GRAND TOTAL:</b>", ParagraphStyle('TotHdr', parent=body_cell, fontName='Helvetica-Bold')),
        Paragraph(f"<b>{total_count:,}</b>", ParagraphStyle('TotCount', parent=body_cell_right, fontName='Helvetica-Bold')),
        Paragraph(f"<b>PKR {total_rev:,.2f}</b>", ParagraphStyle('TotRev', parent=body_cell_right, fontName='Helvetica-Bold', textColor=colors.HexColor('#1D4ED8')))
    ])

    report_table = Table(table_data, colWidths=[0.5*inch, 3.2*inch, 1.5*inch, 2.0*inch])
    report_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F8FAFC')]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E2E8F0')),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#94A3B8'))
    ]))

    story.append(report_table)
    story.append(Spacer(1, 20))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=10))
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    story.append(Paragraph(f"Report Generated on: {now_str} • NQS POS v2.0 Strategic Reporting Engine", ParagraphStyle('Foot', parent=styles['Normal'], fontSize=8, leading=10, alignment=1, textColor=colors.HexColor('#94A3B8'))))

    doc.build(story)
    return output_path
