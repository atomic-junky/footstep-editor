"""
Timeline Panel Widget.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent, QWheelEvent, QPolygonF


class TimelinePanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TimelinePanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self.timeline_view = TimelineView(self)
        layout.addWidget(self.timeline_view)


class TimelineView(QFrame):
    playhead_changed = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("TimelineView")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(180)
        self.setMouseTracking(True)

        self.duration_sec = 15.0
        self.playhead_time = 2.2
        self._is_dragging = False

        self.ruler_height = 24
        self.track_height = 46
        self.track_gap = 8
        self.left_gutter = 78
        self.right_pad = 16
        self.top_pad = 6
        self.bottom_pad = 10

        self.tracks = [
            {
                "name": "SFX",
                "clips": [
                    {"start": 0.8, "duration": 2.4, "color": "#f4a261"},
                    {"start": 4.2, "duration": 3.0, "color": "#f4a261"},
                ],
            },
        ]

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._set_playhead_from_pos(event.position())
        super().mousePressEvent(event)
    
    def wheelEvent(self, event: QWheelEvent):
        delta_sec = -event.angleDelta().y() / 120 ** 0.85
        self.duration_sec = min(max(3.0, self.duration_sec + delta_sec), 95)
        self.update()
        super().wheelEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_dragging:
            self._set_playhead_from_pos(event.position())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
        super().mouseReleaseEvent(event)

    def _set_playhead_from_pos(self, pos: QPointF):
        content_rect = self._content_rect()
        if content_rect.width() <= 1:
            return
        
        x = max(content_rect.left(), min(content_rect.right(), pos.x()))
        t = (x - content_rect.left()) / content_rect.width() * self.duration_sec
        self.playhead_time = max(0.0, min(self.duration_sec, round(t, 1)))
        self.playhead_changed.emit(self.playhead_time)
        self.update()

    def _content_rect(self) -> QRectF:
        rect = self.rect()
        return QRectF(
            self.left_gutter,
            self.top_pad,
            max(1.0, rect.width() - self.left_gutter - self.right_pad),
            max(1.0, rect.height() - self.top_pad - self.bottom_pad),
        )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        content_rect = self._content_rect()

        self._draw_ruler(painter, content_rect)
        self._draw_tracks(painter, content_rect)
        self._draw_playhead(painter, content_rect)

    def _draw_ruler(self, painter: QPainter, content_rect: QRectF):
        ruler_rect = QRectF(
            content_rect.left(),
            content_rect.top(),
            content_rect.width(),
            self.ruler_height,
        )

        painter.setPen(QPen(QColor("#dddddd"), 1))
        painter.setBrush(QBrush(QColor("#f5f5f5")))
        painter.drawRoundedRect(
            ruler_rect,
            6,
            6,
        )

        if content_rect.width() <= 1:
            return

        seconds = int(self.duration_sec) + 1
        px_per_sec = content_rect.width() / self.duration_sec
        
        painter.setPen(QPen(QColor("#b5b5b5"), 1))
        
        if px_per_sec > 80:
            self._draw_ruler_small(painter, content_rect, ruler_rect, seconds, px_per_sec)
        else:
            self._draw_ruler_medium(painter, content_rect, ruler_rect, seconds, px_per_sec)
    
    def _draw_ruler_medium(self, painter: QPainter, content_rect: QRectF, ruler_rect: QRectF, seconds: int, px_per_sec: float):
        every_sec = max(1, int(2 / (px_per_sec / 40)))
        for sec in range(0, seconds, every_sec):
            painter.setPen(QPen(QColor("#b5b5b5"), 1))
            x = content_rect.left() + sec * px_per_sec
            center = QPointF(x, ruler_rect.bottom())
            text_rect = painter.fontMetrics().boundingRect(f"{sec}s")
            text_x = x - text_rect.width() / 2
            text_y = ruler_rect.bottom() - text_rect.height()/2
            painter.drawText(text_x, text_y, f"{sec}s", )
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#b5b5b5")))
            
            center = QPointF(center.x(), ruler_rect.bottom())
            center_rect = QRectF(center.x() - 1, center.y() - 3, 2, 6)
            painter.drawRoundedRect(center_rect, 1, 1)
            
            half = x + px_per_sec * every_sec * 0.5
            if half < content_rect.right():
                center = QPointF(half, ruler_rect.bottom())
                center_rect = QRectF(center.x() - 1, center.y() - 2, 2, 4)
                painter.drawRoundedRect(center_rect, 1, 1)

    def _draw_ruler_small(self, painter: QPainter, content_rect: QRectF, ruler_rect: QRectF, seconds: int, px_per_sec: float):
        for sec in range(seconds):
            painter.setPen(QPen(QColor("#b5b5b5"), 1))
            x = content_rect.left() + sec * px_per_sec
            center = QPointF(x, ruler_rect.bottom())
            text_rect = painter.fontMetrics().boundingRect(f"{sec}s")
            text_x = x - text_rect.width() / 2
            text_y = ruler_rect.bottom() - text_rect.height()/2
            painter.drawText(text_x, text_y, f"{sec}s", )
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#b5b5b5")))
            
            center = QPointF(center.x(), ruler_rect.bottom())
            center_rect = QRectF(center.x() - 1, center.y() - 3, 2, 6)
            painter.drawRoundedRect(center_rect, 1, 1)
            
            half = x + px_per_sec * 0.5
            if half < content_rect.right():
                center = QPointF(half, ruler_rect.bottom())
                center_rect = QRectF(center.x() - 1, center.y() - 2, 2, 4)
                painter.drawRoundedRect(center_rect, 1, 1)
            
            if px_per_sec > 40:
                for tenth in range(1, 10):
                    tenth_x = x + px_per_sec * tenth * 0.1
                    if tenth_x < content_rect.right():
                        center = QPointF(tenth_x, ruler_rect.bottom())
                        painter.drawEllipse(center, 1, 1)
            elif px_per_sec * 0.5 > 20:
                quarter = x + px_per_sec * 0.25
                three_quarter = x + px_per_sec * 0.75
                if quarter < content_rect.right():
                    center = QPointF(quarter, ruler_rect.bottom())
                    painter.drawEllipse(center, 1, 1)
                if three_quarter < content_rect.right():
                    center = QPointF(three_quarter, ruler_rect.bottom())
                    painter.drawEllipse(center, 1, 1)
            
    def _draw_tracks(self, painter: QPainter, content_rect: QRectF):
        y = content_rect.top() + self.ruler_height + self.track_gap

        for track in self.tracks:
            track_rect = QRectF(
                content_rect.left(),
                y,
                content_rect.width(),
                self.track_height,
            )

            painter.setPen(QPen(QColor("#eeeeee"), 1))
            painter.setBrush(QBrush(QColor("#fafafa")))
            painter.drawRoundedRect(track_rect, 6, 6)

            painter.setPen(QPen(QColor("#9a9a9a"), 1))
            painter.drawText(
                12,
                int(track_rect.center().y()) + 5,
                track["name"],
            )

            for clip in track["clips"]:
                clip_rect = self._clip_rect(clip, track_rect)
                painter.setPen(QPen(QColor("#d48c4e"), 1))
                painter.setBrush(QBrush(QColor(clip["color"])))
                painter.drawRoundedRect(clip_rect, 6, 6)

            y += self.track_height + self.track_gap

    def _clip_rect(self, clip: dict, track_rect: QRectF) -> QRectF:
        start = clip["start"]
        duration = clip["duration"]

        px_per_sec = track_rect.width() / self.duration_sec
        x = track_rect.left() + start * px_per_sec
        width = max(8.0, duration * px_per_sec)

        return QRectF(x, track_rect.top() + 8, width, track_rect.height() - 16)

    def _draw_playhead(self, painter: QPainter, content_rect: QRectF):
        if content_rect.width() <= 1:
            return

        px_per_sec = content_rect.width() / self.duration_sec
        x = content_rect.left() + self.playhead_time * px_per_sec

        painter.setPen(QPen(QColor("#e76f51"), 2))
        painter.drawLine(
            x,
            content_rect.top() + 20,
            x,
            self.rect().bottom() - self.bottom_pad,
        )

        triangle = QPolygonF(
            [
                QPointF(x - 7, content_rect.top()),
                QPointF(x + 6, content_rect.top()),
                QPointF(x + 6, content_rect.top() + 12),
                QPointF(x - 1, content_rect.top() + 20),
                QPointF(x, content_rect.top() + 20),
                QPointF(x - 7, content_rect.top() + 12),
            ]
        )
        painter.setBrush(QBrush(QColor("#e76f51")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(triangle)
