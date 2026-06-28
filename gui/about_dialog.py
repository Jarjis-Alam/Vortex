import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QApplication, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, QUrl, QRectF, QRect, QPropertyAnimation, QEasingCurve, QByteArray, QSize
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient,
    QRadialGradient, QFont, QPixmap, QDesktopServices, QIcon
)
from PyQt6.QtSvg import QSvgRenderer

# SVG Helpers
def make_dialog_svg_pixmap(svg_xml, color, size):
    xml_colored = svg_xml.replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(xml_colored.encode('utf-8')))
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap

def make_dialog_svg_icon(svg_xml, color_normal, color_hover, size):
    icon = QIcon()
    for color, mode, state in [
        (color_normal, QIcon.Mode.Normal, QIcon.State.Off),
        (color_hover, QIcon.Mode.Active, QIcon.State.Off)
    ]:
        xml_colored = svg_xml.replace("currentColor", color)
        renderer = QSvgRenderer(QByteArray(xml_colored.encode('utf-8')))
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        icon.addPixmap(pixmap, mode, state)
    return icon

# Social icons
SOCIAL_SVGS = {
    "GitHub": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
    </svg>""",
    "LinkedIn": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>
      <rect x="2" y="9" width="4" height="12"/>
      <circle cx="4" cy="4" r="2"/>
    </svg>""",
    "Instagram": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
      <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
      <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
    </svg>""",
    "Web": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <line x1="2" y1="12" x2="22" y2="12"/>
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
    </svg>"""
}

class ClickableLogo(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(96, 96)
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
        logo_path = os.path.join(res_dir, "vortex_logo_v2.png")
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path).scaled(84, 84, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(int((self.width() - pm.width()) / 2), int((self.height() - pm.height()) / 2), pm)
        else:
            painter.setFont(QFont("Inter", 48))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "🌀")


class FeatureChipButton(QPushButton):
    def __init__(self, text, icon_xml, text_color, parent=None):
        super().__init__(parent)
        self.setText("  " + text)
        self.setIcon(make_dialog_svg_icon(icon_xml, text_color, text_color, QSize(14, 14)))
        self.setIconSize(QSize(14, 14))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #0b0e14;
                border: 1px solid {text_color}33;
                border-radius: 6px;
                color: {text_color};
                font-family: 'Inter', sans-serif;
                font-size: 12px;
                font-weight: 600;
                padding: 6px 14px;
            }}
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)


