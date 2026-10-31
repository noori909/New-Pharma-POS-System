"""
Automated End-Of-Day (E.O.D) Intelligence & Email Scheduler for New Quetta Surgical and Medicine Distribution (NQS POS v2.0)
Triggers daily at 10:00 PM sharp (and on application startup for missed days) to compile and
dispatch professional HTML summary emails to Stakeholders via Gmail SMTP.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

from app.core.models import (
    get_setting, set_setting, get_dashboard_summary,
    get_sales_by_sales_rep, get_sales_by_product, get_invoices
)
from app.services.backup_manager import create_local_backup
from app.services.gdrive_sync import upload_backup_to_gdrive


def generate_eod_html_content(report_date: str) -> Tuple[str, Dict[str, Any]]:
    """
    Compiles data and builds responsive HTML email for EOD report.
    """
    biz_name = get_setting('business_name', 'New Quetta Surgical and Medicine Distribution')
    
    # Fetch sales for target report date
    invoices = get_invoices(start_date=report_date, end_date=report_date)
    sales_reps = get_sales_by_sales_rep(start_date=report_date, end_date=report_date)
    products = get_sales_by_product(start_date=report_date, end_date=report_date)

    total_revenue = sum(inv['grand_total'] for inv in invoices)
    total_invoices_count = len(invoices)

    cash_revenue = sum(inv['grand_total'] for inv in invoices if (inv.get('payment_mode') or 'Cash') == 'Cash')
    credit_revenue = sum(inv['grand_total'] for inv in invoices if (inv.get('payment_mode') or 'Cash') == 'Credit')
    cash_count = sum(1 for inv in invoices if (inv.get('payment_mode') or 'Cash') == 'Cash')
    credit_count = sum(1 for inv in invoices if (inv.get('payment_mode') or 'Cash') == 'Credit')

    # Sales Rep Table HTML
    rep_rows_html = ""
    for r in sales_reps:
        rep_rows_html += f"""
        <tr>
            <td style="padding: 8px 12px; border-bottom: 1px solid #E2E8F0; font-weight: 500;">{r['sales_rep_name']}</td>
            <td style="padding: 8px 12px; border-bottom: 1px solid #E2E8F0; text-align: center;">{r['total_invoices']}</td>
            <td style="padding: 8px 12px; border-bottom: 1px solid #E2E8F0; text-align: right; font-weight: 600; color: #2563EB;">PKR {r['total_revenue']:,.2f}</td>
        </tr>
        """
    if not rep_rows_html:
        rep_rows_html = "<tr><td colspan='3' style='padding: 12px; text-align: center; color: #64748B;'>No sales recorded for this date.</td></tr>"

    # Top Products Table HTML
    prod_rows_html = ""
    for p in products[:5]: # Top 5
        prod_rows_html += f"""
        <tr>
            <td style="padding: 8px 12px; border-bottom: 1px solid #E2E8F0; font-weight: 500;">{p['product_name']}</td>
            <td style="padding: 8px 12px; border-bottom: 1px solid #E2E8F0; text-align: center;">{p['total_quantity_sold']} units</td>
            <td style="padding: 8px 12px; border-bottom: 1px solid #E2E8F0; text-align: right; font-weight: 600; color: #16A34A;">PKR {p['total_revenue']:,.2f}</td>
        </tr>
        """
    if not prod_rows_html:
        prod_rows_html = "<tr><td colspan='3' style='padding: 12px; text-align: center; color: #64748B;'>No items sold today.</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #F8FAFC; color: #0F172A; margin: 0; padding: 20px; }}
            .container {{ max-width: 650px; margin: 0 auto; background: #FFFFFF; border-radius: 12px; border: 1px solid #CBD5E1; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .header {{ background: #1E293B; color: #FFFFFF; padding: 24px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 20px; font-weight: 700; letter-spacing: 0.5px; }}
            .header p {{ margin: 6px 0 0 0; color: #CBD5E1; font-size: 13px; }}
            .content {{ padding: 24px; }}
            .kpi-title {{ font-size: 11px; text-transform: uppercase; color: #334155; font-weight: 700; margin-bottom: 4px; }}
            .kpi-value {{ font-size: 22px; font-weight: 700; }}
            .section-title {{ font-size: 15px; font-weight: 700; color: #1E293B; margin-top: 20px; margin-bottom: 10px; border-bottom: 2px solid #0284C7; padding-bottom: 4px; display: inline-block; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13px; }}
            th {{ background: #F1F5F9; color: #0F172A; text-align: left; padding: 10px 12px; font-weight: 600; border-bottom: 2px solid #CBD5E1; }}
            .footer {{ background: #F8FAFC; padding: 16px; text-align: center; font-size: 11px; color: #475569; border-top: 1px solid #E2E8F0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{biz_name}</h1>
                <p>Official End of Day (E.O.D) Business Intelligence Report • <b>{report_date}</b></p>
            </div>
            <div class="content">
                <table style="width: 100%; border: none; margin-bottom: 16px;">
                    <tr>
                        <td style="width: 48%; background: #EFF6FF; border-radius: 8px; padding: 14px; text-align: center; border: 1px solid #BFDBFE;">
                            <div class="kpi-title">Total Revenue Collected</div>
                            <div class="kpi-value" style="color: #1D4ED8;">PKR {total_revenue:,.2f}</div>
                        </td>
                        <td style="width: 4%;"></td>
                        <td style="width: 48%; background: #F0FDF4; border-radius: 8px; padding: 14px; text-align: center; border: 1px solid #BBF7D0;">
                            <div class="kpi-title">Total Invoices Processed</div>
                            <div class="kpi-value" style="color: #15803D;">{total_invoices_count}</div>
                        </td>
                    </tr>
                </table>

                <table style="width: 100%; border: none; margin-bottom: 20px;">
                    <tr>
                        <td style="width: 48%; background: #F8FAFC; border-radius: 8px; padding: 12px; text-align: center; border: 1px solid #CBD5E1;">
                            <div class="kpi-title">Cash Sales</div>
                            <div class="kpi-value" style="font-size: 18px; color: #16A34A;">PKR {cash_revenue:,.2f}</div>
                            <div style="font-size: 11px; color: #475569;">({cash_count} invoices)</div>
                        </td>
                        <td style="width: 4%;"></td>
                        <td style="width: 48%; background: #F8FAFC; border-radius: 8px; padding: 12px; text-align: center; border: 1px solid #CBD5E1;">
                            <div class="kpi-title">Credit Sales</div>
                            <div class="kpi-value" style="font-size: 18px; color: #DC2626;">PKR {credit_revenue:,.2f}</div>
                            <div style="font-size: 11px; color: #475569;">({credit_count} invoices)</div>
                        </td>
                    </tr>
                </table>

                <div class="section-title">Sales Performance by Sales Representative</div>
                <table>
                    <thead>
                        <tr>
                            <th>Sales Representative</th>
                            <th style="text-align: center;">Invoices</th>
                            <th style="text-align: right;">Total Revenue</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rep_rows_html}
                    </tbody>
                </table>

                <div class="section-title">Top 5 Fast Moving Products</div>
                <table>
                    <thead>
                        <tr>
                            <th>Product Name</th>
                            <th style="text-align: center;">Quantity Sold</th>
                            <th style="text-align: right;">Revenue</th>
                        </tr>
                    </thead>
                    <tbody>
                        {prod_rows_html}
                    </tbody>
                </table>
            </div>
            <div class="footer">
                Auto-generated by <b>{biz_name} POS System</b> at 10:00 PM • Disaster Recovery Backup Archived Safely.
            </div>
        </div>
    </body>
    </html>
    """

    summary_metrics = {
        'date': report_date,
        'total_revenue': total_revenue,
        'cash_revenue': cash_revenue,
        'credit_revenue': credit_revenue,
        'invoices_count': total_invoices_count
    }

    return html_content, summary_metrics


