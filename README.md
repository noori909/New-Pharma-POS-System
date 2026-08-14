# New Pharma POS System (NQS POS v2.0)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://pypi.org/project/PyQt6/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![ReportLab](https://img.shields.io/badge/PDF-ReportLab-red.svg)](https://pypi.org/project/reportlab/)
[![License](https://img.shields.io/badge/License-Proprietary-darkgrey.svg)]()

**NQS POS v2.0** is a robust, modern, single-workstation desktop application designed specifically for secondary pharmaceutical distribution operations. Built with **PyQt6**, **SQLite**, and **ReportLab**, it prioritizes offline reliability, zero-delay sales entry, automated 10 PM E.O.D email intelligence, and triple-layer disaster recovery.

---

##  Executive Features

- **Zero-Delay Sales & Invoicing**: Process sales instantly even during internet outages.
- **Trade Price (TP) Engine**: Automatically calculates Trade Price as `MRP - 15%` (`MRP * 0.85`).
- **Dynamic Customer Discount Tiers**: Configure custom discount tiers (e.g. Gold 12%, Silver 7%, Bronze 4%, Standard 0%) applied directly to TP.
- **Perpetual Invoice Sequence**: Formatted as `NQS-XXX-DD-MM-YY` starting at `001` (`NQS-001-14-08-26`). Sequences increment perpetually across days without resetting.
- **Instant PDF Receipts**: Generates branded, professional PDF customer receipts via ReportLab.
- **🚨 Low-Stock Alerts & Quick Restock**: Prominently highlights low-stock items with one-click **Quick Restock** modal.
- **Automated 10:00 PM E.O.D "Postman"**: Compiles daily sales performance, top-moving items, and rep totals into a responsive HTML email dispatched via Gmail SMTP.
- **Triple-Layer Disaster Recovery**:
  1. Local SQLite Database in `%APPDATA%\NQS_POS\nqs_pos.db`.
  2. Time-Stamped `.zip` archives with **30-day automatic retention purge**.
  3. Google Drive OAuth2 background cloud synchronization.
- **Dark & Light Color Themes**: Switchable visual styles designed for reduced eye strain during long warehouse shifts.

---

## System Architecture

```
NQS/
├── app/
│   ├── core/
│   │   ├── database.py          # SQLite setup & schema version migration engine
│   │   ├── models.py            # DAO for Products, Customers, Tiers, Reps, Invoices
│   │   ├── pricing.py           # Trade Price (MRP - 15%) & discount engine
│   │   ├── pdf_receipt.py       # ReportLab PDF receipt generator
│   │   └── pdf_report.py        # ReportLab BI PDF report exporter
│   ├── services/
│   │   ├── backup_manager.py    # Local ZIP backups, 30-day retention purge & restore
│   │   ├── gdrive_sync.py       # Google Drive OAuth2 cloud vault mirror
│   │   └── eod_postman.py       # 10 PM EOD HTML email summary generator & sender
│   └── ui/
│       ├── styles.py            # Dark & Light QSS theme stylesheets
│       ├── main_window.py       # Main shell layout with sidebar navigation
│       └── views/
│           ├── dashboard_view.py# Real-time KPIs, Low Stock Alerts, Quick Restock
│           ├── pos_view.py      # Sales & Invoicing engine with receipt printing
│           ├── inventory_view.py# Product CRUD & stock management
│           ├── master_data_view.py # Customers, Discount Tiers, Reps, Areas
│           ├── reports_view.py  # BI reports (Sales by Rep, Area, Product)
│           └── settings_view.py # Email, GDrive OAuth, Theme, Backup/Restore
├── main.py                      # Application launcher
├── PharmaPOS.spec               # PyInstaller single-executable configuration
└── requirements.txt             # Project dependencies
```

---

## Quick Start Guide

### Prerequisites
- Windows 10 / 11 (64-bit)
- Python 3.10+ (for running from source)

### 1. Running from Source Code
```powershell
# Clone the repository
git clone https://github.com/noori909/New-Pharma-POS-System.git
cd New-Pharma-POS-System

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch application
python main.py
```

### 2. Building Standalone Windows Executable (`PharmaPOS.exe`)
```powershell
.\venv\Scripts\pyinstaller.exe PharmaPOS.spec --clean
```
The single portable executable will be generated at `dist\PharmaPOS.exe`. No Python installation is required to run the EXE!

---

## Initial Configuration & Setup

### 1. Master Data Population
Master Data is empty by default upon initial installation:
1. Open **Master Data** tab → Create **Geographical Areas**.
2. Open **Discount Tiers** tab → Add standard discount tiers (0%, 4%, 7%, 12%).
3. Open **Sales Representatives** tab → Add sales rep profiles.
4. Open **Customers** tab → Add customer pharmacies, assigning them an Area and Discount Tier.
5. Open **Inventory** tab → Add products (Name, MRP, Stock Level, Reorder Level).

### 2. Email Configuration (Gmail SMTP)
1. Go to **Settings** → **✉️ E.O.D Postman Email**.
2. Enter your **Sender Gmail Address** and a **16-character Gmail App Password** (generated from [Google Account Security](https://myaccount.google.com/apppasswords)).
3. Enter comma-separated **Recipient Emails** (e.g. `boss@company.com, manager@company.com`).
4. Click **Save Email Settings** and test delivery via **"Test Send E.O.D Email Now"**.

### 3. Cloud Backup Configuration (Google Drive)
1. Download your `credentials.json` file from Google Cloud Console (Desktop OAuth Client ID).
2. Go to **Settings** → **Disaster Recovery**.
3. Click **"Select credentials.json File"** and choose your JSON credentials file.
4. Click **"Authenticate via Browser"** to complete the one-time authorization. `token.json` will be saved locally in `%APPDATA%\NQS_POS\`.

---

## Security & Privacy FAQ

### Q: Are my Gmail App Password or Google Drive `credentials.json` exposed if I upload the code or `PharmaPOS.exe` to GitHub?
**NO.** All private credentials, `credentials.json`, `token.json`, and database files are stored dynamically at runtime inside the local Windows user profile directory (`%APPDATA%\NQS_POS\`). They are **never hardcoded** in the source code or packaged inside `PharmaPOS.exe`. The `.gitignore` file ensures these sensitive files are excluded from git commits.

### Q: Does the app require internet to process sales?
**NO.** Sales, invoicing, inventory deductions, PDF receipt generation, and local database backups operate 100% offline. Internet is only used for background Google Drive sync and 10 PM EOD email dispatches.

---

