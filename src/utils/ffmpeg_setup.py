"""
Configure pydub to use the ffmpeg binary bundled via imageio-ffmpeg.

imageio-ffmpeg ships ffmpeg as a Python package (installed via pip), which
allows PyInstaller to bundle it automatically.
"""

import logging
import os

log = logging.getLogger(__name__)


def get_ffmpeg_path() -> str | None:
    """Return the path to the ffmpeg binary provided by imageio-ffmpeg, or None."""
    try:
        import imageio_ffmpeg

        path = imageio_ffmpeg.get_ffmpeg_exe()
        log.debug("Found ffmpeg via imageio-ffmpeg: %s", path)
        return path
    except Exception as exc:
        log.warning("imageio-ffmpeg not available, falling back to system ffmpeg: %s", exc)
        return None


def setup_ffmpeg() -> None:
    """
    Configure pydub (and the FFMPEG_BINARY env-var) to use the bundled ffmpeg.

    Must be called before any pydub AudioSegment operations.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        log.warning("No bundled ffmpeg found. pydub will rely on a system-installed ffmpeg.")
        return

    os.environ["FFMPEG_BINARY"] = ffmpeg_path

    try:
        from pydub import AudioSegment

        AudioSegment.converter = ffmpeg_path
        log.info("pydub configured to use ffmpeg at: %s", ffmpeg_path)
    except ImportError:
        log.warning("pydub is not installed; FFMPEG_BINARY env-var set anyway.")
