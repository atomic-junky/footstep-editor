"""Main entry point for the application."""

import logging
import sys

from src.utils.ffmpeg_setup import setup_ffmpeg
from src.main import FSEAPP
from src.ui import FSEditor

logger = logging.getLogger(__name__)


def main():
    setup_ffmpeg()
    app = FSEAPP()
    window = FSEditor()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
