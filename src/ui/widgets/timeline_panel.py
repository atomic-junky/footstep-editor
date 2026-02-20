"""
Timeline Panel - Simple and functional timeline with keys.
"""

from typing import Optional, List, Tuple, Dict, Any, Union

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsItem, QPushButton, QWidget, QLabel, QGraphicsLineItem, QGraphicsPathItem, QGraphicsTextItem, QGraphicsRectItem
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QEvent, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF, QPainterPath, QIcon, QResizeEvent, QMouseEvent, QWheelEvent, QKeyEvent


class TimelinePanel(QFrame):
    """Container for timeline with playback controls."""
    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
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
    
    def _update_time_display(self, time_sec: float) -> None:
        """Update time display label."""
        minutes = int(time_sec // 60)
        seconds = int(time_sec % 60)
        milliseconds = int((time_sec % 1) * 1000)
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}")
    
    def _create_control_bar(self) -> QWidget:
        """Create playback control bar."""
        control_widget = QWidget()
        control_widget.setFixedHeight(40)
        
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(10, 5, 10, 5)
        control_layout.setSpacing(5)
        
        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedSize(32, 30)
        self.btn_play.setToolTip("Play (Space)")
        self.btn_play.clicked.connect(self.play_clicked.emit)
        
        self.btn_pause = QPushButton("⏸")
        self.btn_pause.setFixedSize(32, 30)
        self.btn_pause.setToolTip("Pause")
        self.btn_pause.clicked.connect(self.pause_clicked.emit)
        
        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setFixedSize(32, 30)
        self.btn_stop.setToolTip("Stop")
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        
        control_layout.addWidget(self.btn_play)
        control_layout.addWidget(self.btn_pause)
        control_layout.addWidget(self.btn_stop)
        
        self.time_label = QLabel("00:00.00")
        self.time_label.setMinimumWidth(90)
        control_layout.addWidget(self.time_label)
        
        control_layout.addStretch()
        
        return control_widget


