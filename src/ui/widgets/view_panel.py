"""
View Panel Widget.

This widget represents the main view or editor area.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class ViewPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ViewPanel")
        
        layout = QVBoxLayout(self)
        
        label = QLabel("View")
        label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a1a1a;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
