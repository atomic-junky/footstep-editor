"""
Application Theme.

This file defines the QSS (Qt Style Sheets) for the application
to match the modern, card-based design.
"""

# Colors
BG_COLOR = "#f3f4f6"       # Light grey background
SURFACE_COLOR = "#ffffff"   # White cards
BORDER_COLOR = "#e5e7eb"    # Subtle borders
TEXT_COLOR = "#1f2937"      # Dark grey text
PRIMARY_COLOR = "#8b5cf6"   # Purple accent
ACCENT_COLOR = "#a3e635"    # Lime/Green accent

STYLESHEET = f"""
/* Global Reset */
QMainWindow {{
    background-color: {BG_COLOR};
}}

QWidget {{
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    color: {TEXT_COLOR};
}}

/* Panel Cards (identified by class or object name in widgets) */
QFrame {{
    background-color: transparent;
}}

/* Buttons */
QPushButton {{
    background-color: {SURFACE_COLOR};
    border: 1px solid {BORDER_COLOR};
    border-radius: 4px;
    padding: 4px 8px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: #f9fafb;
    border-color: #d1d5db;
}}

QPushButton:pressed {{
    background-color: #f3f4f6;
}}

/* Primary Action Buttons */
QPushButton[class="primary"] {{
    background-color: {PRIMARY_COLOR};
    color: white;
    border: none;
}}

QPushButton[class="primary"]:hover {{
    background-color: #7c3aed;
}}

/* Splitters - Make them invisible spacers */
QSplitter::handle {{
    background: {BORDER_COLOR};
    width: 2px;
    height: 2px;
}}

/* Menu Bar */
QMenuBar {{
    background-color: {SURFACE_COLOR};
    border-bottom: 1px solid {BORDER_COLOR};
    padding: 3px;
}}

QMenuBar::item {{
    padding: 3px 6px;
    border-radius: 3px;
    background: transparent;
}}

QMenuBar::item:selected {{
    background-color: {BG_COLOR};
}}

QFrame#ViewPanel {{
    background-color: {BORDER_COLOR};
}}
"""
