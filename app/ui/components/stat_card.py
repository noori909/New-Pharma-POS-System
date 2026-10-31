"""
Stat Card Component for New Quetta Surgical and Medicine Distribution (NQS POS v2.0)
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
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "CardTitle")
        layout.addWidget(self.title_label)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setProperty("class", "CardValue")
        self.value_label.setStyleSheet(f"color: {accent_color}; font-weight: 800; font-size: 22px;")
        layout.addWidget(self.value_label)

        # Subtext
        self.subtext_label = QLabel(subtext)
        self.subtext_label.setProperty("class", "SubHeader")
        self.subtext_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.subtext_label)

    def set_value(self, value: str):
        self.value_label.setText(value)

    def set_subtext(self, subtext: str):
        self.subtext_label.setText(subtext)
