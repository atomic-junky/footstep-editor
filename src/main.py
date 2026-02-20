import logging
import sys
from pathlib import Path

import sass
from PySide6.QtWidgets import QApplication

from src.core.audio_engine import AudioEngine


_THEME_DIR = Path(__file__).parent / "ui" / "themes"

log = logging.getLogger(__name__)


class FSEAPP(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setup_style_sheet()
        self.audio_engine: AudioEngine = AudioEngine()

    def setup_style_sheet(self):
        scss_path = _THEME_DIR / "main.scss"
        compiled_css = sass.compile(filename=str(scss_path))
        self.setStyleSheet(compiled_css)
