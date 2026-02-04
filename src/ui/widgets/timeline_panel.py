"""
Timeline Panel Widget.

This widget contains the main action buttons.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class TimelinePanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TimelinePanel")
        
        self.setFrameShape(QFrame.Shape.NoFrame)
               
        layout = QVBoxLayout(self)
        
        label = QLabel("Timeline")
        label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a1a1a;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
