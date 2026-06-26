import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QUrl, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient,
    QRadialGradient, QFont, QPixmap, QDesktopServices
)


class RotatingLogo(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0.0
        self.setFixedSize(80, 80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.click_count = 0
        self.easter_egg_timer = None

    def set_angle(self, angle):
        self.angle = angle
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_count += 1
            # Add rotation burst on click
            self.angle += 35
            self.update()
            
            if self.click_count >= 5:
                self.click_count = 0
                # Find parent dialog and show egg toast
                p = self.window()
                if p and hasattr(p, "_trigger_easter_egg"):
                    p._trigger_easter_egg()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)

        res_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")
        logo_path = os.path.join(res_dir, "logo.png")
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(int(-pm.width() / 2), int(-pm.height() / 2), pm)
        else:
            painter.setFont(QFont("Inter", 36))
            painter.drawText(QRectF(-25, -25, 50, 50), Qt.AlignmentFlag.AlignCenter, "🌀")


class GradientDivider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(12)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0, QColor("rgba(37, 99, 235, 0)"))
        grad.setColorAt(0.5, QColor("rgba(37, 99, 235, 0.45)"))
        grad.setColorAt(1, QColor("rgba(37, 99, 235, 0)"))
        
        pen = QPen(grad, 1)
        painter.setPen(pen)
        painter.drawLine(0, self.height() // 2, self.width(), self.height() // 2)


class FeatureChip(QLabel):
    def __init__(self, text, color="#2563eb", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color}15;
                color: {color};
                border: 1px solid {color}30;
                border-radius: 999px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
            }}
        """)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Vortex")
        self.setFixedSize(620, 640)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setStyleSheet("background-color: #0b0e18;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(12)

        # Header Row: Logo + App Meta
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)

        self.logo = RotatingLogo(self)
        self.logo_timer = QTimer(self)
        self.logo_timer.timeout.connect(self._rotate_logo)
        self.logo_timer.start(24)

        meta_layout = QVBoxLayout()
        meta_layout.setSpacing(2)
        
        title_lbl = QLabel("VORTEX")
        title_lbl.setStyleSheet("font-size: 26px; font-weight: 900; color: #ffffff; letter-spacing: 1px;")
        
        sub_lbl = QLabel("Modern BitTorrent Client")
        sub_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #3b82f6;")
        
        desc_lbl = QLabel("Built from scratch in Python")
        desc_lbl.setStyleSheet("font-size: 12px; font-weight: 500; color: #6b7590;")
        
        meta_layout.addWidget(title_lbl)
        meta_layout.addWidget(sub_lbl)
        meta_layout.addWidget(desc_lbl)
        meta_layout.addStretch()

        # Version Pill Badge
        badge_layout = QVBoxLayout()
        version_badge = QLabel("v1.0.0 Stable")
        version_badge.setStyleSheet("""
            QLabel {
                background-color: rgba(34, 197, 94, 0.12);
                color: #22c55e;
                border: 1px solid rgba(34, 197, 94, 0.3);
                border-radius: 999px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        badge_layout.addWidget(version_badge)
        badge_layout.addStretch()

        header_layout.addWidget(self.logo)
        header_layout.addLayout(meta_layout, 1)
        header_layout.addLayout(badge_layout)

        layout.addWidget(header_widget)

        # Divider
        layout.addWidget(GradientDivider(self))

        # Bio Paragraph
        bio_lbl = QLabel(
            "A high-performance BitTorrent client written purely in Python. "
            "Engineered focusing on speed, resource efficiency, and a clean, clutter-free "
            "desktop workspace dashboard."
        )
        bio_lbl.setWordWrap(True)
        bio_lbl.setStyleSheet("color: #a0aec0; font-size: 13px; line-height: 1.4;")
        layout.addWidget(bio_lbl)

        # Feature Chips Row
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)
        chips_layout.addWidget(FeatureChip("BitTorrent v1", "#2563eb"))
        chips_layout.addWidget(FeatureChip("Magnet URI", "#bd93f9"))
        chips_layout.addWidget(FeatureChip("Multi-Peer", "#22c55e"))
        chips_layout.addWidget(FeatureChip("Open Source", "#f59e0b"))
        chips_layout.addWidget(FeatureChip("PyQt6 Engine", "#06b6d4"))
        chips_layout.addStretch()
        layout.addLayout(chips_layout)

        # Divider
        layout.addWidget(GradientDivider(self))

        # System / Engine Build Metadata Grid
        grid_frame = QFrame()
        grid_frame.setStyleSheet("""
            QFrame {
                background-color: #141828;
                border: 1px solid #1e2438;
                border-radius: 12px;
            }
            QLabel {
                font-size: 13px;
                border: none;
                background: transparent;
            }
        """)
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setContentsMargins(16, 12, 16, 12)
        grid_layout.setSpacing(8)

        def add_row(grid, row, key, val, val_color="#ffffff"):
            kl = QLabel(key)
            kl.setStyleSheet("color: #6b7590; font-weight: bold;")
            vl = QLabel(val)
            vl.setStyleSheet(f"color: {val_color}; font-weight: 500;")
            grid.addWidget(kl, row, 0)
            grid.addWidget(vl, row, 1)

        add_row(grid_layout, 0, "Build Date", "2026.06.25")
        add_row(grid_layout, 1, "Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        add_row(grid_layout, 2, "Qt Binding", "PyQt6 v6.5+")
        add_row(grid_layout, 3, "License type", "MIT License", "#f59e0b")

        layout.addWidget(grid_frame)

        # Status / Running state
        status_lbl = QLabel("● Engine status: Active  ● Sockets loop: Bound  ● DHT routing: Connected")
        status_lbl.setStyleSheet("color: #22c55e; font-size: 11px; font-weight: bold; alignment: center;")
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_lbl)

        # Divider
        layout.addWidget(GradientDivider(self))

        # Developer & Socials row
        dev_widget = QWidget()
        dev_layout = QHBoxLayout(dev_widget)
        dev_layout.setContentsMargins(0, 0, 0, 0)
        
        dev_info = QVBoxLayout()
        dev_info.setSpacing(2)
        lbl_dev = QLabel("Lead Developer")
        lbl_dev.setStyleSheet("color: #6b7590; font-size: 11px; font-weight: bold;")
        lbl_name = QLabel("Munshi Jarjis Alam")
        lbl_name.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: bold;")
        dev_info.addWidget(lbl_dev)
        dev_info.addWidget(lbl_name)
        dev_layout.addLayout(dev_info)

        # Social Icon Buttons: GitHub, LinkedIn, Instagram, Website
        socials_layout = QHBoxLayout()
        socials_layout.setSpacing(10)

        def make_social_btn(text, tooltip, url):
            btn = QPushButton(text)
            btn.setFixedSize(36, 36)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #141828;
                    border: 1px solid #1e2438;
                    border-radius: 18px;
                    color: #ffffff;
                    font-size: 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    border-color: #2563eb;
                    background-color: rgba(37, 99, 235, 0.12);
                }
            """)
            btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
            return btn

        btn_gh = make_social_btn("💻", "GitHub Profile", "https://github.com/Jarjis-Alam")
        btn_li = make_social_btn("in", "LinkedIn Profile", "https://linkedin.com/in/jarjisalam/")
        btn_ig = make_social_btn("📷", "Instagram Profile", "https://instagram.com/jarvis._exe_")
        btn_web = make_social_btn("🌐", "Vortex Repository", "https://github.com/Jarjis-Alam/Vortex")

        socials_layout.addWidget(btn_gh)
        socials_layout.addWidget(btn_li)
        socials_layout.addWidget(btn_ig)
        socials_layout.addWidget(btn_web)
        
        dev_layout.addStretch()
        dev_layout.addLayout(socials_layout)
        layout.addWidget(dev_widget)

        # Divider
        layout.addWidget(GradientDivider(self))

        # Bottom row: Repo link, Star button, check for updates, Close button
        bottom_row = QHBoxLayout()
        
        btn_update = QPushButton("Check for Updates")
        btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_update.setStyleSheet("""
            QPushButton {
                background-color: #1e2438;
                border: 1px solid #2d3650;
                border-radius: 999px;
                padding: 6px 14px;
                color: #c8d0e0;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d3650;
                color: #ffffff;
            }
        """)
        btn_update.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Jarjis-Alam/Vortex/releases")))
        
        lbl_repo = QLabel("⭐ Star on GitHub")
        lbl_repo.setCursor(Qt.CursorShape.PointingHandCursor)
        lbl_repo.setStyleSheet("color: #f59e0b; font-size: 12px; font-weight: bold;")
        lbl_repo.mousePressEvent = lambda e: QDesktopServices.openUrl(QUrl("https://github.com/Jarjis-Alam/Vortex"))
        
        btn_close = QPushButton("Close")
        btn_close.setFixedSize(90, 36)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                border: none;
                border-radius: 999px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3b82f6, stop:1 #2563eb);
            }
        """)
        btn_close.clicked.connect(self.accept)

        bottom_row.addWidget(btn_update)
        bottom_row.addSpacing(14)
        bottom_row.addWidget(lbl_repo)
        bottom_row.addStretch()
        bottom_row.addWidget(btn_close)

        layout.addLayout(bottom_row)

        # Easter Egg Toast widget placeholder
        self.egg_toast = QLabel(self)
        self.egg_toast.hide()

    def _rotate_logo(self):
        self.logo.set_angle(self.logo.angle + 0.5)

    def _trigger_easter_egg(self):
        self.egg_toast.setText("🚀 Vortex Overclock: Torrent Mode Activated!")
        self.egg_toast.setStyleSheet("""
            QLabel {
                background-color: #141828;
                border: 2px solid #f59e0b;
                border-radius: 12px;
                color: #f59e0b;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 16px;
            }
        """)
        self.egg_toast.adjustSize()
        # center at bottom of dialog
        tx = (self.width() - self.egg_toast.width()) // 2
        ty = self.height() - 110
        self.egg_toast.move(tx, ty)
        self.egg_toast.show()
        
        QTimer.singleShot(3000, self.egg_toast.hide)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QRadialGradient(self.width() / 2, self.height() / 2, self.width() * 0.7)
        grad.setColorAt(0, QColor("#0f1220"))
        grad.setColorAt(1, QColor("#05070c"))
        painter.fillRect(self.rect(), grad)
