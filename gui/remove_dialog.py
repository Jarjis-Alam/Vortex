import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QFrame, QWidget, QGraphicsDropShadowEffect, QApplication
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QPointF, QRectF, QTimer
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QFontMetrics, QPainterPath
)

class WarningIconWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.use_circle = True # Use the user's red circle icon by default!
        
    def set_use_circle(self, use_circle):
        self.use_circle = use_circle
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        if self.use_circle:
            # Draw the beautiful red circle matching the user's image
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor("#FF453A"))
            grad.setColorAt(1.0, QColor("#FF3B30"))
            
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(1, 1, 48, 48)
            
            # Exclamation point inside circle
            painter.setBrush(QColor("#FFFFFF"))
            painter.drawRoundedRect(QRectF(w / 2.0 - 3.0, 11, 6.0, 20), 3.0, 3.0)
            painter.drawEllipse(QPointF(w / 2.0, 38.0), 3.0, 3.0)
        else:
            # Rounded warning triangle
            path = QPainterPath()
            path.moveTo(w / 2, 6)
            path.arcTo(w / 2 - 8, 4, 16, 16, 120, -60) # Top corner
            path.lineTo(w - 4, h - 10)
            path.arcTo(w - 12, h - 10, 8, 8, 300, -60) # Bottom right corner
            path.lineTo(12, h - 2)
            path.arcTo(4, h - 10, 8, 8, 180, -60) # Bottom left corner
            path.closeSubpath()
            
            grad = QLinearGradient(0, 0, 0, h)
            grad.setColorAt(0.0, QColor("#EF4444"))
            grad.setColorAt(1.0, QColor("#DC2626"))
            
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path)
            
            painter.setPen(QPen(QColor("#FFFFFF"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(w / 2), 16, int(w / 2), 28)
            painter.setPen(QPen(QColor("#FFFFFF"), 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawPoint(int(w / 2), 34)


class RemoveTorrentDialog(QDialog):
    def __init__(self, parent=None, tasks=None, default_delete_data=False):
        super().__init__(parent)
        
        # Store tasks
        if tasks is None:
            tasks = []
        elif not isinstance(tasks, list):
            tasks = [tasks]
        self.tasks = tasks
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Roomy dialog size to prevent any compression and layout issues
        self.resize(520, 290)
        
        # Position relative to parent window if available
        if parent:
            geo = parent.geometry()
            self.move(
                int(geo.center().x() - self.width() / 2),
                int(geo.center().y() - self.height() / 2)
            )
            
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8) # Shadow margin
        
        # Background container card
        self.bg_frame = QFrame()
        self.bg_frame.setObjectName("dialogBg")
        self.bg_frame.setStyleSheet("""
            QFrame#dialogBg {
                background: transparent;
                border: none;
            }
        """)
        
        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 6)
        self.bg_frame.setGraphicsEffect(shadow)
        
        # Inner layout of background card (using compact, precise spacing)
        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(20, 20, 20, 20)
        bg_layout.setSpacing(10)
        
        # Top part: Icon + Content (horizontal)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Warning Icon
        self.icon_widget = WarningIconWidget()
        content_layout.addWidget(self.icon_widget)
        
        # Vertical text area
        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        count = len(self.tasks)
        if count > 1:
            title_text = f"Remove {count} Torrents?"
        else:
            title_text = "Remove Torrent?"
        self.title_lbl = QLabel(title_text)
        self.title_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 600; color: #ffffff;")
        text_layout.addWidget(self.title_lbl)
        
        # Subtitle / Body sentence
        if count > 1:
            body_text = "Are you sure you want to remove the selected torrents from Vortex?"
        else:
            body_text = "Are you sure you want to remove"
        self.body_lbl = QLabel(body_text)
        self.body_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #a0aec0;")
        text_layout.addWidget(self.body_lbl)
        
        # Filename (only for single torrent)
        if count == 1:
            task = self.tasks[0]
            name = task.torrent.get_name().decode('utf-8', errors='ignore')
            
            # Elide middle if name is too long
            font = QFont("Inter", 14, QFont.Weight.DemiBold)
            fm = QFontMetrics(font)
            elided_name = fm.elidedText(name, Qt.TextElideMode.ElideMiddle, 380)
            
            self.filename_lbl = QLabel(elided_name)
            self.filename_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 600; color: #3b82f6;") # Accent color
            text_layout.addWidget(self.filename_lbl)
            
        # Warning label
        self.warning_lbl = QLabel()
        self.warning_lbl.setWordWrap(True)
        self.warning_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 12px; color: #64748b;")
        text_layout.addWidget(self.warning_lbl)
        
        content_layout.addLayout(text_layout, 1)
        bg_layout.addLayout(content_layout)
        
        # Delete Data Checkbox
        self.chk_delete_data = QCheckBox("Also delete downloaded files from disk")
        self.chk_delete_data.setChecked(default_delete_data)
        self.chk_delete_data.setStyleSheet("""
            QCheckBox {
                color: #c8d0e0;
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #1e2438;
                background-color: #0f1220;
            }
            QCheckBox::indicator:checked {
                background-color: #EF4444;
                border-color: #EF4444;
                image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2024%2024%27%20fill%3D%27none%27%20stroke%3D%27white%27%20stroke-width%3D%273%27%20stroke-linecap%3D%27round%27%20stroke-linejoin%3D%27round%27%3E%3Cpolyline%20points%3D%2720%206%209%2017%204%2012%27%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E");
            }
        """)
        self.chk_delete_data.toggled.connect(self._update_warning)
        bg_layout.addWidget(self.chk_delete_data)
        
        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Plain)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.05); max-height: 1px; border: none;")
        bg_layout.addWidget(divider)
        
        # Bottom Button Row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Cancel Button (Outlined)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                color: #c8d0e0;
                font-family: 'Inter', sans-serif;
                font-weight: 500;
                font-size: 13px;
                min-height: 36px;
                min-width: 100px;
            }
            QPushButton:hover {
                border-color: rgba(255, 255, 255, 0.35);
                background-color: rgba(255, 255, 255, 0.04);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.08);
            }
            QPushButton:focus {
                border-color: #3b82f6;
                background-color: rgba(59, 130, 246, 0.05);
                outline: none;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        # Remove Button (Filled Red)
        self.btn_remove = QPushButton("Remove")
        self.btn_remove.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                border: 1px solid transparent;
                border-radius: 8px;
                color: #FFFFFF;
                font-family: 'Inter', sans-serif;
                font-weight: 600;
                font-size: 13px;
                min-height: 36px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #F87171;
            }
            QPushButton:pressed {
                background-color: #DC2626;
            }
            QPushButton:focus {
                border: 2px solid #FFFFFF;
                outline: none;
            }
        """)
        self.btn_remove.clicked.connect(self.accept)
        
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_remove)
        bg_layout.addLayout(button_layout)
        
        layout.addWidget(self.bg_frame)
        
        # Initial warning update
        self._update_warning(self.chk_delete_data.isChecked())
        
        # Animation timer to update background gradients
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self.update)
        self.bg_timer.start(100) # 10 FPS
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        import math
        import time
        
        # Draw rounded rect body with margins for the drop shadow
        path = QPainterPath()
        rect = QRectF(8, 8, self.width() - 16, self.height() - 16)
        path.addRoundedRect(rect, 12.0, 12.0)
        
        # Clip inside the rounded path to keep radial gradient blobs clean
        painter.setClipPath(path)
        
        # 1. Base dark theme color with subtle translucency (92%)
        painter.fillPath(path, QBrush(QColor(6, 7, 19, 235)))
        
        # 2. Moving radial gradients (matching the main screen blue/purple design)
        w = rect.width()
        h = rect.height()
        t = time.time()
        
        # Blue shifting top-left
        cx1 = 8 + w * 0.25 + (w * 0.15) * math.sin(t * 0.08)
        cy1 = 8 + h * 0.25 + (h * 0.15) * math.cos(t * 0.06)
        grad1 = QRadialGradient(cx1, cy1, w * 0.6)
        grad1.setColorAt(0.0, QColor(37, 99, 235, 40)) # blue
        grad1.setColorAt(0.5, QColor(37, 99, 235, 10))
        grad1.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillPath(path, QBrush(grad1))
        
        # Purple shifting bottom-right
        cx2 = 8 + w * 0.75 + (w * 0.15) * math.cos(t * 0.07)
        cy2 = 8 + h * 0.75 + (h * 0.15) * math.sin(t * 0.09)
        grad2 = QRadialGradient(cx2, cy2, w * 0.7)
        grad2.setColorAt(0.0, QColor(147, 51, 234, 30)) # purple
        grad2.setColorAt(0.5, QColor(147, 51, 234, 8))
        grad2.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillPath(path, QBrush(grad2))
        
        # 3. Outer border
        painter.setClipping(False)
        pen = QPen(QColor(255, 255, 255, 20), 1) # rgba(255, 255, 255, 0.08)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, 12.0, 12.0)
        
    def _update_warning(self, checked):
        self.icon_widget.set_use_circle(True)
        if checked:
            self.warning_lbl.setText("This will remove the torrent and permanently delete all downloaded files from your disk. This action is irreversible.")
            self.warning_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 12px; color: #EF4444; font-weight: 500;")
            self.btn_remove.setText("Delete")
            self.btn_remove.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;
                    border: 1px solid transparent;
                    border-radius: 8px;
                    color: #FFFFFF;
                    font-family: 'Inter', sans-serif;
                    font-weight: 600;
                    font-size: 13px;
                    min-height: 36px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #F87171;
                }
                QPushButton:pressed {
                    background-color: #DC2626;
                }
                QPushButton:focus {
                    border: 2px solid #FFFFFF;
                    outline: none;
                }
            """)
        else:
            self.warning_lbl.setText("This will remove the torrent from Vortex.\nDownloaded files will remain on disk.")
            self.warning_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 12px; color: #64748b;")
            self.btn_remove.setText("Remove")
            self.btn_remove.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;
                    border: 1px solid transparent;
                    border-radius: 8px;
                    color: #FFFFFF;
                    font-family: 'Inter', sans-serif;
                    font-weight: 600;
                    font-size: 13px;
                    min-height: 36px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #F87171;
                }
                QPushButton:pressed {
                    background-color: #DC2626;
                }
                QPushButton:focus {
                    border: 2px solid #FFFFFF;
                    outline: none;
                }
            """)
        self.warning_lbl.updateGeometry()
            
    def showEvent(self, event):
        super().showEvent(event)
        self.animate_entrance()
        
    def animate_entrance(self):
        geom = self.geometry()
        center = geom.center()
        w = geom.width()
        h = geom.height()
        
        # Scale 98% geometry
        start_w = int(w * 0.98)
        start_h = int(h * 0.98)
        start_x = center.x() - start_w // 2
        start_y = center.y() - start_h // 2
        
        self.setGeometry(QRect(start_x, start_y, start_w, start_h))
        
        self.geom_anim = QPropertyAnimation(self, b"geometry")
        self.geom_anim.setDuration(150)
        self.geom_anim.setStartValue(QRect(start_x, start_y, start_w, start_h))
        self.geom_anim.setEndValue(geom)
        
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(150)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        
        self.geom_anim.start()
        self.opacity_anim.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Enter -> Remove (only if Remove has focus)
            if self.btn_remove.hasFocus():
                self.accept()
            elif self.btn_cancel.hasFocus():
                self.reject()
            else:
                event.ignore()
        else:
            super().keyPressEvent(event)
            
    def get_delete_data(self):
        return self.chk_delete_data.isChecked()
