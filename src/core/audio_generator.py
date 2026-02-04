"""Simple audio generation."""

import numpy as np


class AudioGenerator:
    """Basic audio generator."""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