class SocialButton(QPushButton):
    def __init__(self, svg_xml, tooltip, url, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.url = url
        self.setIconSize(QSize(16, 16))
        
        icon = make_dialog_svg_icon(svg_xml, "#8892a8", "#ffffff", QSize(16, 16))
        self.setIcon(icon)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #161a25;
                border-radius: 6px;
            }
            QPushButton:hover {
                border-color: #2563eb;
                background-color: rgba(37, 99, 235, 0.08);
            }
        """)
        self.clicked.connect(self.open_url)

    def open_url(self):
        QDesktopServices.openUrl(QUrl(self.url))


class TopCloseButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(28, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.1);
                border-color: rgba(239, 68, 68, 0.3);
            }
        """)
        x_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>"""
        self.setIcon(make_dialog_svg_icon(x_xml, "#8892a8", "#ef4444", QSize(11, 11)))


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Vortex")
        self.setFixedSize(720, 810)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Outer layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(8, 8, 8, 8)
        
        # Container frame
        self.bg_frame = QFrame()
        self.bg_frame.setObjectName("dialogBg")
        self.bg_frame.setStyleSheet("""
            QFrame#dialogBg {
                background-color: rgba(7, 9, 14, 0.92);
                border: 1px solid #161a25;
                border-radius: 16px;
            }
        """)
        outer_layout.addWidget(self.bg_frame)
        
        # Stack Widget inside background frame
        self.stack = QStackedWidget(self.bg_frame)
        
        # Create Pages
        self.init_main_page()
        self.init_credits_page()
        
        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(28, 28, 28, 28)
        bg_layout.addWidget(self.stack)
        
        # Add absolute positioned top-right close button
        self.btn_top_close = TopCloseButton(self.bg_frame)
        self.btn_top_close.clicked.connect(self.accept_dialog)
        
        self.stack.setCurrentIndex(0)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.btn_top_close.move(self.bg_frame.width() - 42, 14)
        
    def init_main_page(self):
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)
        
        # 1. Hero Section (Vortex Info & Badges)
        hero_hbox = QHBoxLayout()
        hero_hbox.setSpacing(24)
        
        # Left swirl logo layout
        logo_vbox = QVBoxLayout()
        logo_vbox.setSpacing(4)
        self.logo = ClickableLogo(self)
        lbl_vortex_caps = QLabel("V O R T E X")
        lbl_vortex_caps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_vortex_caps.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 10px; font-weight: bold; color: #6b7590; letter-spacing: 4px; border: none; background: transparent;")
        logo_vbox.addWidget(self.logo)
        logo_vbox.addWidget(lbl_vortex_caps)
        hero_hbox.addLayout(logo_vbox)
        
        # Middle text information
        meta_vbox = QVBoxLayout()
        meta_vbox.setSpacing(4)
        meta_vbox.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        title_lbl = QLabel("VORTEX")
        title_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 32px; font-weight: 800; color: #ffffff; letter-spacing: 1.5px; border: none; background: transparent;")
        
        sub_lbl = QLabel("Modern BitTorrent Client")
        sub_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 700; color: #2563eb; letter-spacing: 0.5px; border: none; background: transparent;")
        
        desc_lbl = QLabel("Built from scratch in Python")
        desc_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 500; color: #6b7590; border: none; background: transparent;")
        
        meta_vbox.addWidget(title_lbl)
        meta_vbox.addWidget(sub_lbl)
        meta_vbox.addWidget(desc_lbl)
        meta_vbox.addSpacing(8)
        
        # Hero Description Paragraph
        hero_desc = QLabel("A high-performance BitTorrent client written purely in Python. Engineered for speed, resource efficiency, and a clean, clutter-free desktop workspace.")
        hero_desc.setWordWrap(True)
        hero_desc.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #8892a8; line-height: 1.5; border: none; background: transparent;")
        meta_vbox.addWidget(hero_desc)
        
        hero_hbox.addLayout(meta_vbox, 1)
        
        # Right version badges stack
        badge_vbox = QVBoxLayout()
        badge_vbox.setSpacing(8)
        badge_vbox.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        btn_version = QPushButton("v1.0.5 Beta")
        btn_version.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_version.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        btn_version.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Jarjis-Alam/Vortex/releases")))
        
        lbl_build = QLabel("Build 1024")
        lbl_build.setStyleSheet("""
            QLabel {
                background-color: #111420;
                color: #8892a8;
                border: 1px solid #161a25;
                border-radius: 6px;
                padding: 6px 14px;
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        lbl_build.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_status = QLabel("✓ Latest Version")
        lbl_status.setStyleSheet("""
            QLabel {
                background-color: rgba(16, 185, 129, 0.05);
                color: #10b981;
                border: 1px solid rgba(16, 185, 129, 0.2);
                border-radius: 6px;
                padding: 6px 14px;
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        badge_vbox.addWidget(btn_version)
        badge_vbox.addWidget(lbl_build)
        badge_vbox.addWidget(lbl_status)
        hero_hbox.addLayout(badge_vbox)
        
        layout.addLayout(hero_hbox)
        
        # 2. Tag Buttons (Feature Chips Row)
        chips_hbox = QHBoxLayout()
        chips_hbox.setSpacing(10)
        
        torrent_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
          <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
        </svg>"""
        magnet_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 9v3a6 6 0 0 0 12 0V9"/>
          <path d="M18 9V7a3 3 0 0 0-6 0v2"/>
          <path d="M12 9V7a3 3 0 0 0-6 0v2"/>
        </svg>"""
        globe_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="2" y1="12" x2="22" y2="12"/>
          <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
        </svg>"""
        code_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="16 18 22 12 16 6"/>
          <polyline points="8 6 2 12 8 18"/>
        </svg>"""
        cpu_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="4" y="4" width="16" height="16" rx="2" ry="2"/>
          <rect x="9" y="9" width="6" height="6"/>
          <line x1="9" y1="1" x2="9" y2="4"/>
          <line x1="15" y1="1" x2="15" y2="4"/>
          <line x1="9" y1="20" x2="9" y2="23"/>
          <line x1="15" y1="20" x2="15" y2="23"/>
        </svg>"""
        
        chips_hbox.addWidget(FeatureChipButton("BitTorrent v1", torrent_svg, "#2563eb"))
        chips_hbox.addWidget(FeatureChipButton("Magnet URI", magnet_svg, "#8b5cf6"))
        chips_hbox.addWidget(FeatureChipButton("Multi-Peer", globe_svg, "#10b981"))
        chips_hbox.addWidget(FeatureChipButton("Open Source", code_svg, "#f59e0b"))
        chips_hbox.addWidget(FeatureChipButton("PyQt6 Engine", cpu_svg, "#06b6d4"))
        
        layout.addLayout(chips_hbox)
        
        # 3. Status strip
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                border-top: 1px solid #161a25;
                border-bottom: 1px solid #161a25;
                background: transparent;
            }
        """)
        status_hbox = QHBoxLayout(status_frame)
        status_hbox.setContentsMargins(12, 8, 12, 8)
        
        # Engine Running
        w_engine = QWidget()
        lay_engine = QHBoxLayout(w_engine)
        lay_engine.setContentsMargins(0, 0, 0, 0)
        lay_engine.setSpacing(8)
        lbl_dot = QLabel()
        lbl_dot.setFixedSize(8, 8)
        lbl_dot.setStyleSheet("background-color: #10b981; border-radius: 4px; border: none;")
        lbl_txt_engine = QLabel('Engine: <span style="color: #ffffff; font-weight: bold;">Running</span>')
        lbl_txt_engine.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 12px; color: #8892a8; border: none;")
        lay_engine.addWidget(lbl_dot)
        lay_engine.addWidget(lbl_txt_engine)
        
        # Network Connected
        w_network = QWidget()
        lay_network = QHBoxLayout(w_network)
        lay_network.setContentsMargins(0, 0, 0, 0)
        lay_network.setSpacing(8)
        lbl_ico_network = QLabel()
        lbl_ico_network.setPixmap(make_dialog_svg_pixmap(globe_svg, "#2563eb", QSize(14, 14)))
        lbl_txt_network = QLabel('Network: <span style="color: #ffffff; font-weight: bold;">Connected</span>')
        lbl_txt_network.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 12px; color: #8892a8; border: none;")
        lay_network.addWidget(lbl_ico_network)
        lay_network.addWidget(lbl_txt_network)
        
        # DHT Online
        w_dht = QWidget()
        lay_dht = QHBoxLayout(w_dht)
        lay_dht.setContentsMargins(0, 0, 0, 0)
        lay_dht.setSpacing(8)
        lbl_ico_dht = QLabel()
        dht_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="18" cy="5" r="3"/>
          <circle cx="6" cy="12" r="3"/>
          <circle cx="18" cy="19" r="3"/>
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
        </svg>"""
        lbl_ico_dht.setPixmap(make_dialog_svg_pixmap(dht_svg, "#2563eb", QSize(14, 14)))
        lbl_txt_dht = QLabel('DHT: <span style="color: #ffffff; font-weight: bold;">Online</span>')
        lbl_txt_dht.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 12px; color: #8892a8; border: none;")
        lay_dht.addWidget(lbl_ico_dht)
        lay_dht.addWidget(lbl_txt_dht)
        
        # Vertical dividers
        def make_divider():
            frame = QFrame()
            frame.setFixedWidth(1)
            frame.setFixedHeight(14)
            frame.setStyleSheet("background-color: #161a25; border: none;")
            return frame
            
        status_hbox.addStretch()
        status_hbox.addWidget(w_engine)
        status_hbox.addStretch()
        status_hbox.addWidget(make_divider())
        status_hbox.addStretch()
        status_hbox.addWidget(w_network)
        status_hbox.addStretch()
        status_hbox.addWidget(make_divider())
        status_hbox.addStretch()
        status_hbox.addWidget(w_dht)
        status_hbox.addStretch()
        
        layout.addWidget(status_frame)
        
        # 4. Specs grid card
        specs_card = QFrame()
        specs_card.setStyleSheet("""
            QFrame {
                background-color: #0b0e14;
                border: 1px solid rgba(37, 99, 235, 0.15);
                border-radius: 10px;
            }
        """)
        specs_grid = QHBoxLayout(specs_card)
        specs_grid.setContentsMargins(20, 16, 20, 16)
        specs_grid.setSpacing(24)
        
        # Left Specs Column
        specs_left = QVBoxLayout()
        specs_left.setSpacing(10)
        
        # Calendar row
        row_cal = QHBoxLayout()
        row_cal.setSpacing(12)
        ico_cal = QLabel()
        cal_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
          <line x1="16" y1="2" x2="16" y2="6"/>
          <line x1="8" y1="2" x2="8" y2="6"/>
          <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>"""
        ico_cal.setPixmap(make_dialog_svg_pixmap(cal_svg, "#8892a8", QSize(16, 16)))
        lbl_cal_title = QLabel("Build Date")
        lbl_cal_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #8892a8; border: none;")
        lbl_cal_val = QLabel("2026-06-25")
        lbl_cal_val.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #ffffff; font-weight: bold; border: none;")
        row_cal.addWidget(ico_cal)
        row_cal.addWidget(lbl_cal_title)
        row_cal.addStretch()
        row_cal.addWidget(lbl_cal_val)
        specs_left.addLayout(row_cal)
        
        # Python row
        row_py = QHBoxLayout()
        row_py.setSpacing(12)
        ico_py = QLabel()
        py_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>"""
        ico_py.setPixmap(make_dialog_svg_pixmap(py_svg, "#8892a8", QSize(16, 16)))
        lbl_py_title = QLabel("Python")
        lbl_py_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #8892a8; border: none;")
        lbl_py_val = QLabel("3.12.3")
        lbl_py_val.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #ffffff; font-weight: bold; border: none;")
        row_py.addWidget(ico_py)
        row_py.addWidget(lbl_py_title)
        row_py.addStretch()
        row_py.addWidget(lbl_py_val)
        specs_left.addLayout(row_py)
        
        # Qt Binding row
        row_qt = QHBoxLayout()
        row_qt.setSpacing(12)
        ico_qt = QLabel()
        qt_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <circle cx="12" cy="12" r="4"/>
          <line x1="15" y1="15" x2="19" y2="19"/>
        </svg>"""
        ico_qt.setPixmap(make_dialog_svg_pixmap(qt_svg, "#8892a8", QSize(16, 16)))
        lbl_qt_title = QLabel("Qt Binding")
        lbl_qt_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #8892a8; border: none;")
        lbl_qt_val = QLabel("PyQt6 v6.5+")
        lbl_qt_val.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #ffffff; font-weight: bold; border: none;")
        row_qt.addWidget(ico_qt)
        row_qt.addWidget(lbl_qt_title)
        row_qt.addStretch()
        row_qt.addWidget(lbl_qt_val)
        specs_left.addLayout(row_qt)
        
        # License row
        row_lic = QHBoxLayout()
        row_lic.setSpacing(12)
        ico_lic = QLabel()
        lic_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>"""
        ico_lic.setPixmap(make_dialog_svg_pixmap(lic_svg, "#8892a8", QSize(16, 16)))
        lbl_lic_title = QLabel("License")
        lbl_lic_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #8892a8; border: none;")
        lbl_lic_val = QLabel("MIT")
        lbl_lic_val.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #ffffff; font-weight: bold; border: none;")
        
        badge_os = QLabel("Open Source")
        badge_os.setStyleSheet("""
            QLabel {
                background-color: rgba(37, 99, 235, 0.08);
                color: #2563eb;
                border: 1px solid rgba(37, 99, 235, 0.2);
                border-radius: 4px;
                padding: 1px 6px;
                font-family: 'Inter', sans-serif;
                font-size: 10px;
                font-weight: bold;
            }
        """)
        
        row_lic.addWidget(ico_lic)
        row_lic.addWidget(lbl_lic_title)
        row_lic.addStretch()
        row_lic.addWidget(lbl_lic_val)
        row_lic.addWidget(badge_os)
        specs_left.addLayout(row_lic)
        
        specs_grid.addLayout(specs_left, 1)
        
        # Dotted vertical separator
        specs_sep = QFrame()
        specs_sep.setFixedWidth(1)
        specs_sep.setStyleSheet("border-left: 1px dashed rgba(37, 99, 235, 0.25); border-right: none; border-top: none; border-bottom: none;")
        specs_grid.addWidget(specs_sep)
        
        # Right Specs Column
        specs_right = QVBoxLayout()
        specs_right.setSpacing(10)
        
        # Downloads Completed row
        row_dl = QHBoxLayout()
        row_dl.setSpacing(12)
        ico_dl = QLabel()
        dl_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>"""
        ico_dl.setPixmap(make_dialog_svg_pixmap(dl_svg, "#8892a8", QSize(16, 16)))
        lbl_dl_title = QLabel("Downloads Completed")
        lbl_dl_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #8892a8; border: none;")
        lbl_dl_val = QLabel("128")
        lbl_dl_val.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #2563eb; font-weight: bold; border: none;")
        row_dl.addWidget(ico_dl)
        row_dl.addWidget(lbl_dl_title)
        row_dl.addStretch()
        row_dl.addWidget(lbl_dl_val)
        specs_right.addLayout(row_dl)
        
        # Pieces Verified row
        row_pv = QHBoxLayout()
        row_pv.setSpacing(12)
        ico_pv = QLabel()
        pv_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <polyline points="9 11 11 13 15 9"/>
        </svg>"""
        ico_pv.setPixmap(make_dialog_svg_pixmap(pv_svg, "#8892a8", QSize(16, 16)))
        lbl_pv_title = QLabel("Pieces Verified")
        lbl_pv_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #8892a8; border: none;")
        lbl_pv_val = QLabel("1,240,582")
        lbl_pv_val.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #2563eb; font-weight: bold; border: none;")
        row_pv.addWidget(ico_pv)
        row_pv.addWidget(lbl_pv_title)
        row_pv.addStretch()
        row_pv.addWidget(lbl_pv_val)
        specs_right.addLayout(row_pv)
        
        # Runtime row
        row_rt = QHBoxLayout()
        row_rt.setSpacing(12)
        ico_rt = QLabel()
        rt_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>"""
        ico_rt.setPixmap(make_dialog_svg_pixmap(rt_svg, "#8892a8", QSize(16, 16)))
        lbl_rt_title = QLabel("Runtime")
        lbl_rt_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #8892a8; border: none;")
        lbl_rt_val = QLabel("28 hours")
        lbl_rt_val.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #2563eb; font-weight: bold; border: none;")
        row_rt.addWidget(ico_rt)
        row_rt.addWidget(lbl_rt_title)
        row_rt.addStretch()
        row_rt.addWidget(lbl_rt_val)
        specs_right.addLayout(row_rt)
        
        # Engine Startup row
        row_es = QHBoxLayout()
        row_es.setSpacing(12)
        ico_es = QLabel()
        es_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4.5 16.5c-1.5 1.5-2.5 3.5-2.5 5.5C4 22 6 21 7.5 19.5"/>
          <path d="M12 2C6 2 2 6 2 12c0 2.5 1 4.5 2.5 6l11.5-11.5C14.5 5 12.5 4 12 2z"/>
          <path d="M22 2s-4 1-6 2.5L20 9c1.5-2 2.5-6 2.5-6z"/>
        </svg>"""
        ico_es.setPixmap(make_dialog_svg_pixmap(es_svg, "#8892a8", QSize(16, 16)))
        lbl_es_title = QLabel("Engine Startup")
        lbl_es_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #8892a8; border: none;")
        lbl_es_val = QLabel("0.42 s")
        lbl_es_val.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #2563eb; font-weight: bold; border: none;")
        row_es.addWidget(ico_es)
        row_es.addWidget(lbl_es_title)
        row_es.addStretch()
        row_es.addWidget(lbl_es_val)
        specs_right.addLayout(row_es)
        
        specs_grid.addLayout(specs_right, 1)
        
        layout.addWidget(specs_card)
        
        # 5. Technical Strip (CPU / Memory / Commit)
        tech_frame = QFrame()
        tech_frame.setStyleSheet("""
            QFrame {
                border-top: 1px solid #161a25;
                border-bottom: 1px solid #161a25;
                background: transparent;
            }
        """)
        tech_hbox = QHBoxLayout(tech_frame)
        tech_hbox.setContentsMargins(12, 8, 12, 8)
        
        # Left CPU/Memory
        lbl_mem_ico = QLabel()
        lbl_mem_ico.setPixmap(make_dialog_svg_pixmap(cpu_svg, "#8892a8", QSize(14, 14)))
        lbl_mem_txt = QLabel('<span style="color: #8892a8;">Memory:</span> <span style="color: #ffffff; font-weight: bold;">78 MB</span>')
        lbl_mem_txt.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 11px; border: none;")
        
        # Right Commit
        lbl_commit_ico = QLabel()
        lbl_commit_ico.setPixmap(make_dialog_svg_pixmap(code_svg, "#2563eb", QSize(14, 14)))
        lbl_commit_txt = QLabel('<span style="color: #8892a8;">Commit:</span> <span style="color: #2563eb; font-weight: bold;">3a1e92f</span>')
        lbl_commit_txt.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 11px; border: none;")
        
        tech_hbox.addWidget(lbl_mem_ico)
        tech_hbox.addWidget(lbl_mem_txt)
        tech_hbox.addStretch()
        tech_hbox.addWidget(lbl_commit_ico)
        tech_hbox.addWidget(lbl_commit_txt)
        
        layout.addWidget(tech_frame)
        
        # 6. Protocol & Codebase Overview Box
        overview_card = QFrame()
        overview_card.setStyleSheet("""
            QFrame {
                background-color: #080b10;
                border: 1px solid #161a25;
                border-radius: 8px;
            }
        """)
        overview_vbox = QVBoxLayout(overview_card)
        overview_vbox.setContentsMargins(16, 12, 16, 12)
        overview_vbox.setSpacing(8)
        
        # Protocol support line
        line_proto = QHBoxLayout()
        line_proto.setSpacing(10)
        ico_proto = QLabel()
        ico_proto.setPixmap(make_dialog_svg_pixmap(pv_svg, "#2563eb", QSize(14, 14)))
        
        lbl_proto_text = QLabel(
            '<span style="color: #8892a8; font-weight: bold;">Protocol Support:</span> '
            '<span style="color: #10b981;">✓ BitTorrent v1</span>  '
            '<span style="color: #10b981;">✓ Magnet URI</span>  '
            '<span style="color: #10b981;">✓ DHT</span>  '
            '<span style="color: #10b981;">✓ PEX</span>  '
            '<span style="color: #10b981;">✓ Multi-Peer</span>  '
            '<span style="color: #10b981;">✓ Resume Downloads</span>'
        )
        lbl_proto_text.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 11px; border: none;")
        line_proto.addWidget(ico_proto)
        line_proto.addWidget(lbl_proto_text)
        line_proto.addStretch()
        overview_vbox.addLayout(line_proto)
        
        # Codebase line
        line_code = QHBoxLayout()
        line_code.setSpacing(10)
        ico_code = QLabel()
        ico_code.setPixmap(make_dialog_svg_pixmap(code_svg, "#2563eb", QSize(14, 14)))
        
        lbl_code_text = QLabel(
            '<span style="color: #8892a8; font-weight: bold;">Codebase:</span> '
            '<span style="color: #c8d0e0;">Python 3.12, PyQt6, SHA-1 Verification, Multi-threaded Downloader</span>'
        )
        lbl_code_text.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 11px; border: none;")
        line_code.addWidget(ico_code)
        line_code.addWidget(lbl_code_text)
        line_code.addStretch()
        overview_vbox.addLayout(line_code)
        
        layout.addWidget(overview_card)
        
        # 7. Developer & Socials Profile Box
        dev_hbox = QHBoxLayout()
        dev_hbox.setSpacing(16)
        
        # Circular Avatar
        lbl_avatar = QLabel("MJ")
        lbl_avatar.setFixedSize(48, 48)
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_avatar.setStyleSheet("""
            QLabel {
                background-color: rgba(37, 99, 235, 0.08);
                border: 2px solid #2563eb;
                border-radius: 24px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        dev_hbox.addWidget(lbl_avatar)
        
        # Developer Details Text
        dev_info_vbox = QVBoxLayout()
        dev_info_vbox.setSpacing(2)
        dev_info_vbox.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        lbl_dev_title = QLabel("Lead Developer")
        lbl_dev_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 11px; color: #6b7590; font-weight: bold; border: none;")
        
        lbl_dev_name = QLabel("Munshi Jarjis Alam")
        lbl_dev_name.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 15px; color: #ffffff; font-weight: bold; border: none;")
        
        lbl_dev_subtitle = QLabel("Graphics • UI/UX • Backend")
        lbl_dev_subtitle.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 11px; color: #6b7590; font-weight: 500; border: none;")
        
        dev_info_vbox.addWidget(lbl_dev_title)
        dev_info_vbox.addWidget(lbl_dev_name)
        dev_info_vbox.addWidget(lbl_dev_subtitle)
        dev_hbox.addLayout(dev_info_vbox)
        
        dev_hbox.addStretch()
        
        # Social links container frame
        social_container = QFrame()
        social_container.setStyleSheet("""
            QFrame {
                background-color: #0b0e14;
                border: 1px solid #161a25;
                border-radius: 8px;
            }
        """)
        social_layout = QHBoxLayout(social_container)
        social_layout.setContentsMargins(6, 6, 6, 6)
        social_layout.setSpacing(6)
        
        social_layout.addWidget(SocialButton(SOCIAL_SVGS["GitHub"], "GitHub Profile", "https://github.com/Jarjis-Alam"))
        social_layout.addWidget(SocialButton(SOCIAL_SVGS["LinkedIn"], "LinkedIn Profile", "https://linkedin.com/in/jarjisalam/"))
        social_layout.addWidget(SocialButton(SOCIAL_SVGS["Instagram"], "Instagram Profile", "https://instagram.com/jarvis._exe_"))
        social_layout.addWidget(SocialButton(SOCIAL_SVGS["Web"], "Vortex Repository", "https://github.com/Jarjis-Alam/Vortex"))
        
        dev_hbox.addWidget(social_container)
        layout.addLayout(dev_hbox)
        
        layout.addSpacing(6)
        
        # 8. Footer Action Buttons
        footer_hbox = QHBoxLayout()
        footer_hbox.setSpacing(12)
        
        # Check Updates Button
        refresh_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M23 4v6h-6M1 20v-6h6"/>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
        </svg>"""
        btn_updates = QPushButton("  Check for Updates")
        btn_updates.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_updates.setIcon(make_dialog_svg_icon(refresh_svg, "#ffffff", "#2563eb", QSize(14, 14)))
        btn_updates.setIconSize(QSize(14, 14))
        btn_updates.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #20263d;
                border-radius: 8px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 18px;
            }
            QPushButton:hover {
                border-color: #2563eb;
                background-color: rgba(37, 99, 235, 0.04);
            }
        """)
        btn_updates.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Jarjis-Alam/Vortex/releases")))
        footer_hbox.addWidget(btn_updates)
        
        # Star on GitHub Button
        star_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>"""
        btn_star = QPushButton("  Star on GitHub")
        btn_star.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_star.setIcon(make_dialog_svg_icon(star_svg, "#f59e0b", "#f59e0b", QSize(14, 14)))
        btn_star.setIconSize(QSize(14, 14))
        btn_star.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #f59e0b33;
                border-radius: 8px;
                color: #f59e0b;
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 18px;
            }
            QPushButton:hover {
                border-color: #f59e0b;
                background-color: rgba(245, 158, 11, 0.08);
            }
        """)
        btn_star.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Jarjis-Alam/Vortex")))
        footer_hbox.addWidget(btn_star)
        
        footer_hbox.addStretch()
        
        # Close Button
        x_close_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>"""
        btn_close = QPushButton("  Close")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setIcon(make_dialog_svg_icon(x_close_svg, "#ffffff", "#ffffff", QSize(12, 12)))
        btn_close.setIconSize(QSize(12, 12))
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                border: none;
                border-radius: 8px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 22px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        btn_close.clicked.connect(self.accept_dialog)
        footer_hbox.addWidget(btn_close)
        
        layout.addLayout(footer_hbox)
        
        self.stack.addWidget(main_widget)

    def init_credits_page(self):
        credits_widget = QWidget()
        layout = QVBoxLayout(credits_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_lbl = QLabel("VORTEX")
        title_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 32px; font-weight: 700; color: #ffffff; letter-spacing: 2px; border: none;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub_lbl = QLabel("Developed by Munshi Jarjis Alam")
        sub_lbl.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 600; color: #2563eb; border: none;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Info Box
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #0b0e14;
                border: 1px solid #161a25;
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
                background: #2563eb;
                border: none;
                border-radius: 18px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
        """)
        btn_back.clicked.connect(self._show_main_page)
        
        layout.addWidget(title_lbl)
        layout.addWidget(sub_lbl)
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
