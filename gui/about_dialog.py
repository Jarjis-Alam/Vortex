import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QApplication, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, QUrl, QRectF, QRect, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient,
    QRadialGradient, QFont, QPixmap, QDesktopServices
)

class ClickableLogo(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.click_count = 0
        self.parent_dialog = parent

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_count += 1
            if self.click_count >= 5:
                self.click_count = 0
                if self.parent_dialog and hasattr(self.parent_dialog, "_show_credits_page"):
                    self.parent_dialog._show_credits_page()
            super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        res_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")
        logo_path = os.path.join(res_dir, "logo.png")
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path).scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(int((self.width() - pm.width()) / 2), int((self.height() - pm.height()) / 2), pm)
        else:
            painter.setFont(QFont("Inter", 54))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "🌀")


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
                background-color: rgba(37, 99, 235, 0.08);
                color: {color};
                border: 1px solid rgba(37, 99, 235, 0.15);
                border-radius: 999px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)


class SocialButton(QPushButton):
    def __init__(self, text, tooltip, url, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(40, 40)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.url = url
        self.setStyleSheet("""
            QPushButton {
                background-color: #141828;
                border: 1px solid #1e2438;
                border-radius: 20px;
                color: #a0aec0;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: #3b82f6;
                background-color: #3b82f6;
                color: #ffffff;
            }
        """)
        self.clicked.connect(self.open_url)

    def open_url(self):
        QDesktopServices.openUrl(QUrl(self.url))


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Vortex")
        self.setFixedSize(650, 720)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Outer Layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        # Glassmorphic Background Frame
        self.bg_frame = QFrame()
        self.bg_frame.setObjectName("dialogBg")
        self.bg_frame.setStyleSheet("""
            QFrame#dialogBg {
                background-color: rgba(11, 14, 24, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        outer_layout.addWidget(self.bg_frame)
        
        # Stack Widget inside background frame
        self.stack = QStackedWidget(self.bg_frame)
        
        # Create Pages
        self.init_main_page()
        self.init_credits_page()
        
        # Layout for background frame
        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(20, 20, 20, 20)
        bg_layout.addWidget(self.stack)
        
        self.stack.setCurrentIndex(0)
        
    def init_main_page(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(14)
        
        # 1. Hero Section (Larger, radial gradient background)
        hero_widget = QWidget()
        hero_widget.setFixedHeight(140)
        
        # Inner Hero Layout
        hero_layout = QHBoxLayout(hero_widget)
        hero_layout.setContentsMargins(10, 10, 10, 10)
        hero_layout.setSpacing(24)
        
        self.logo = ClickableLogo(self)
        
        meta_layout = QVBoxLayout()
        meta_layout.setSpacing(4)
        meta_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        title_lbl = QLabel("VORTEX")
        title_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 28px; font-weight: 700; color: #ffffff; letter-spacing: 2px;")
        
        sub_lbl = QLabel("Modern BitTorrent Client")
        sub_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: #3b82f6; letter-spacing: 0.5px;")
        
        desc_lbl = QLabel("Built from scratch in Python")
        desc_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 500; color: #6b7590;")
        
        meta_layout.addWidget(title_lbl)
        meta_layout.addWidget(sub_lbl)
        meta_layout.addWidget(desc_lbl)
        
        # Version Badges Layout
        badge_container = QWidget()
        badge_layout = QVBoxLayout(badge_container)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setSpacing(6)
        badge_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Clickable Version Badge
        self.version_badge = QPushButton("v1.0.5 Beta")
        self.version_badge.setCursor(Qt.CursorShape.PointingHandCursor)
        self.version_badge.setToolTip("Click to view Release Notes")
        self.version_badge.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 4px 12px;
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        self.version_badge.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Jarjis-Alam/Vortex/releases")))
        
        # Build Badge
        build_badge = QLabel("Build 1024")
        build_badge.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.08);
                color: #c8d0e0;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                padding: 4px 12px;
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        
        # Update Status Badge
        update_status = QLabel("✓ Latest Version")
        update_status.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 11px; color: #22c55e; font-weight: 600;")
        
        badge_layout.addWidget(self.version_badge)
        badge_layout.addWidget(build_badge)
        badge_layout.addWidget(update_status)
        
        hero_layout.addWidget(self.logo)
        hero_layout.addLayout(meta_layout, 1)
        hero_layout.addWidget(badge_container)
        
        layout.addWidget(hero_widget)
        
        # 2. Description (Bounded width)
        desc_container = QWidget()
        desc_c_layout = QHBoxLayout(desc_container)
        desc_c_layout.setContentsMargins(0, 0, 0, 0)
        
        bio_lbl = QLabel(
            "A high-performance BitTorrent client written purely in Python. "
            "Engineered focusing on speed, resource efficiency, and a clean, clutter-free "
            "desktop workspace dashboard."
        )
        bio_lbl.setWordWrap(True)
        bio_lbl.setFixedWidth(520)
        bio_lbl.setStyleSheet("color: #a0aec0; font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.5;")
        desc_c_layout.addWidget(bio_lbl)
        desc_c_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_container)
        
        # 3. Feature Chips Row
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)
        chips_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chips_layout.addWidget(FeatureChip("BitTorrent v1", "#3b82f6"))
        chips_layout.addWidget(FeatureChip("Magnet URI", "#8b5cf6"))
        chips_layout.addWidget(FeatureChip("Multi-Peer", "#10b981"))
        chips_layout.addWidget(FeatureChip("Open Source", "#f59e0b"))
        chips_layout.addWidget(FeatureChip("PyQt6 Engine", "#06b6d4"))
        layout.addLayout(chips_layout)
        
        # 4. Engine Status Strip
        status_strip = QFrame()
        status_strip.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
        """)
        status_layout = QHBoxLayout(status_strip)
        status_layout.setContentsMargins(16, 8, 16, 8)
        
        def make_status_item(label, val):
            widget = QWidget()
            item_layout = QHBoxLayout(widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(6)
            
            lbl_dot = QLabel("🟢")
            lbl_dot.setStyleSheet("font-size: 8px; background: transparent; border: none;")
            
            lbl_txt = QLabel(f"<span style='color: #6b7590;'>{label}:</span> <span style='color: #ffffff; font-weight: bold;'>{val}</span>")
            lbl_txt.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 11px; background: transparent; border: none;")
            
            item_layout.addWidget(lbl_dot)
            item_layout.addWidget(lbl_txt)
            return widget
            
        status_layout.addWidget(make_status_item("Engine", "Running"))
        status_layout.addWidget(make_status_item("Network", "Connected"))
        status_layout.addWidget(make_status_item("DHT", "Online"))
        layout.addWidget(status_strip)
        
        # 5. Information & Stats Card (Two-column layout)
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 24, 40, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
            QLabel {
                font-family: 'Inter', sans-serif;
                border: none;
                background: transparent;
            }
        """)
        info_layout = QGridLayout(info_frame)
        info_layout.setContentsMargins(20, 16, 20, 16)
        info_layout.setSpacing(14)
        
        # Column 1 (System Info)
        def add_info_row(grid, row, key, val, badge_txt=None):
            kl = QLabel(key)
            kl.setStyleSheet("color: #6b7590; font-weight: 600; font-size: 12px;")
            grid.addWidget(kl, row, 0)
            
            if badge_txt:
                badge_widget = QWidget()
                bw_layout = QHBoxLayout(badge_widget)
                bw_layout.setContentsMargins(0, 0, 0, 0)
                bw_layout.setSpacing(6)
                
                vl = QLabel(val)
                vl.setStyleSheet("color: #ffffff; font-weight: 500; font-size: 12px;")
                
                badge_lbl = QLabel(badge_txt)
                badge_lbl.setStyleSheet("background-color: rgba(59, 130, 246, 0.12); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: bold;")
                
                bw_layout.addWidget(vl)
                bw_layout.addWidget(badge_lbl)
                bw_layout.addStretch()
                grid.addWidget(badge_widget, row, 1)
            else:
                vl = QLabel(val)
                vl.setStyleSheet("color: #ffffff; font-weight: 500; font-size: 12px;")
                grid.addWidget(vl, row, 1)

        add_info_row(info_layout, 0, "Build Date", "2026-06-25")
        add_info_row(info_layout, 1, "Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        add_info_row(info_layout, 2, "Qt Binding", "PyQt6 v6.5+")
        add_info_row(info_layout, 3, "License", "MIT", "Open Source")
        
        # Column 2 (App Stats)
        def add_stats_row(grid, row, key, val):
            kl = QLabel(key)
            kl.setStyleSheet("color: #6b7590; font-weight: 600; font-size: 12px;")
            vl = QLabel(val)
            vl.setStyleSheet("color: #3b82f6; font-weight: bold; font-size: 12px;")
            grid.addWidget(kl, row, 2)
            grid.addWidget(vl, row, 3)
            
        add_stats_row(info_layout, 0, "Downloads Completed", "128")
        add_stats_row(info_layout, 1, "Pieces Verified", "1,240,582")
        add_stats_row(info_layout, 2, "Runtime", "28 hours")
        add_stats_row(info_layout, 3, "Engine Startup", "0.42 s")
        
        layout.addWidget(info_frame)
        
        # 6. Technical / Git / Memory Panel
        tech_strip = QWidget()
        tech_layout = QHBoxLayout(tech_strip)
        tech_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_mem = QLabel("<span style='color: #6b7590;'>Memory:</span> <span style='color: #ffffff; font-weight: 500;'>78 MB</span>")
        lbl_mem.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 11px;")
        
        lbl_commit = QLabel("<span style='color: #6b7590;'>Commit:</span> <span style='color: #3b82f6; font-weight: 600;'>3a1e92f</span>")
        lbl_commit.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 11px;")
        
        tech_layout.addWidget(lbl_mem)
        tech_layout.addStretch()
        tech_layout.addWidget(lbl_commit)
        layout.addWidget(tech_strip)
        
        # 7. Project Overview Details (Protocol Support)
        overview_frame = QFrame()
        overview_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.04);
                border-radius: 8px;
            }
            QLabel {
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                border: none;
                background: transparent;
            }
        """)
        overview_layout = QVBoxLayout(overview_frame)
        overview_layout.setContentsMargins(12, 10, 12, 10)
        overview_layout.setSpacing(6)
        
        lbl_protocols = QLabel("<span style='color: #6b7590; font-weight: bold;'>Protocol Support:</span> <span style='color: #22c55e;'>✓ BitTorrent v1</span>  <span style='color: #22c55e;'>✓ Magnet URI</span>  <span style='color: #22c55e;'>✓ DHT</span>  <span style='color: #22c55e;'>✓ PEX</span>  <span style='color: #22c55e;'>✓ Multi-Peer</span>  <span style='color: #22c55e;'>✓ Resume Downloads</span>")
        lbl_protocols.setWordWrap(True)
        
        lbl_codebase = QLabel("<span style='color: #6b7590; font-weight: bold;'>Codebase:</span> <span style='color: #c8d0e0;'>Python 3.12, PyQt6, SHA-1 Verification, Multi-threaded Downloader</span>")
        lbl_codebase.setWordWrap(True)
        
        overview_layout.addWidget(lbl_protocols)
        overview_layout.addWidget(lbl_codebase)
        layout.addWidget(overview_frame)
        
        # 8. Developer & Socials row
        dev_widget = QWidget()
        dev_layout = QHBoxLayout(dev_widget)
        dev_layout.setContentsMargins(0, 0, 0, 0)
        
        dev_info = QVBoxLayout()
        dev_info.setSpacing(2)
        
        lbl_dev = QLabel("Lead Developer")
        lbl_dev.setStyleSheet("color: #6b7590; font-family: 'Inter', sans-serif; font-size: 11px; font-weight: bold;")
        
        lbl_name = QLabel("Munshi Jarjis Alam")
        lbl_name.setStyleSheet("color: #ffffff; font-family: 'Inter', sans-serif; font-size: 15px; font-weight: bold;")
        
        lbl_dev_sub = QLabel("Graphics • UI/UX • Backend")
        lbl_dev_sub.setStyleSheet("color: #6b7590; font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 500;")
        
        dev_info.addWidget(lbl_dev)
        dev_info.addWidget(lbl_name)
        dev_info.addWidget(lbl_dev_sub)
        dev_layout.addLayout(dev_info)
        
        # Social Buttons
        socials_layout = QHBoxLayout()
        socials_layout.setSpacing(8)
        socials_layout.addWidget(SocialButton("💻", "GitHub Profile", "https://github.com/Jarjis-Alam"))
        socials_layout.addWidget(SocialButton("in", "LinkedIn Profile", "https://linkedin.com/in/jarjisalam/"))
        socials_layout.addWidget(SocialButton("📷", "Instagram Profile", "https://instagram.com/jarvis._exe_"))
        socials_layout.addWidget(SocialButton("🌐", "Vortex Repository", "https://github.com/Jarjis-Alam/Vortex"))
        
        dev_layout.addStretch()
        dev_layout.addLayout(socials_layout)
        layout.addWidget(dev_widget)
        
        # 9. Divider & Footer
        layout.addWidget(GradientDivider(self))
        
        footer_layout = QHBoxLayout()
        
        btn_update = QPushButton("Check for Updates")
        btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_update.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 999px;
                padding: 6px 16px;
                color: #c8d0e0;
                font-family: 'Inter', sans-serif;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                border-color: rgba(255, 255, 255, 0.35);
                background-color: rgba(255, 255, 255, 0.04);
            }
        """)
        btn_update.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Jarjis-Alam/Vortex/releases")))
        
        btn_repo = QPushButton("GitHub ⭐")
        btn_repo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_repo.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 999px;
                padding: 6px 16px;
                color: #f59e0b;
                font-family: 'Inter', sans-serif;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                border-color: #f59e0b;
                background-color: rgba(245, 158, 11, 0.08);
            }
        """)
        btn_repo.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Jarjis-Alam/Vortex")))
        
        btn_close = QPushButton("Close")
        btn_close.setFixedSize(100, 32)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                border: none;
                border-radius: 999px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3b82f6, stop:1 #2563eb);
            }
        """)
        btn_close.clicked.connect(self.accept_dialog)
        
        footer_layout.addWidget(btn_update)
        footer_layout.addSpacing(10)
        footer_layout.addWidget(btn_repo)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_close)
        layout.addLayout(footer_layout)
        
        self.stack.addWidget(main_widget)

    def init_credits_page(self):
        credits_widget = QWidget()
        layout = QVBoxLayout(credits_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_lbl = QLabel("VORTEX")
        title_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 32px; font-weight: 700; color: #ffffff; letter-spacing: 2px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub_lbl = QLabel("Made with ❤️ by Munshi Jarjis Alam")
        sub_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 600; color: #3b82f6;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        divider = GradientDivider(self)
        
        # Info Box
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 24, 40, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
            QLabel {
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                color: #c8d0e0;
                line-height: 1.6;
                border: none;
                background: transparent;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setSpacing(12)
        
        lib_lbl = QLabel(
            "<b>Built Using Open-Source Libraries:</b><br>"
            "• Python 3.12 Standard Library (socket, threading, hashlib, struct)<br>"
            "• PyQt6 (Qt 6.5 binding for modern graphic layout Engine)<br>"
            "• Torrent metadata encoder/decoder (Bencode parsing library)"
        )
        lib_lbl.setWordWrap(True)
        
        thanks_lbl = QLabel(
            "<b>Special Thanks:</b><br>"
            "Thank you to the GitHub community, beta testers, and developers "
            "worldwide who support Python projects!"
        )
        thanks_lbl.setWordWrap(True)
        
        info_layout.addWidget(lib_lbl)
        info_layout.addWidget(thanks_lbl)
        
        # Back Button
        btn_back = QPushButton("Back")
        btn_back.setFixedSize(120, 36)
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                border: none;
                border-radius: 999px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3b82f6, stop:1 #2563eb);
            }
        """)
        btn_back.clicked.connect(self._show_main_page)
        
        layout.addWidget(title_lbl)
        layout.addWidget(sub_lbl)
        layout.addWidget(divider)
        layout.addWidget(info_frame)
        layout.addSpacing(20)
        layout.addWidget(btn_back, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.stack.addWidget(credits_widget)
        
    def _show_credits_page(self):
        self.stack.setCurrentIndex(1)
        
    def _show_main_page(self):
        self.stack.setCurrentIndex(0)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.animate_entrance()
        
    def animate_entrance(self):
        geom = self.geometry()
        center = geom.center()
        w = geom.width()
        h = geom.height()
        
        start_w = int(w * 0.98)
        start_h = int(h * 0.98)
        start_x = center.x() - start_w // 2
        start_y = center.y() - start_h // 2
        
        self.setGeometry(QRect(start_x, start_y, start_w, start_h))
        
        self.geom_anim = QPropertyAnimation(self, b"geometry")
        self.geom_anim.setDuration(180)
        self.geom_anim.setStartValue(QRect(start_x, start_y, start_w, start_h))
        self.geom_anim.setEndValue(geom)
        self.geom_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(180)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        
        self.geom_anim.start()
        self.opacity_anim.start()

    def accept_dialog(self):
        # Fade out before closing
        self.opacity_anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim_out.setDuration(150)
        self.opacity_anim_out.setStartValue(1.0)
        self.opacity_anim_out.setEndValue(0.0)
        self.opacity_anim_out.finished.connect(self.accept)
        self.opacity_anim_out.start()

    def paintEvent(self, event):
        # Drawing the nice radial background and borders
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Radial background Behind Logo (around top-left of the dialog)
        grad = QRadialGradient(100, 100, 160)
        grad.setColorAt(0, QColor("rgba(37, 99, 235, 0.08)"))
        grad.setColorAt(1, QColor("rgba(11, 14, 24, 0.0)"))
        
        # Draw background inside card bounds to match border radius
        rect = QRectF(self.bg_frame.geometry())
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 16, 16)
