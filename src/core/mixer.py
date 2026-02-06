import io
from typing import List
from pydub import AudioSegment


class Mixer:
    def __init__(self):
        self._segments: List[AudioSegment] = []
    
    def add_segment(self, segment: AudioSegment, volume_db: float):
        segment = segment + volume_db 
        self._segments.append(segment)
    
    def concat(self, format: str = "ogg") -> io.BytesIO:
        if len(self._segments) <= 0:
            return
        
        longest = None
        for segment in self._segments:
            if longest is None or segment.duration_seconds > longest.duration_seconds:
                longest = segment
        
        result = longest
        for segment in self._segments:
            if segment != longest:
                result = result.overlay(segment)
        
        stream: io.BytesIO = io.BytesIO()
        result.export(stream, format=format)
        return stream