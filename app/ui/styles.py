"""
Modern Visual Design System & Themes for NQS POS v2.0 (PyQt6 QSS)
Provides Dark and Light Theme stylesheets with rich aesthetics, curated HSL-tailored colors,
custom tables, styled cards, hover states, and professional badges.
"""

DARK_THEME_QSS = """
/* Global Window Styling */
QMainWindow, QDialog {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #F8FAFC;
    font-family: 'Segoe UI', 'Inter', sans-serif;
}

/* Sidebar & Navigation Header */
#SidebarFrame {
    background-color: #1E293B;
    border-right: 1px solid #334155;
}

#HeaderFrame {
    background-color: #1E293B;
    border-bottom: 1px solid #334155;
    padding: 6px 16px;
}

#AppTitleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #38BDF8;
    letter-spacing: 0.5px;
}

#SubTitleLabel {
    font-size: 11px;
    color: #94A3B8;
}

/* Nav Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.NavButton:hover {
    background-color: #334155;
    color: #F8FAFC;
}

QPushButton.NavButton:checked {
    background-color: #2563EB;
    color: #FFFFFF;
    border-left: 4px solid #60A5FA;
}

/* Cards & Frames */
QFrame.CardFrame {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
}

QFrame.AlertFrame {
    background-color: #451A03;
    border: 1px solid #9A3412;
    border-radius: 8px;
}

/* Typography Labels */
QLabel.CardTitle {
    font-size: 12px;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
}

QLabel.CardValue {
    font-size: 26px;
    font-weight: 800;
    color: #F8FAFC;
}

QLabel.SectionHeader {
    font-size: 16px;
    font-weight: 700;
    color: #38BDF8;
}

/* Form Controls & Inputs */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1.5px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #2563EB;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
    border: 1.5px solid #38BDF8;
    background-color: #1E293B;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

/* Push Buttons */
QPushButton.PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #1D4ED8);
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
}

QPushButton.PrimaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
}

QPushButton.SuccessBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #16A34A, stop:1 #15803D);
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
}

QPushButton.SuccessBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #22C55E, stop:1 #16A34A);
}

QPushButton.SecondaryBtn {
    background-color: #334155;
    color: #F8FAFC;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid #475569;
    border-radius: 8px;
    padding: 8px 16px;
}

QPushButton.SecondaryBtn:hover {
    background-color: #475569;
    color: #FFFFFF;
}

QPushButton.DangerBtn {
    background-color: #DC2626;
    color: #FFFFFF;
    font-weight: 600;
    font-size: 12px;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
}

QPushButton.DangerBtn:hover {
    background-color: #EF4444;
}

/* Tables */
QTableWidget {
    background-color: #1E293B;
    color: #F8FAFC;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 8px;
    selection-background-color: #1E3A8A;
    selection-color: #FFFFFF;
    font-size: 12px;
}

QHeaderView::section {
    background-color: #0F172A;
    color: #94A3B8;
    padding: 8px;
    font-weight: bold;
    font-size: 12px;
    border: none;
    border-bottom: 2px solid #334155;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:hover {
    background-color: #334155;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #1E293B;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #0F172A;
    color: #94A3B8;
    padding: 10px 20px;
    font-weight: 600;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #1E293B;
    color: #38BDF8;
    border-bottom: 3px solid #38BDF8;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #0F172A;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #475569;
}
"""

LIGHT_THEME_QSS = """
/* Global Window Styling */
QMainWindow, QDialog {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #0F172A;
    font-family: 'Segoe UI', 'Inter', sans-serif;
}

/* Sidebar & Navigation Header */
#SidebarFrame {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

#HeaderFrame {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 6px 16px;
}

#AppTitleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #0284C7;
    letter-spacing: 0.5px;
}

#SubTitleLabel {
    font-size: 11px;
    color: #64748B;
}

/* Nav Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #64748B;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.NavButton:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

QPushButton.NavButton:checked {
    background-color: #2563EB;
    color: #FFFFFF;
    border-left: 4px solid #1D4ED8;
}

/* Cards & Frames */
QFrame.CardFrame {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}

QFrame.AlertFrame {
    background-color: #FFF7ED;
    border: 1px solid #FFEDD5;
    border-radius: 8px;
}

/* Typography Labels */
QLabel.CardTitle {
    font-size: 12px;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
}

QLabel.CardValue {
    font-size: 26px;
    font-weight: 800;
    color: #0F172A;
}

QLabel.SectionHeader {
    font-size: 16px;
    font-weight: 700;
    color: #0284C7;
}

/* Form Controls & Inputs */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #2563EB;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
    border: 1.5px solid #0284C7;
    background-color: #FFFFFF;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

/* Push Buttons */
QPushButton.PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563EB, stop:1 #1D4ED8);
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
}

QPushButton.PrimaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
}

QPushButton.SuccessBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #16A34A, stop:1 #15803D);
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
}

QPushButton.SuccessBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #22C55E, stop:1 #16A34A);
}

QPushButton.SecondaryBtn {
    background-color: #F1F5F9;
    color: #334155;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 8px 16px;
}

QPushButton.SecondaryBtn:hover {
    background-color: #E2E8F0;
    color: #0F172A;
}

QPushButton.DangerBtn {
    background-color: #DC2626;
    color: #FFFFFF;
    font-weight: 600;
    font-size: 12px;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
}

QPushButton.DangerBtn:hover {
    background-color: #EF4444;
}

/* Tables */
QTableWidget {
    background-color: #FFFFFF;
    color: #0F172A;
    gridline-color: #E2E8F0;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    selection-background-color: #DBEAFE;
    selection-color: #1E40AF;
    font-size: 12px;
}

QHeaderView::section {
    background-color: #F8FAFC;
    color: #475569;
    padding: 8px;
    font-weight: bold;
    font-size: 12px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:hover {
    background-color: #F1F5F9;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #E2E8F0;
    background-color: #FFFFFF;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #F8FAFC;
    color: #64748B;
    padding: 10px 20px;
    font-weight: 600;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #0284C7;
    border-bottom: 3px solid #0284C7;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #F8FAFC;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}
"""
