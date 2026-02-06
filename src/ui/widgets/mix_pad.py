from PySide6.QtWidgets import QFrame, QSizePolicy, QLabel
from PySide6.QtCore import Qt, QEvent, QPointF, Signal, QRectF
from PySide6.QtGui import QMouseEvent, QPainter, QColor, QPen, QBrush, QRegion

class MixPad(QFrame):
    handle_moved = Signal(float, float)
    pressed = Signal(float, float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._debug = False
        self.handle_position = QPointF(0.5, 0.5)
        self.is_hovering = False
        self.is_pressing = False
        
        self.setObjectName("MixPad")
        
        self.setMinimumSize(150, 150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.setMouseTracking(True)
        

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self._get_square_rect().toRect()
        self.setMask(QRegion(rect))

    def _get_square_rect(self) -> QRectF:
        side = min(self.width(), self.height())
        x = (self.width() - side) / 2
        y = (self.height() - side) / 2
        return QRectF(x, y, side, side)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.is_hovering = True
        if self.is_pressing:
             self._update_position(event.position())
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):       
        self.is_pressing = True
        self._update_position(event.position())
        self.pressed.emit(self.handle_position.x(), self.handle_position.y())
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        self.is_pressing = False
        self._update_position(event.position())
        super().mouseReleaseEvent(event)
    
    def leaveEvent(self, event: QEvent):
        self.is_hovering = False
        self.update()
        super().leaveEvent(event)

    def _update_position(self, pos: QPointF):
        rect = self._get_square_rect()
        
        x = (pos.x() - rect.x()) / rect.width()
        y = (pos.y() - rect.y()) / rect.height()
        
        x = max(0.0, min(1.0, x))
        y = max(0.0, min(1.0, y))
        
        self.handle_position = QPointF(x, y)
        self.handle_moved.emit(x, y)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self._get_square_rect()
        side = rect.width()
        
        painter.translate(rect.topLeft())

        arc_size = side * 0.75
        
        painter.setPen(QPen(QColor("#d9c7f7"), 1))
        
        painter.drawEllipse(QPointF(0, 0), arc_size, arc_size)
        painter.drawEllipse(QPointF(side, 0), arc_size, arc_size)
        painter.drawEllipse(QPointF(0, side), arc_size, arc_size)
        painter.drawEllipse(QPointF(side, side), arc_size, arc_size)

        cx = self.handle_position.x() * side
        cy = self.handle_position.y() * side
        
        painter.setPen(QPen(QColor("#d9c7f7"), 1, Qt.PenStyle.DashLine))
        
        painter.drawLine(cx, 0, cx, side)
        painter.drawLine(0, cy, side, cy)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#8b5cf6")))
        if self.is_pressing:
            painter.setBrush(QBrush(QColor("#7c3aed")))
        painter.drawEllipse(QPointF(cx, cy), 6, 6)
