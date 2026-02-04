"""
Action Panel Widget (Bottom).

This widget contains the main action buttons.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt

class ActionPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ActionPanel")
        
        # Styling
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # Main Layout
        layout = QVBoxLayout(self)
        
        # -- Row 1: Two buttons --
        row1 = QHBoxLayout()
        row1.addStretch()
        
        self.btn_1 = QPushButton("Generic Button 1")
        self.btn_1.setFixedSize(150, 40)
        row1.addWidget(self.btn_1)
        
        row1.addSpacing(40)
        
        self.btn_2 = QPushButton("Generic Button 2")
        self.btn_2.setFixedSize(150, 40)
        row1.addWidget(self.btn_2)
        
        row1.addStretch()
        
        # -- Row 2: Main button --
        row2 = QHBoxLayout()
        row2.addStretch()
        
        self.btn_main = QPushButton("Main Action Button")
        self.btn_main.setProperty("class", "primary") # Set property for styling
        self.btn_main.setFixedSize(250, 50)
        row2.addWidget(self.btn_main)
        
        row2.addStretch()
        
        # Add to main layout
        layout.addStretch()
        layout.addLayout(row1)
        layout.addSpacing(10)
        layout.addLayout(row2)
        layout.addStretch()
