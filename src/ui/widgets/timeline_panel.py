"""
Timeline Panel - Simple and functional timeline with keys.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsItem, QPushButton, QWidget, QLabel
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF, QPainterPath, QIcon


class TimelinePanel(QFrame):
    """Container for timeline with playback controls."""
    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TimelinePanel")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.control_bar = self._create_control_bar()
        layout.addWidget(self.control_bar)
        
        self.timeline = TimelineView(self)
        layout.addWidget(self.timeline)
        
        self.timeline.playhead_changed.connect(self._update_time_display)
    
    def _update_time_display(self, time_sec: float):
        """Update time display label."""
        minutes = int(time_sec // 60)
        seconds = int(time_sec % 60)
        milliseconds = int((time_sec % 1) * 1000)
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}")
    
    def _create_control_bar(self):
        """Create playback control bar."""
        control_widget = QWidget()
        control_widget.setStyleSheet("background: #f5f5f5; border-bottom: 1px solid #cccccc;")
        control_widget.setFixedHeight(40)
        
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(10, 5, 10, 5)
        control_layout.setSpacing(5)
        
        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedSize(32, 30)
        self.btn_play.setToolTip("Play (Space)")
        self.btn_play.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
            QPushButton:pressed {
                background: #3d8b40;
            }
        """)
        self.btn_play.clicked.connect(self.play_clicked.emit)
        
        self.btn_pause = QPushButton("⏸")
        self.btn_pause.setFixedSize(32, 30)
        self.btn_pause.setToolTip("Pause")
        self.btn_pause.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e68900;
            }
            QPushButton:pressed {
                background: #cc7a00;
            }
        """)
        self.btn_pause.clicked.connect(self.pause_clicked.emit)
        
        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedSize(32, 30)
        self.btn_stop.setToolTip("Stop")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #da190b;
            }
            QPushButton:pressed {
                background: #c41408;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        
        control_layout.addWidget(self.btn_play)
        control_layout.addWidget(self.btn_pause)
        control_layout.addWidget(self.btn_stop)
        
        self.time_label = QLabel("00:00.00")
        self.time_label.setStyleSheet("""
            QLabel {
                background: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px 10px;
                font-family: monospace;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.time_label.setMinimumWidth(90)
        control_layout.addWidget(self.time_label)
        
        control_layout.addStretch()
        
        return control_widget


class TimelineView(QGraphicsView):
    """Simple timeline view with keys."""
    
    playhead_changed = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setStyleSheet("background: #ffffff; border: 1px solid #e0e0e0;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        self.LEFT_MARGIN = 100
        self.RIGHT_MARGIN = 30
        self.RULER_HEIGHT = 40
        self.TRACK_HEIGHT = 60
        self.TRACK_GAP = 5
        
        self.max_duration_sec = 15 * 60
        self.playhead_sec = 0.0
        self.px_per_sec = 40.0
        self.dragging_playhead = False
        self.panning = False
        self.space_pressed = False
        self.last_pan_pos = None
        
        # Items
        self.playhead_line = None
        self.playhead_handle = None
        self.playhead_time_text = None
        self.track_headers = []
        self.ruler_header = None
        
        self.tracks = [
            {"name": "SFX", "keys": [2.5, 5.0, 8.3, 12.0]},
            {"name": "Footsteps", "keys": [1.0, 3.5, 6.8, 10.2]},
        ]
        
        self.horizontalScrollBar().valueChanged.connect(self.update_headers_position)
        
        self.build_timeline()
    
    def build_timeline(self):
        """Build complete timeline."""
        # Disable updates during rebuild for performance
        self.setUpdatesEnabled(False)
        
        self.scene.clear()
        
        self.playhead_line = None
        self.playhead_handle = None
        self.playhead_time_text = None
        self.track_headers = []
        self.ruler_header = None
        
        scene_width = self.max_duration_sec * self.px_per_sec
        
        num_tracks = len(self.tracks)
        total_height = self.RULER_HEIGHT + num_tracks * (self.TRACK_HEIGHT + self.TRACK_GAP) + 20
        
        self.scene.setSceneRect(0, 0, self.LEFT_MARGIN + scene_width + self.RIGHT_MARGIN, total_height)
        
        y = self.RULER_HEIGHT
        for track in self.tracks:
            self.draw_track(track, y, scene_width)
            y += self.TRACK_HEIGHT + self.TRACK_GAP
        
        self.draw_ruler(scene_width)
        
        self.update_playhead()
        
        self.update_headers_position()
        
        self.setUpdatesEnabled(True)
    
    def draw_ruler(self, width: float):
        """Draw time ruler."""
        y = 0
        h = self.RULER_HEIGHT
        x_start = self.LEFT_MARGIN
        
        bg = self.scene.addRect(x_start, y, width + self.RIGHT_MARGIN, h, QPen(Qt.PenStyle.NoPen), QBrush(QColor("#f5f5f5")))
        bg.setZValue(40)
        
        self.ruler_header = self.scene.addRect(
            0, y, self.LEFT_MARGIN, h,
            QPen(Qt.PenStyle.NoPen),
            QBrush(QColor("#e0e0e0"))
        )
        self.ruler_header.setZValue(50)
        
        interval = self.get_time_interval()
        max_time = int((width / self.px_per_sec) + 1)
        ruler_range = map(lambda x: x/10.0, range(0, max_time, int(interval*10.0)))
        
        for t in ruler_range:
            x = x_start + t * self.px_per_sec
            
            if x > x_start + width:
                break
            
            tick = self.scene.addLine(x, h - 10, x, h, QPen(QColor("#888888"), 1))
            tick.setZValue(45)
            
            label = self.format_time(t)
            text = self.scene.addText(label)
            text.setFont(QFont("Arial", 9))
            text.setDefaultTextColor(QColor("#333333"))
            text.setPos(x - text.boundingRect().width() / 2, 8)
            text.setZValue(45)
    
    def get_time_interval(self) -> float:
        """Get time interval for ruler ticks based on zoom level."""
        if self.px_per_sec > 90:
            return 0.5
        elif self.px_per_sec > 60:
            return 1.0
        elif self.px_per_sec > 30:
            return 2.0
        elif self.px_per_sec > 15:
            return 5.0
        elif self.px_per_sec > 8:
            return 10.0
        elif self.px_per_sec > 4:
            return 30.0
        elif self.px_per_sec > 2:
            return 60.0
        else:
            return 120.0
    
    def format_time(self, seconds: int) -> str:
        """Format time in seconds to readable string."""
        if seconds < 60:
            return f"{seconds}s"
        else:
            minutes = seconds // 60
            secs = seconds % 60
            if secs == 0:
                return f"{minutes}m"
            else:
                return f"{minutes}m{secs}s"
    
    def draw_track(self, track: dict, y: float, width: float):
        """Draw a track with keys."""
        x_start = self.LEFT_MARGIN
        
        header_bg = self.scene.addRect(
            0, y, self.LEFT_MARGIN, self.TRACK_HEIGHT,
            QPen(QColor("#cccccc"), 1),
            QBrush(QColor("#f0f0f0"))
        )
        header_bg.setZValue(50)
        
        name_text = self.scene.addText(track["name"])
        name_text.setFont(QFont("Arial", 10))
        name_text.setDefaultTextColor(QColor("#333333"))
        name_text.setPos(10, y + self.TRACK_HEIGHT / 2 - 8)
        name_text.setZValue(51)
        
        self.track_headers.append((header_bg, name_text))
        
        lane = self.scene.addRect(
            x_start, y, width, self.TRACK_HEIGHT,
            QPen(QColor("#dddddd"), 1),
            QBrush(QColor("#fafafa"))
        )
        lane.setZValue(-10)
        
        for key_time in track["keys"]:
            key_x = key_time * self.px_per_sec
            if key_x >= 0 and key_x <= width:
                self.draw_key(key_time, y + self.TRACK_HEIGHT / 2)
    
    def draw_key(self, time_sec: float, y: float):
        """Draw a key (diamond) at time position."""
        x = self.LEFT_MARGIN + time_sec * self.px_per_sec
        size = 6
        
        diamond = QPolygonF([
            QPointF(x, y - size),
            QPointF(x + size, y),
            QPointF(x, y + size),
            QPointF(x - size, y),
        ])
        
        key_item = self.scene.addPolygon(
            diamond,
            QPen(QColor("#e67e22"), 2),
            QBrush(QColor("#f39c12"))
        )
        key_item.setZValue(10)
    
    def update_playhead(self):
        """Update playhead position."""
        # Remove old playhead elements
        if self.playhead_line:
            self.scene.removeItem(self.playhead_line)
        if self.playhead_handle:
            self.scene.removeItem(self.playhead_handle)
        if self.playhead_time_text:
            self.scene.removeItem(self.playhead_time_text)
        
        x = self.LEFT_MARGIN + self.playhead_sec * self.px_per_sec
        
        num_tracks = len(self.tracks)
        line_height = self.RULER_HEIGHT + num_tracks * (self.TRACK_HEIGHT + self.TRACK_GAP)
        
        self.playhead_line = self.scene.addLine(
            x, 0, x, line_height,
            QPen(QColor("#e74c3c"), 2)
        )
        self.playhead_line.setZValue(100)
        
        minutes = int(self.playhead_sec // 60)
        seconds = int(self.playhead_sec % 60)
        milliseconds = int((self.playhead_sec % 1) * 100)
        time_text = f"{seconds:02d}:{milliseconds:02d}"
        if minutes > 0:
            time_text = f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
        
        temp_text = self.scene.addText(time_text)
        temp_text.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        text_width = temp_text.boundingRect().width()
        text_height = temp_text.boundingRect().height()
        self.scene.removeItem(temp_text)
        
        pill_width = text_width + 6
        pill_height = 18
        pill_x = x - pill_width / 2
        pill_y = 2
        pill_radius = pill_height / 2
        
        pill_path = QPainterPath()
        pill_path.addRoundedRect(
            QRectF(pill_x, pill_y, pill_width, pill_height),
            pill_radius, pill_radius
        )
        
        self.playhead_handle = self.scene.addPath(
            pill_path,
            QPen(Qt.PenStyle.NoPen),
            QBrush(QColor("#e74c3c"))
        )
        self.playhead_handle.setZValue(101)
        
        self.playhead_time_text = self.scene.addText(time_text)
        self.playhead_time_text.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        self.playhead_time_text.setDefaultTextColor(QColor("#ffffff"))
        self.playhead_time_text.setPos(
            x - text_width / 2,
            pill_y + (pill_height - text_height) / 2 + 1
        )
        self.playhead_time_text.setZValue(102)
    
    def resizeEvent(self, event):
        """Handle view resize."""
        super().resizeEvent(event)
        self.build_timeline()
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.MiddleButton or (event.button() == Qt.MouseButton.LeftButton and self.space_pressed):
            # Start panning with middle button or space + left button
            self.panning = True
            self.last_pan_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            
            if scene_pos.y() < self.RULER_HEIGHT:
                self.dragging_playhead = True
                self.set_playhead_from_x(scene_pos.x())
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move."""
        if self.panning and self.last_pan_pos:
            # Pan the view
            current_pos = event.position().toPoint()
            delta = current_pos - self.last_pan_pos
            self.last_pan_pos = current_pos
            
            # Update scroll position
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
        elif self.dragging_playhead:
            scene_pos = self.mapToScene(event.position().toPoint())
            self.set_playhead_from_x(scene_pos.x())
        elif self.space_pressed:
            # Show open hand cursor when space is pressed but not dragging
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.MouseButton.MiddleButton or (event.button() == Qt.MouseButton.LeftButton and self.panning):
            self.panning = False
            self.last_pan_pos = None
            if self.space_pressed:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.LeftButton:
            self.dragging_playhead = False
        
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        """Handle zoom with mouse wheel around mouse position."""
        mouse_pos = self.mapToScene(event.position().toPoint())
        mouse_time = (mouse_pos.x() - self.LEFT_MARGIN) / self.px_per_sec
        
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        old_px_per_sec = self.px_per_sec
        self.px_per_sec *= zoom_factor
        
        view_width = self.width() - self.LEFT_MARGIN
        min_zoom = max(1.0, view_width / self.max_duration_sec)
        self.px_per_sec = max(min_zoom, min(150.0, self.px_per_sec))
        
        self.build_timeline()
        
        new_mouse_x = self.LEFT_MARGIN + mouse_time * self.px_per_sec
        old_mouse_x = mouse_pos.x()
        
        scroll_delta = int(new_mouse_x - old_mouse_x)
        self.horizontalScrollBar().setValue(
            self.horizontalScrollBar().value() + scroll_delta
        )
    
    def set_playhead_from_x(self, scene_x: float):
        """Set playhead from scene x coordinate."""
        time = (scene_x - self.LEFT_MARGIN) / self.px_per_sec
        self.playhead_sec = max(0.0, time)
        self.update_playhead()
        self.playhead_changed.emit(self.playhead_sec)
    
    def update_headers_position(self):
        """Update track headers position to keep them visible during scroll."""
        scroll_x = self.horizontalScrollBar().value()
        
        if self.ruler_header:
            self.ruler_header.setPos(scroll_x, 0)
        
        for header_bg, name_text in self.track_headers:
            rect = header_bg.rect()
            y = header_bg.pos().y()
            
            header_bg.setPos(scroll_x, y)
            
            text_y = name_text.pos().y()
            name_text.setPos(scroll_x + 10, text_y)
    
    def keyPressEvent(self, event):
        """Handle key press."""
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.space_pressed = True
            if not self.panning:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Handle key release."""
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.space_pressed = False
            if not self.panning:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().keyReleaseEvent(event)
