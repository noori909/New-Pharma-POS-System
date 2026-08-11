"""
Stat Card Component for NQS POS v2.0
Modern KPI Card widget displaying metric label, value, subtext, and custom color accents.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class StatCard(QFrame):
    def __init__(self, title: str, value: str, subtext: str = "", accent_color: str = "#2563EB", parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.setProperty("class", "CardFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "CardTitle")
        layout.addWidget(self.title_label)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setProperty("class", "CardValue")
        self.value_label.setStyleSheet(f"color: {accent_color};")
        layout.addWidget(self.value_label)

        # Subtext
        if subtext:
            self.subtext_label = QLabel(subtext)
            self.subtext_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
            layout.addWidget(self.subtext_label)

    def set_value(self, value: str):
        self.value_label.setText(value)

    def set_subtext(self, subtext: str):
        if hasattr(self, 'subtext_label'):
            self.subtext_label.setText(subtext)
