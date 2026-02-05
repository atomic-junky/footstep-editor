"""
Main Window Form.

This is the main container that assembles the standard widgets.
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

# Import our custom widgets
from src.ui.widgets.view_panel import ViewPanel
from src.ui.widgets.properties_panel import PropertiesPanel
from src.ui.widgets.timeline_panel import TimelinePanel

class FSEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Footstep Editor")
        self.resize(1450, 820)
        
        self._init_ui()
        self._create_menubar()
        
        self.show()
        

    def _create_menubar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # --- File Menu ---
        file_menu = menubar.addMenu("&File")
        
        # New Project
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)

        # Open
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        # Save
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # --- Edit Menu ---
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        # --- Help Menu ---
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction("About")

    def _init_ui(self):
        """Initialize the layout and widgets."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(self.main_splitter)
        
        self.view_panel = ViewPanel()
        self.properties_panel = PropertiesPanel()
        
        self.top_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.top_splitter.addWidget(self.view_panel)
        self.top_splitter.addWidget(self.properties_panel)
        self.top_splitter.setSizes([400, 600])
        
        self.timeline_panel = TimelinePanel()
        
        self.main_splitter.addWidget(self.top_splitter)
        self.main_splitter.addWidget(self.timeline_panel)
        self.main_splitter.setSizes([450, 550])