class TimelineView(QGraphicsView):
    """Simple timeline view with keys."""
    
    playhead_changed = Signal(float)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Setup
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        self.LEFT_MARGIN = 100
        self.RIGHT_MARGIN = 30
        self.RULER_HEIGHT = 20
        self.TRACK_HEIGHT = 30
        self.TRACK_GAP = 5
        
        # Handle configuration
        self.HANDLE_WIDTH = 2
        self.HANDLE_COLOR = QColor("#000000")
        self.HANDLE_GRAB_MARGIN = 10
        
        self.file_start_sec: float = 0.0
        self.file_duration_sec: float = 30.0
        self.playhead_sec: float = 0.0
        self.px_per_sec: float = 40.0
        self.dragging_playhead: bool = False
        self.dragging_start_handle: bool = False
        self.dragging_duration_handle: bool = False
        self.panning: bool = False
        self.space_pressed: bool = False
        self.last_pan_pos: Optional[QPoint] = None
        
        # Items
        self.playhead_line: Optional[QGraphicsLineItem] = None
        self.playhead_handle: Optional[QGraphicsPathItem] = None
        self.playhead_time_text: Optional[QGraphicsTextItem] = None
        self.start_handle: Optional[QGraphicsRectItem] = None
        self.start_line: Optional[QGraphicsLineItem] = None
        self.start_overlay: Optional[QGraphicsRectItem] = None
        self.duration_handle: Optional[QGraphicsRectItem] = None
        self.duration_line: Optional[QGraphicsLineItem] = None
        self.duration_overlay: Optional[QGraphicsRectItem] = None
        self.track_headers: List[Tuple[QGraphicsRectItem, QGraphicsTextItem]] = []
        self.ruler_safe_margin: Optional[QGraphicsRectItem] = None
        
        self.tracks: List[Dict[str, Any]] = [
            {"keys": [2.5, 5.0, 8.3, 12.0]},
            {"keys": [1.0, 3.5, 6.8, 10.2]},
        ]
        
        self.horizontalScrollBar().valueChanged.connect(self.update_headers_position)
        
        self.build_timeline()
    
    def build_timeline(self) -> None:
        """Build complete timeline."""
        self.setUpdatesEnabled(False)
        
        self.scene.clear()
        
        self.playhead_line = None
        self.playhead_handle = None
        self.playhead_time_text = None
        self.start_handle = None
        self.start_line = None
        self.start_overlay = None
        self.duration_handle = None
        self.duration_line = None
        self.duration_overlay = None
        self.ruler_safe_margin = None
        
        scene_width = self.size().width()
        
        num_tracks = len(self.tracks)
        total_height = self.RULER_HEIGHT + num_tracks * (self.TRACK_HEIGHT + self.TRACK_GAP) + 20
        
        self.scene.setSceneRect(0, 0, self.LEFT_MARGIN + scene_width + self.RIGHT_MARGIN, total_height)
        
        y = self.RULER_HEIGHT
        for track in self.tracks:
            self.draw_track(track, y, scene_width)
            y += self.TRACK_HEIGHT + self.TRACK_GAP
        
        self.draw_ruler(scene_width)
        
        self.draw_duration_handle(total_height)
        
        self.update_playhead()
        
        self.update_headers_position()
        
        self.setUpdatesEnabled(True)
    
    def draw_ruler(self, width: float) -> None:
        """Draw time ruler."""
        y = 0
        h = self.RULER_HEIGHT
        x_start = self.LEFT_MARGIN
        
        bg = self.scene.addRect(x_start, y, width + self.RIGHT_MARGIN, h, QPen(Qt.PenStyle.NoPen), QBrush(QColor("#f5f5f5")))
        bg.setZValue(41)
        
        self.ruler_safe_margin = self.scene.addRect(
            0, y, x_start, h,
            QPen(Qt.PenStyle.NoPen),
            QBrush(QColor("#e0e0e0"))
        )
        self.ruler_safe_margin.setZValue(40)
        
        lane = self.scene.addLine(
            x_start, self.RULER_HEIGHT, x_start + width, self.RULER_HEIGHT,
            QPen(QColor("#dddddd"), 1)
        )
        lane.setZValue(-10)
        
        interval = self.get_time_interval()
        max_time = (width / self.px_per_sec) + 1
        
        t = 0
        while t <= max_time:
            x = x_start + t * self.px_per_sec
            x_half = x + (interval * self.px_per_sec / 2)
            
            if x > x_start + width:
                break
            
            half = self.scene.addLine(x_half, h/2-3, x_half, h/2+3, QPen(QColor("#888888"), 1))
            half.setZValue(45)
            
            # Add two intermediate ticks between the half tick
            for i in range(1, 6):
                x_intermediate = x + (i * interval * self.px_per_sec / 6)
                intermediate_tick = self.scene.addLine(x_intermediate, h/2-1, x_intermediate, h/2+1, QPen(QColor("#C2C2C2"), 1))
                intermediate_tick.setZValue(45)
            
            label = self.format_time(t)
            text = self.scene.addText(label)
            text.setFont(QFont("Arial", 8))
            text.setDefaultTextColor(QColor("#888888"))
            text.setPos(x - text.boundingRect().width() / 2, self.RULER_HEIGHT/2 - 10)
            text.setZValue(45)
            
            t += interval
    
    def get_time_interval(self) -> float:
        """Get time interval for ruler ticks based on zoom level."""
        if self.px_per_sec > 120:
            return 1.0
        elif self.px_per_sec > 60:
            return 2.0
        elif self.px_per_sec > 30:
            return 5.0
        elif self.px_per_sec > 15:
            return 10.0
        elif self.px_per_sec > 8:
            return 15.0
        elif self.px_per_sec > 2:
            return 30.0
        else:
            return 60.0
    
    def format_time(self, seconds: float) -> str:
        """Format time in seconds to readable string."""
        if seconds < 60:
            return f"{simplify_number(seconds)}s"
        else:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            if secs == 0:
                return f"{minutes}m"
            else:
                return f"{minutes}m{secs}s"
    
    def draw_track(self, track: Dict[str, Any], y: float, width: float) -> None:
        """Draw a track with keys."""
        x_start = 0
        
        lane = self.scene.addLine(
            x_start, y+self.TRACK_HEIGHT/2, x_start + width, y+self.TRACK_HEIGHT/2,
            QPen(QColor("#dddddd"), 1)
        )
        lane.setZValue(-10)
        
        for key_time in track["keys"]:
            key_x = key_time * self.px_per_sec
            if key_x >= 0 and key_x <= width:
                self.draw_key(key_time, y + self.TRACK_HEIGHT / 2)
    
    def draw_key(self, time_sec: float, y: float) -> None:
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
    
    def draw_duration_handle(self, total_height: float) -> None:
        """Draw start and duration handles to define file bounds."""
        x_start = self.LEFT_MARGIN + self.file_start_sec * self.px_per_sec
        x_end = self.LEFT_MARGIN + self.file_duration_sec * self.px_per_sec
        
        scene_rect = self.scene.sceneRect()
        overlay_width_end = scene_rect.width() - x_end
        overlay_width_start = x_start
        overlays = [
            (0, 0, overlay_width_start),
            (x_end, 0, overlay_width_end)
        ]
        
        for x, y, w in overlays:
            if w <= 0:
                continue
            overlay = self.scene.addRect(
                x, y, w, total_height,
                QPen(Qt.PenStyle.NoPen),
                QBrush(QColor(200, 200, 200, 60))
            )
            overlay.setZValue(100)
        
        
        line_color = QColor("#888888")
        lines = [x_start, x_end]
        
        for line_x in lines:
            line = self.scene.addLine(
                line_x, 0, line_x, total_height,
                QPen(line_color, 1, Qt.PenStyle.DashLine)
             )
            line.setZValue(90)
        
        # Create start handle
        self.start_handle = self.scene.addRect(
            x_start - self.HANDLE_WIDTH/2, 0, self.HANDLE_WIDTH, self.RULER_HEIGHT,
            QPen(self.HANDLE_COLOR, 1),
            QBrush(self.HANDLE_COLOR)
        )
        self.start_handle.setZValue(105)
        self.start_handle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.start_handle.setCursor(Qt.CursorShape.SizeHorCursor)
        
        # Create duration handle
        self.duration_handle = self.scene.addRect(
            x_end - self.HANDLE_WIDTH/2, 0, self.HANDLE_WIDTH, self.RULER_HEIGHT,
            QPen(self.HANDLE_COLOR, 1),
            QBrush(self.HANDLE_COLOR)
        )
        self.duration_handle.setZValue(105)
        self.duration_handle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.duration_handle.setCursor(Qt.CursorShape.SizeHorCursor)
    
    def update_playhead(self) -> None:
        """Update playhead position."""
        if self.playhead_line:
            self.scene.removeItem(self.playhead_line)
        if self.playhead_handle:
            self.scene.removeItem(self.playhead_handle)
        if self.playhead_time_text:
            self.scene.removeItem(self.playhead_time_text)
        
        x = self.LEFT_MARGIN + self.playhead_sec * self.px_per_sec
        line_height = self.scene.sceneRect().height()
        
        self.playhead_line = self.scene.addLine(
            x, 0, x, line_height,
            QPen(QColor("#e74c3c"), 2)
        )
        self.playhead_line.setZValue(140)
        
        head_path = QPainterPath()
        rect_radius = 4
        rect_width = self.RULER_HEIGHT*0.5+4
        rect_height = self.RULER_HEIGHT*0.5
        triangle_width = rect_width
        triangle_height = self.RULER_HEIGHT*0.5
        rect_x = x - rect_width/2
        rect_y = self.RULER_HEIGHT - rect_height-triangle_height
        head_path.addRoundedRect(
            QRectF(rect_x, rect_y, rect_width, rect_height),
            rect_radius, 0
        )
        head_path.addPolygon(QPolygonF([
            QPointF(x, rect_y + rect_height + triangle_height),
            QPointF(x - triangle_width / 2, rect_y + rect_height),
            QPointF(x + triangle_width / 2, rect_y + rect_height),
        ]))
        
        self.playhead_handle = self.scene.addPath(
            head_path,
            QPen(Qt.PenStyle.NoPen),
            QBrush(QColor("#e74c3c"))
        )
        self.playhead_handle.setZValue(150)
    
    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle view resize."""
        super().resizeEvent(event)
        self.build_timeline()
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press."""
        
        if event.button() == Qt.MouseButton.MiddleButton or (event.button() == Qt.MouseButton.LeftButton and self.space_pressed):
            self.panning = True
            self.last_pan_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.position().toPoint())
            if scene_pos.y() >= self.RULER_HEIGHT:
                return
            
            # Priority: playhead > start handle > duration handle
            # Check playhead first (highest priority)
            if self.playhead_handle and self._is_near_handle(scene_pos, self.playhead_handle):
                self.dragging_playhead = True
                self.set_playhead_from_x(scene_pos.x())
                event.accept()
                return
            
            # Check start handle
            if self.start_handle and self._is_near_handle(scene_pos, self.start_handle):
                self.dragging_start_handle = True
                event.accept()
                return
            
            # Check duration handle
            if self.duration_handle and self._is_near_handle(scene_pos, self.duration_handle):
                self.dragging_duration_handle = True
                event.accept()
                return
            
            # Default: drag playhead
            self.dragging_playhead = True
            self.set_playhead_from_x(scene_pos.x())
        
        super().mousePressEvent(event)
    
    def _is_near_handle(self, scene_pos: QPointF, handle: Union[QGraphicsPathItem, QGraphicsRectItem]) -> bool:
        """Check if mouse position is near a handle."""
        handle_rect = handle.boundingRect()
        handle_pos = handle.pos()
        handle_x = handle_rect.x() + handle_pos.x() + handle_rect.width() / 2
        return abs(scene_pos.x() - handle_x) < self.HANDLE_GRAB_MARGIN
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move."""
        if self.panning and self.last_pan_pos:
            current_pos = event.position().toPoint()
            delta = current_pos - self.last_pan_pos
            self.last_pan_pos = current_pos
            
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
        elif self.dragging_start_handle:
            scene_pos = self.mapToScene(event.position().toPoint())
            new_start = (scene_pos.x() - self.LEFT_MARGIN) / self.px_per_sec
            self.file_start_sec = max(0.0, min(new_start, self.file_duration_sec - 1.0))
            self.build_timeline()
            event.accept()
        elif self.dragging_duration_handle:
            scene_pos = self.mapToScene(event.position().toPoint())
            new_duration = (scene_pos.x() - self.LEFT_MARGIN) / self.px_per_sec
            self.file_duration_sec = max(self.file_start_sec + 1.0, new_duration)
            self.build_timeline()
            event.accept()
        elif self.dragging_playhead:
            scene_pos = self.mapToScene(event.position().toPoint())
            self.set_playhead_from_x(scene_pos.x())
        elif self.space_pressed:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
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
            self.dragging_start_handle = False
            self.dragging_duration_handle = False
        
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle zoom with mouse wheel around mouse position."""
        mouse_pos = self.mapToScene(event.position().toPoint())
        mouse_time = (mouse_pos.x() - self.LEFT_MARGIN) / self.px_per_sec
        
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        self.px_per_sec *= zoom_factor
        
        view_width = self.width() - self.LEFT_MARGIN
        min_zoom = max(1.0, view_width / 900)  # 15 minutes max for min zoom
        self.px_per_sec = max(min_zoom, min(150.0, self.px_per_sec))
        
        self.build_timeline()
        
        new_mouse_x = self.LEFT_MARGIN + mouse_time * self.px_per_sec
        old_mouse_x = mouse_pos.x()
        
        scroll_delta = int(new_mouse_x - old_mouse_x)
        self.horizontalScrollBar().setValue(
            self.horizontalScrollBar().value() + scroll_delta
        )
    
    def set_playhead_from_x(self, scene_x: float) -> None:
        """Set playhead from scene x coordinate."""
        time = (scene_x - self.LEFT_MARGIN) / self.px_per_sec
        self.playhead_sec = max(0.0, time)
        self.update_playhead()
        self.playhead_changed.emit(self.playhead_sec)
    
    def update_headers_position(self) -> None:
        """Update track headers position to keep them visible during scroll."""
        scroll_x = self.horizontalScrollBar().value()
        
        for header_bg, name_text in self.track_headers:
            y = header_bg.pos().y()
            
            header_bg.setPos(scroll_x, y)
            
            text_y = name_text.pos().y()
            name_text.setPos(scroll_x + 10, text_y)
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press."""
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.space_pressed = True
            if not self.panning:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        """Handle key release."""
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.space_pressed = False
            if not self.panning:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().keyReleaseEvent(event)


def simplify_number(num: float) -> str:
    """Simplify number to 1 decimal place if possible."""
    if num.is_integer():
        return str(int(num))
    else:
        return f"{num:.1f}"