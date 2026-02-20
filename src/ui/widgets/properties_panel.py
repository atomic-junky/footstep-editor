"""
Properties Panel Widget.

This widget represents the properties area.
"""

import numpy as np
from pathlib import Path
from random import randint

from PySide6.QtWidgets import QFrame, QHBoxLayout, QApplication
from PySide6.QtCore import Qt
from pydub import AudioSegment

from src.ui.widgets.mix_pad import MixPad
from src.core.mixer import Mixer


_ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"


class PropertiesPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PropertiesPanel")

        center_layout = QHBoxLayout(self)
        center_layout.setContentsMargins(20, 20, 20, 20)

        self.mix_pad = MixPad(self)
        self.mix_pad.handle_moved.connect(self._on_mix_pad_moved)
        self.mix_pad.pressed.connect(self._on_mix_pad_pressed)

        center_layout.addWidget(self.mix_pad, 1)
        center_layout.addStretch()

        self._segments = {}
        self._preload_segments()

    def _preload_segments(self):
        for material in ["floor", "dirt", "wood", "gravel"]:
            for idx in range(1, 22):
                file_path = _ASSETS_DIR / "sfx" / "footsteps" / material / f"Steps_{material}-{idx:03d}.ogg"
                self._segments[file_path] = AudioSegment.from_file(file_path)

    def _on_mix_pad_moved(self, x: float, y: float):
        pass

    def _on_mix_pad_pressed(self, x: float, y: float):
        app = QApplication.instance()
        mixer = Mixer()

        corners = [
            (0.0, 0.0, "floor"),
            (1.0, 0.0, "dirt"),
            (0.0, 1.0, "wood"),
            (1.0, 1.0, "gravel"),
        ]

        for corner in corners:
            cx, cy, material = corner
            idx = randint(1, 21)
            p1 = np.array([cx, cy])
            p2 = np.array([round(x, 2), round(y, 2)])
            dist = np.sqrt(np.sum((p1 - p2) ** 2))
            volume_db = max(-40.0, -20.0 * dist / 0.75)
            file_path = _ASSETS_DIR / "sfx" / "footsteps" / material / f"Steps_{material}-{idx:03d}.ogg"
            segment = self._segments[file_path]
            mixer.add_segment(segment, volume_db)

        stream = mixer.concat(format="wav")
        app.audio_engine.play(stream.getvalue())
        print(f"MixPad handle pressed: x={x:.2f}, y={y:.2f}")
