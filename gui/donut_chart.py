from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QConicalGradient


class DonutChart(QWidget):
    """Circular progress donut chart widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self.setFixedSize(170, 170)

    def set_value(self, val):
        self._value = min(max(val, 0), 100)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        side = min(w, h)
        margin = 12
        rect = QRectF(margin, margin, side - 2 * margin, side - 2 * margin)

        # Background ring
        bg_pen = QPen(QColor("#1a1f30"), 12)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Progress ring with gradient
        if self._value > 0:
            gradient = QConicalGradient(rect.center(), 90)
            gradient.setColorAt(0.0, QColor("#2563eb"))
            gradient.setColorAt(0.5, QColor("#06b6d4"))
            gradient.setColorAt(1.0, QColor("#2563eb"))

            progress_pen = QPen()
            progress_pen.setWidth(12)
            progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            progress_pen.setBrush(gradient)
            painter.setPen(progress_pen)

            span = int(self._value * 360 / 100 * 16)
            painter.drawArc(rect, 90 * 16, -span)

        # Center text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Inter", 26, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{int(self._value)}%")

        painter.end()
