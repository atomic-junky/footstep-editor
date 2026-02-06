import threading
import time
from typing import Optional, List, Tuple, Union
from PySide6.QtCore import QObject, Signal
import miniaudio


class _AbstractAudioFile:
    def __init__(self, stream: bytes):
        decoded = miniaudio.decode(stream)
        
        self.sample_rate = decoded.sample_rate
        self.nchannels = decoded.nchannels
        self.duration = len(decoded.samples) / decoded.sample_rate / decoded.nchannels
        self.position = 0


class AudioEngine(QObject):
    playback_started = Signal()
    playback_stopped = Signal()
    
    def __init__(self) -> None:
        super().__init__()
        self._playback_threads: List[threading.Thread] = []
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._active_count = 0
    
    def play(self, stream: Union[bytes, List[bytes]]) -> None:        
        tracks: List[bytes] = []
        if isinstance(stream, bytes):
            tracks.append(stream)
        else:
            tracks = stream
            
        if not tracks:
            return

        with self._lock:
            self.playback_started.emit()
            
            for stream_data in tracks:
                t = threading.Thread(
                    target=self._playback_worker, 
                    args=(stream_data,), 
                    daemon=True
                )
                self._playback_threads.append(t)
                self._active_count += 1
                t.start()
    
    def stop(self) -> None:
        """Stop all currently playing audio."""
        self._stop_event.set()
        with self._lock:
            self._playback_threads = [t for t in self._playback_threads if t.is_alive()]

    def _playback_worker(self, stream_data: bytes) -> None:
        try:
            stream = miniaudio.stream_memory(stream_data)
            
            with miniaudio.PlaybackDevice() as device:
                device.start(stream)
                device.abstract_audio_file = _AbstractAudioFile(stream_data)
                self._wait_for_playback(device)
        except Exception as e:
            print(f"Playback error for stream data: {e}")
        finally:
            with self._lock:
                self._active_count -= 1
                if self._active_count <= 0:
                    self._active_count = 0
                    self.playback_stopped.emit()
    
    def _wait_for_playback(self, device: miniaudio.PlaybackDevice) -> None:
        start_time = time.time()
        file_infos = device.abstract_audio_file
        
        while not self._stop_event.is_set():
            elapsed = time.time() - start_time
            file_infos.position = elapsed
            
            time.sleep(0.05)

            if elapsed >= file_infos.duration and file_infos.duration > 0:
                break
