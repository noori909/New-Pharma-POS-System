"""
Modern Visual Design System & Themes for New Quetta Surgical and Medicine Distribution (NQS POS v2.0)
Provides High-Contrast Dark and Light Theme stylesheets with crisp typography, accessible color contrast,
and robust readability across all monitors.
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
    font-size: 17px;
    font-weight: bold;
    color: #38BDF8;
    letter-spacing: 0.5px;
}

#SubTitleLabel {
    font-size: 11px;
    color: #CBD5E1;
}

/* Nav Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #CBD5E1;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.NavButton:hover {
    background-color: #334155;
    color: #FFFFFF;
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
    border-radius: 10px;
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
    color: #CBD5E1;
    text-transform: uppercase;
}

QLabel.CardValue {
    font-size: 24px;
    font-weight: 800;
    color: #F8FAFC;
}

QLabel.SectionHeader {
    font-size: 18px;
    font-weight: 700;
    color: #38BDF8;
}

QLabel.SubHeader {
    font-size: 12px;
    color: #CBD5E1;
}

QLabel.FieldLabel {
    font-size: 11px;
    font-weight: bold;
    color: #CBD5E1;
}

QLabel.ValueLabel {
    font-size: 14px;
    font-weight: bold;
    color: #F8FAFC;
}

/* Form Controls & Inputs */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1.5px solid #475569;
    border-radius: 6px;
    padding: 6px 9px;
    font-size: 13px;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
    border: 1.5px solid #38BDF8;
    background-color: #1E293B;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #475569;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
    padding: 4px;
}

/* Push Buttons */
QPushButton.PrimaryBtn {
    background: #2563EB;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
}

QPushButton.PrimaryBtn:hover {
    background: #1D4ED8;
}

QPushButton.SuccessBtn {
    background: #16A34A;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
}

QPushButton.SuccessBtn:hover {
    background: #15803D;
}

QPushButton.SecondaryBtn {
    background-color: #334155;
    color: #F8FAFC;
    font-weight: 600;
    font-size: 12px;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 7px 14px;
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
    background-color: #B91C1C;
}

/* Tables */
QTableWidget {
    background-color: #1E293B;
    color: #F8FAFC;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 6px;
    selection-background-color: #1E3A8A;
    selection-color: #FFFFFF;
    font-size: 12px;
}

QHeaderView::section {
    background-color: #0F172A;
    color: #E2E8F0;
    padding: 6px 8px;
    font-weight: bold;
    font-size: 12px;
    border: none;
    border-bottom: 2px solid #334155;
}

QTableWidget::item {
    padding: 4px 6px;
    color: #F8FAFC;
}

QTableWidget::item:hover {
    background-color: #334155;
}

QTableWidget QSpinBox, QTableWidget QDoubleSpinBox {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1px solid #475569;
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 12px;
    font-weight: bold;
}

QTableWidget QComboBox {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1px solid #475569;
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 11px;
}

QTableWidget QPushButton.SecondaryBtn {
    background-color: #334155;
    color: #F8FAFC;
    font-size: 11px;
    font-weight: 600;
    border-radius: 4px;
    padding: 3px 6px;
}

QTableWidget QPushButton.DangerBtn {
    background-color: #DC2626;
    color: #FFFFFF;
    font-size: 11px;
    font-weight: 600;
    border-radius: 4px;
    padding: 3px 6px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #334155;
    background-color: #1E293B;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #0F172A;
    color: #CBD5E1;
    padding: 9px 18px;
    font-weight: 600;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
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
    background: #475569;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #64748B;
}
"""

LIGHT_THEME_QSS = """
/* Global Window Styling - High Contrast Crisp Light Theme */
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
    border-right: 1px solid #CBD5E1;
}

#HeaderFrame {
    background-color: #FFFFFF;
    border-bottom: 1px solid #CBD5E1;
    padding: 6px 16px;
}

#AppTitleLabel {
    font-size: 17px;
    font-weight: bold;
    color: #0284C7;
    letter-spacing: 0.5px;
}

#SubTitleLabel {
    font-size: 11px;
    color: #334155;
}

/* Nav Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #334155;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
}

QPushButton.NavButton:hover {
    background-color: #E2E8F0;
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
    border: 1px solid #CBD5E1;
    border-radius: 10px;
}

QFrame.AlertFrame {
    background-color: #FFF7ED;
    border: 1px solid #FDBA74;
    border-radius: 8px;
}

/* Typography Labels */
QLabel.CardTitle {
    font-size: 12px;
    font-weight: 700;
    color: #334155;
    text-transform: uppercase;
}

QLabel.CardValue {
    font-size: 24px;
    font-weight: 800;
    color: #0F172A;
}

QLabel.SectionHeader {
    font-size: 18px;
    font-weight: 700;
    color: #0369A1;
}

QLabel.SubHeader {
    font-size: 12px;
    color: #475569;
}

QLabel.FieldLabel {
    font-size: 11px;
    font-weight: bold;
    color: #334155;
}

QLabel.ValueLabel {
    font-size: 14px;
    font-weight: bold;
    color: #0F172A;
}

/* Form Controls & Inputs */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1.5px solid #94A3B8;
    border-radius: 6px;
    padding: 6px 9px;
    font-size: 13px;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
    border: 1.5px solid #0284C7;
    background-color: #FFFFFF;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
    padding: 4px;
}

/* Push Buttons */
QPushButton.PrimaryBtn {
    background: #2563EB;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
}

QPushButton.PrimaryBtn:hover {
    background: #1D4ED8;
}

QPushButton.SuccessBtn {
    background: #16A34A;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 13px;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
}

QPushButton.SuccessBtn:hover {
    background: #15803D;
}

QPushButton.SecondaryBtn {
    background-color: #F1F5F9;
    color: #1E293B;
    font-weight: 600;
    font-size: 12px;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 7px 14px;
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
    background-color: #B91C1C;
}

/* Tables */
QTableWidget {
    background-color: #FFFFFF;
    color: #0F172A;
    gridline-color: #E2E8F0;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    selection-background-color: #DBEAFE;
    selection-color: #1E3A8A;
    font-size: 12px;
}

QHeaderView::section {
    background-color: #F1F5F9;
    color: #0F172A;
    padding: 6px 8px;
    font-weight: bold;
    font-size: 12px;
    border: none;
    border-bottom: 2px solid #CBD5E1;
}

QTableWidget::item {
    padding: 4px 6px;
    color: #0F172A;
}

QTableWidget::item:hover {
    background-color: #F1F5F9;
}

QTableWidget QSpinBox, QTableWidget QDoubleSpinBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 12px;
    font-weight: bold;
}

QTableWidget QComboBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 11px;
}

QTableWidget QPushButton.SecondaryBtn {
    background-color: #F1F5F9;
    color: #1E293B;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid #CBD5E1;
    border-radius: 4px;
    padding: 3px 6px;
}

QTableWidget QPushButton.DangerBtn {
    background-color: #DC2626;
    color: #FFFFFF;
    font-size: 11px;
    font-weight: 600;
    border-radius: 4px;
    padding: 3px 6px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #CBD5E1;
    background-color: #FFFFFF;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #F1F5F9;
    color: #334155;
    padding: 9px 18px;
    font-weight: 600;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
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
    background: #F1F5F9;
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
