"""
Properties Panel Widget.

This widget represents the properties or settings area.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class PropertiesPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PropertiesPanel")
        
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        layout = QVBoxLayout(self)
        
        label = QLabel("Properties")
        label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a1a1a;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