def dispatch_eod_email(report_date: str = None) -> Dict[str, Any]:
    """
    Compiles EOD report and sends via Gmail SMTP to configured stakeholders.
    Also triggers backup creation and Google Drive upload.
    """
    if not report_date:
        report_date = datetime.now().strftime('%Y-%m-%d')

    smtp_email = get_setting('smtp_email', '').strip()
    smtp_password = get_setting('smtp_password', '').strip()
    recipients_str = get_setting('recipient_emails', '').strip()

    if not smtp_email or not smtp_password or not recipients_str:
        err_msg = "SMTP email, App Password, or recipient emails not configured in Settings."
        print(f"EOD Dispatch Skipped: {err_msg}")
        return {'success': False, 'error': err_msg}

    recipients = [r.strip() for r in recipients_str.split(',') if r.strip()]
    if not recipients:
        return {'success': False, 'error': "No valid recipient email addresses found."}

    # Generate HTML content
    html_body, metrics = generate_eod_html_content(report_date)

    try:
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"E.O.D Summary Report - {report_date} | PKR {metrics['total_revenue']:,.2f} Revenue"
        msg['From'] = f"New Quetta Surgical POS <{smtp_email}>"
        msg['To'] = ", ".join(recipients)

        msg.attach(MIMEText(html_body, 'html'))

        # Send via Gmail SSL/TLS (port 465) or TLS (port 587)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, recipients, msg.as_string())
        server.quit()

        print(f"E.O.D Report Email dispatched successfully to {len(recipients)} recipients for date {report_date}.")
        set_setting('last_eod_date', report_date)

        # Trigger automatic backup & GDrive upload
        try:
            zip_path = create_local_backup()
            upload_backup_to_gdrive(zip_path)
        except Exception as b_err:
            print(f"Warning: EOD Backup step encountered error: {b_err}")

        return {'success': True, 'date': report_date, 'revenue': metrics['total_revenue']}

    except Exception as e:
        error_msg = f"Failed to send EOD email: {str(e)}"
        print(error_msg)
        return {'success': False, 'error': error_msg}


def check_and_run_eod_startup_check():
    """
    Checks if yesterday's EOD email was dispatched. If missed (e.g. PC was turned off at 10 PM),
    fires it automatically upon startup.
    """
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')

    last_eod_date = get_setting('last_eod_date', '')

    # If yesterday is not recorded in last_eod_date and it's not today, dispatch missed EOD for yesterday
    if last_eod_date != yesterday_str and last_eod_date != today_str:
        print(f"Startup EOD Check: Missed EOD detected for date {yesterday_str}. Running postman dispatch...")
        dispatch_eod_email(report_date=yesterday_str)
