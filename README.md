# New Quetta Surgical and Medicine Distribution (NQS POS v2.0)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://pypi.org/project/PyQt6/)
[![Database](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6.svg)]()
[![License](https://img.shields.io/badge/License-Proprietary-darkgrey.svg)]()

**NQS POS v2.0** is an enterprise-grade, single-workstation desktop Point of Sale (POS), Inventory Control, and Invoicing system developed specifically for **New Quetta Surgical and Medicine Distribution**. 

Engineered with **PyQt6**, **SQLite**, and **ReportLab**, the application is optimized for high-volume wholesale and retail pharmaceutical distribution. It provides offline reliability, zero-latency transaction entry, flexible pricing rules (Trade Price vs. Retail MRP), custom line-item discounts, Cash vs. Credit account classification, automated 10:00 PM End-of-Day (EOD) email intelligence, and triple-layer disaster recovery with Google Drive cloud backup.

---

## Store & Legal Identification

* **Store Title**: New Quetta Surgical and Medicine Distribution
* **Address**: Ramzan Plaza Near Saleem Complex, Ptail Bagh. Quetta.
* **Phone**: 0334-2045896
* **Email**: newquettamedicalandsurgical@gmail.com
* **Statutory Compliance**: Every generated customer invoice automatically incorporates the mandatory **Form 2A Distributor Warranty under Section 23(1) of the Drug Act 1976** with authorized signatory representation.

---

## Core Capabilities

### 1. Flexible Sales & Invoicing Engine (POS)
* **Selectable Trade Price (TP) Engine**:
  * Calculates Trade Price as `MRP - 15%` (`MRP * 0.85`) for standard pharmaceutical distributor stock.
  * Allows per-product selection of TP or full Retail MRP directly in the catalog, switchable on-the-fly during active billing.
* **Item-Level & Customer Tier Discounts**:
  * Automatically loads assigned customer discount tiers (0%, 4%, 7%, 12%).
  * Real-time editable discount percentage (`QDoubleSpinBox`) directly from the sales dashboard and per line-item in the cart.
* **Payment Mode Tracking (Cash vs. Credit)**:
  * Select between **Cash** and **Credit** modes at transaction creation.
  * Visual indicators throughout POS, stored persistently, printed on receipts, and broken down in financial reports.
* **Spacious Ergonomic Interface**:
  * Structured two-row product selection bar with guaranteed minimum widths (`240px` for Rate Type, `105px` for Discount %, `100px` for Quantity) ensuring digits are never cut off.
  * Ten-column cart grid with comfortable section heights and unconstrained action buttons.
* **Perpetual Sequence Generation**:
  * Generates atomic, collision-free invoice identifiers formatted as `NQS-[001-999]-[DD]-[MM]-[YY]`.

### 2. Form 2A Branded PDF Customer Receipts
* Engineered with ReportLab Platypus flowables with millimetre-accurate margins.
* Contains full distributor identification, date, time, sales representative, customer details, and invoice sequence.
* Line items detail Product Name, MRP, Rate Type, Base Price, Discount %, Final Rate, Quantity, and Line Total.
* Integrated Pakistani Rupee currency words converter (e.g. `Rupees five thousand four hundred ninety-two Only`).
* Formal authorized signature block: `For New Quetta Surgical and Medicine Distribution`.

### 3. Inventory & Catalog Management
* Full CRUD lifecycle for pharmaceutical products with stock, reorder levels, MRP, and TP applicability.
* Low-stock threshold detection with visual alerts and inline one-click Restock dialogs.
* High-visibility action columns with unclipped, standardized buttons for edit and delete operations.

### 4. Master Data Administration
* **Customers Management**: Directory with phone, address, geographical area assignments, and associated discount tiers.
* **Discount Tiers**: Configurable standard tiers applied across customer profiles.
* **Sales Representatives**: Roster tracking contact information and individual billing totals.
* **Geographical Areas**: Route and zone planning for regional distribution across Quetta and surrounding districts.

### 5. Business Intelligence & Strategic Reporting
* Dynamic date range filtering (presets for Today, This Month, or custom date ranges).
* Payment mode filter (All, Cash Only, Credit Only).
* Four dedicated analytical dimensions:
  1. Performance by Sales Representative (Invoices generated, Gross revenue).
  2. Performance by Geographical Area (Regional revenue penetration).
  3. Product Velocity (Quantity sold, gross turnover).
  4. Payment Mode Summary (Cash vs Credit invoice count, gross turnover, total discounts, net revenue).
* Instant one-click ReportLab PDF export with executive headers and formatted financial summaries.

### 6. Automated 10:00 PM End-of-Day (EOD) Postman
* Background daemon timer evaluates daily metrics every evening at 22:00 (10:00 PM).
* Renders a responsive HTML executive summary detailing total turnover, Cash vs Credit breakdown, top products sold, and sales representative performance.
* Dispatches automatically via Gmail SMTP with TLS encryption.
* Startup catch-up mechanism checks for and dispatches any missed previous-day summaries upon application launch.

### 7. Triple-Layer Disaster Recovery
* **Layer 1 (Local Transactional State)**: Embedded SQLite database in `%APPDATA%\NQS_POS\nqs_pos.db` with WAL (Write-Ahead Logging) mode and busy timeout handling.
* **Layer 2 (Automated Local Archives)**: Time-stamped ZIP backups with automated **30-day retention pruning** to preserve workstation storage.
* **Layer 3 (Google Drive Cloud Mirror)**: OAuth2 integration uploading compressed snapshots directly to a secure Google Drive folder.

### 8. Accessible UI Design System
* High-contrast Dark and Light themes crafted with clean slate tones (`#0F172A`, `#1E293B`, `#334155`, `#F8FAFC`).
* Compact layout maximizing table viewport without crowding interactive controls.
* Zero emojis across all dialogs, headers, buttons, navigation items, and placeholders for a formal corporate aesthetic.

---

## Directory Structure

```
NQS/
├── app/
│   ├── core/
│   │   ├── database.py          # SQLite connection, WAL mode, and schema migration engine
│   │   ├── models.py            # Data Access Object (DAO) layer for all business entities
│   │   ├── pricing.py           # Selectable Trade Price (MRP - 15%) and discount calculator
│   │   ├── pdf_receipt.py       # ReportLab PDF invoice generator with Form 2A warranty
│   │   └── pdf_report.py        # ReportLab PDF BI report exporter
│   ├── services/
│   │   ├── backup_manager.py    # Local ZIP archiving, 30-day retention cleanup, and restore
│   │   ├── gdrive_sync.py       # Google Drive OAuth2 background cloud synchronization
│   │   └── eod_postman.py       # 10 PM EOD HTML email summary generator and SMTP dispatcher
│   └── ui/
│       ├── components/
│       │   └── stat_card.py     # Compact KPI visual card component
│       ├── views/
│       │   ├── dashboard_view.py# Operational KPIs, Cash/Credit metrics, Low Stock alerts
│       │   ├── pos_view.py      # Sales & Invoicing engine with TP toggle, custom disc %, Cash/Credit
│       │   ├── inventory_view.py# Product catalog, stock tracking, and pricing rule configuration
│       │   ├── master_data_view.py # Customer, Tier, Sales Rep, and Area administration
│       │   ├── reports_view.py  # BI reporting suite with date & payment mode filters
│       │   └── settings_view.py # Store branding, warranty, Gmail SMTP, GDrive OAuth, Backups
│       ├── main_window.py       # Main application shell with collapsible sidebar navigation
│       └── styles.py            # High-contrast Dark and Light QSS stylesheets
├── main.py                      # Application bootstrap and GUI exception handler
├── run.bat                      # Windows one-click batch runner with error diagnostic pause
├── PharmaPOS.spec               # PyInstaller standalone build configuration
├── requirements.txt             # Production Python dependencies
└── README.md                    # Project documentation
```

---

## Installation & Setup

### Prerequisites
* Windows 10 or Windows 11 (64-bit)
* Python 3.10 or higher
* Internet connection (for Google Drive sync and EOD email dispatch; sales and POS are 100% offline-capable)

### Setup Instructions

1. **Clone the Repository**:
   ```powershell
   git clone https://github.com/your-username/NQS.git
   cd NQS
   ```

2. **Create and Activate a Virtual Environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Launch the Application**:
   ```powershell
   python main.py
   ```
   Or double-click `run.bat` on Windows.

---

## Building a Standalone Windows Executable

To generate a standalone `.exe` using PyInstaller:

```powershell
# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Build the executable using the provided spec file
pyinstaller PharmaPOS.spec
```

The compiled binary will be placed in the `dist/` directory as `PharmaPOS.exe`.

---

## Application Data & Storage Paths

All persistent application data, configuration keys, receipts, and local backups are safely stored in the user's standard Windows Application Data folder:

* **Database**: `%APPDATA%\NQS_POS\nqs_pos.db`
* **Receipts Archive**: `%APPDATA%\NQS_POS\receipts\`
* **Reports Archive**: `%APPDATA%\NQS_POS\reports\`
* **Database Backups**: `%APPDATA%\NQS_POS\backups\`

---

## Technical Specifications

| Parameter | Specification |
| :--- | :--- |
| **Framework** | PyQt6 (Qt 6.6+) |
| **Database** | SQLite 3 (WAL mode enabled, foreign keys enforced) |
| **PDF Generation** | ReportLab 4.0+ (Flowable Platypus architecture) |
| **Cloud Storage** | Google Drive API v3 (OAuth 2.0 Installed App Flow) |
| **Email Protocol** | SMTP via TLS (Port 587, Gmail App Password) |
| **Minimum Resolution** | 1180 x 720 (Recommended: 1366 x 768 or 1920 x 1080) |
| **Operating System** | Microsoft Windows 10 / 11 (64-bit) |

---
