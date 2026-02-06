import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
import sass

from src.core.audio_engine import AudioEngine


log = logging.getLogger(__name__)


class FSEAPP(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setup_style_sheet()
        self.audio_engine: AudioEngine = AudioEngine()
        

    def setup_style_sheet(self):
        compiled_css = sass.compile(filename="src/ui/themes/main.scss")
        self.setStyleSheet(compiled_css)