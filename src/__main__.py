"""Main entry point for the application."""

import sys
import logging

from PySide6.QtWidgets import QApplication

from src.ui.frmMain import FSEditor

logger = logging.getLogger(__name__)


def main():
    """Run the application."""
    logger.info("Starting Footstep Editor")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Using the modular FSEditor from frmMain
    window = FSEditor()
    window.show()
    
    logger.info("Application window shown")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()