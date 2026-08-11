# NQS Pharma POS System
**A modern, offline-first Point of Sale system for Secondary Pharmaceutical Distributors.**

## 📋 Overview
NQS Pharma POS is a desktop application built for pharmaceutical distributors, featuring automated sales recording, inventory management, real-time reporting, and cloud backup capabilities. Designed to run completely offline with zero installation requirements.

---

## ✨ Features
* **Sales & Invoicing** - Quick sales entry with automated pricing and discount calculations
* **Inventory Management** - Real-time stock tracking with low stock alerts
* **Reporting** - Sales analysis by Rep, Area, and Product with PDF export
* **Automated Backups** - Triple-layer security (Local + Time-stamped + Google Drive)
* **E.O.D Reports** - Automatic daily email summaries at 10:00 PM
* **Modern UI** - PyQt6 interface with Dark/Light theme toggle
* **Portable** - Single `.exe` file, no installation required

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **UI Framework** | PyQt6 |
| **Database** | SQLite |
| **ORM** | SQLAlchemy |
| **PDF Generation** | ReportLab |
| **Cloud Backup** | Google Drive API v3 |
| **Email Service** | SMTP (Gmail) |
| **Packaging** | PyInstaller |

---

## 📦 Installation

### End Users (No Development Required)
1. Download `NQS_Pharma_POS.exe`
2. Double-click to run
3. No installation needed

### Developers
```bash
# Clone repository
git clone https://github.com/yourusername/nqs-pharma-pos.git
cd nqs-pharma-pos

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

# Build executable
python scripts/build_exe.py
```

---

## 🚀 Quick Start
1. **Launch the application**
2. **Add Master Data** from Dashboard:
    * Products (Name, MRP, Stock)
    * Sales Representatives
    * Geographical Areas
    * Customers (with discount tiers)
3. **Configure Email and Google Drive** (Settings menu)
4. **Start Selling** - Create invoices, print receipts, manage inventory
5. **Generate Reports** - Analyze sales by Rep, Area, or Product

---

## 📁 Project Structure
```text
nqs-pharma-pos/
├── main.py                  # Entry point
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── database/                # Database models & connection
├── logic/                   # Business logic (pricing, inventory, reports)
├── services/                # Backup, email, Google Drive, scheduler
├── ui/                      # PyQt6 interface components
├── resources/               # Icons, styles, templates
├── utils/                   # Helpers, validators, formatters
└── scripts/                 # Build & setup scripts
```

---

## 📊 Key Features Details

### Business Logic
* **Trade Price (TP):** `MRP - 15%`
* **Discount Tiers:** `0%, 4%, 7%, 12%`
* **Invoice Format:** `NQS-XXX-DD-MM-YY` (perpetual increment)

### Reports
* Sales by Sales Rep
* Sales by Area
* Sales by Product
* Export to PDF

### Backup System
* Auto-backup on shutdown
* Auto-backup at 10:00 PM daily
* Retains last 30 days locally
* Syncs to Google Drive

---

## 🔧 Configuration

### Email (Gmail)
```python
# Use App Password (not regular password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
```

### Data Storage
```text
%APPDATA%\NQSPharmaPOS\
├── data\
│   ├── pharma.db          # Main database
│   └── backups\           # Local backups
├── token.json             # Google Drive OAuth token
└── logs\                  # Application logs
```

---

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License
Proprietary - Internal use only

---

---

## 🙏 Acknowledgments
* Built with PyQt6, SQLAlchemy, ReportLab
* Google Drive API for cloud backups
* Gmail SMTP for automated reporting
