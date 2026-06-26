from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QVariantAnimation, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QConicalGradient


class DonutChart(QWidget):
    """Circular progress donut chart widget with smooth transitions and rotation animation."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0.0
        self._target_value = 0.0
        self.angle_offset = 90.0
        self.is_downloading = False
        self.setFixedSize(100, 100)
        
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(300)
        self.anim.valueChanged.connect(self._on_anim_value)
        
        self.rot_timer = QTimer(self)
        self.rot_timer.timeout.connect(self._rotate_ring)
        self.rot_timer.start(50)

    def _rotate_ring(self):
        if self.is_downloading and self._value < 100.0:
            self.angle_offset = (self.angle_offset - 2.0) % 360.0
            self.update()

    def set_value(self, val, is_downloading=False):
        self.is_downloading = is_downloading
        val = min(max(float(val), 0.0), 100.0)
        if val == self._target_value:
            return
        self._target_value = val
        self.anim.stop()
        self.anim.setStartValue(self._value)
        self.anim.setEndValue(val)
        self.anim.start()

    def _on_anim_value(self, val):
        self._value = val
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        side = min(w, h)
        pen_width = max(2, int(side / 12))
        margin = pen_width + 2
        rect = QRectF(margin, margin, side - 2 * margin, side - 2 * margin)

        bg_pen = QPen(QColor("#1a1f30"), pen_width)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, 0, 360 * 16)

        if self._value > 0:
            gradient = QConicalGradient(rect.center(), self.angle_offset)
            gradient.setColorAt(0.0, QColor("#2563eb"))
            gradient.setColorAt(0.5, QColor("#3b82f6"))
            gradient.setColorAt(1.0, QColor("#2563eb"))

            progress_pen = QPen()
            progress_pen.setWidth(pen_width)
            progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            progress_pen.setBrush(gradient)
            painter.setPen(progress_pen)

            span = int(self._value * 360 / 100 * 16)
            painter.drawArc(rect, int(self.angle_offset * 16), -span)

        painter.setPen(QColor("#ffffff"))
        font_size = max(6, int(side / 5))
        font = QFont("Inter", font_size, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{int(self._value)}%")

        painter.end()
