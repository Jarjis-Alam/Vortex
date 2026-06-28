import sys
import time
import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QRadialGradient, QPixmap

class SplashScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(480, 320)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)
        
        self.lbl_logo = QLabel()
        res_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
        logo_path = os.path.join(res_dir, "vortex_logo_v2.png")
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path).scaled(110, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.lbl_logo.setPixmap(pm)
        else:
            self.lbl_logo.setText("🌀")
            self.lbl_logo.setStyleSheet("font-size: 80px; background: transparent; border: none;")
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_title = QLabel("VORTEX")
        self.lbl_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffffff; letter-spacing: 4px; background: transparent; border: none;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_subtitle = QLabel("Modern BitTorrent Client")
        self.lbl_subtitle.setStyleSheet("font-size: 14px; color: #8892a8; font-weight: 500; background: transparent; border: none;")
        self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_status = QLabel("Loading Engine...")
        self.lbl_status.setStyleSheet("font-size: 13px; color: #6b7590; font-style: italic; background: transparent; border: none;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(6)
        self.pbar.setTextVisible(False)
        self.pbar.setStyleSheet("""
            QProgressBar {
                background-color: #101424;
                border-radius: 999px;
                border: none;
                max-width: 320px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2F7CF6, stop:1 #47B2FF);
                border-radius: 999px;
            }
        """)
        self.pbar.setValue(0)
        
        layout.addWidget(self.lbl_logo)
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_subtitle)
        layout.addWidget(self.lbl_status)
        layout.addWidget(self.pbar, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.progress_val = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._step_progress)
        self.timer.start(30)
        
    def _step_progress(self):
        self.progress_val += 2
        self.pbar.setValue(self.progress_val)
        
        if self.progress_val == 30:
            self.lbl_status.setText("Initializing socket mapping...")
        elif self.progress_val == 60:
            self.lbl_status.setText("Checking peer credentials...")
        elif self.progress_val == 85:
            self.lbl_status.setText("Connecting tracking services...")
            
        if self.progress_val >= 100:
            self.timer.stop()
            self.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        grad = QRadialGradient(self.width() / 2, self.height() / 2, self.width() * 0.7)
        grad.setColorAt(0, QColor("#141828"))
        grad.setColorAt(1, QColor("#0b0e18"))
        
        painter.setBrush(grad)
        painter.setPen(QColor("#2563eb"))
        painter.drawRoundedRect(self.rect(), 12, 12)
