import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QRect, QTimer, QByteArray
from PyQt6.QtGui import QIcon, QPixmap, QFont, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from gui.theme import presets

SVG_ICONS = {
    "Torrents": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
    </svg>""",
    "Downloading": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <line x1="12" y1="5" x2="12" y2="19"/>
      <polyline points="19 12 12 19 5 12"/>
    </svg>""",
    "Completed": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="20 6 9 17 4 12"/>
    </svg>""",
    "Active": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polygon points="5 3 19 12 5 21 5 3"/>
    </svg>""",
    "Inactive": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
    </svg>""",
    "Labels": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
      <line x1="7" y1="7" x2="7.01" y2="7"/>
    </svg>""",
    "Feeds": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M4 11a9 9 0 0 1 9 9"/>
      <path d="M4 4a16 16 0 0 1 16 16"/>
      <circle cx="5" cy="19" r="1"/>
    </svg>""",
    "Devices": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
      <line x1="8" y1="21" x2="16" y2="21"/>
      <line x1="12" y1="17" x2="12" y2="21"/>
    </svg>""",
    "Settings": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="3"/>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
    </svg>""",
    "Statistics": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <line x1="18" y1="20" x2="18" y2="10"/>
      <line x1="12" y1="20" x2="12" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="14"/>
    </svg>""",
    "About": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="16" x2="12" y2="12"/>
      <line x1="12" y1="8" x2="12.01" y2="8"/>
    </svg>"""
}

def make_svg_icon(svg_xml, color_muted, color_accent, color_text, size=QSize(18, 18)):
    icon = QIcon()
    for color, mode, state in [
        (color_muted, QIcon.Mode.Normal, QIcon.State.Off),
        (color_accent, QIcon.Mode.Normal, QIcon.State.On),
        (color_text, QIcon.Mode.Active, QIcon.State.Off),
        (color_accent, QIcon.Mode.Active, QIcon.State.On)
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

class SidebarItem(QPushButton):
    def __init__(self, text, badge_count=0, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.badge_count = badge_count
        self.setCheckable(True)
        self.setFixedHeight(44)
        self.setIconSize(QSize(18, 18))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_text()

    def _update_text(self):
        base = self.text().strip()
        if " (" in base:
            base = base.split(" (")[0]
        if self.badge_count > 0:
            self.setText(f"{base} ({self.badge_count})")
        else:
            self.setText(base)

    def set_badge(self, count):
        self.badge_count = count
        self._update_text()

class Sidebar(QWidget):
    filter_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)
        self.setObjectName("sidebar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(3)

        # Logo area
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(6, 0, 0, 20)
        res_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")
        logo_path = os.path.join(res_dir, "vortex_logo_v2.png")
        logo_icon = QLabel()
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path).scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_icon.setPixmap(pm)
        logo_icon.setFixedSize(40, 40)
        logo_text = QLabel("Vortex")
        logo_text.setObjectName("logoText")
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        layout.addLayout(logo_layout)

        # Nav items
        self.items = {}
        nav_data = [
            ("Torrents", 0),
            ("Downloading", 0),
            ("Completed", 0),
            ("Active", 0),
            ("Inactive", 0),
        ]
        for name, badge in nav_data:
            item = SidebarItem(name, badge, self)
            item.setObjectName(f"nav_{name.lower()}")
            item.clicked.connect(lambda checked, n=name: self._on_clicked(n))
            layout.addWidget(item)
            self.items[name] = item

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("sidebarSep")
        layout.addWidget(sep)

        nav_data2 = [
            ("Labels", 0),
            ("Feeds", 0),
            ("Devices", 0),
        ]
        for name, badge in nav_data2:
            item = SidebarItem(name, badge, self)
            item.setObjectName(f"nav_{name.lower()}")
            item.clicked.connect(lambda checked, n=name: self._on_clicked(n))
            layout.addWidget(item)
            self.items[name] = item

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setObjectName("sidebarSep")
        layout.addWidget(sep2)

        nav_data3 = [
            ("Settings", 0),
            ("Statistics", 0),
            ("About", 0),
        ]
        for name, badge in nav_data3:
            item = SidebarItem(name, badge, self)
            item.setObjectName(f"nav_{name.lower()}")
            item.clicked.connect(lambda checked, n=name: self._on_clicked(n))
            layout.addWidget(item)
            self.items[name] = item

        layout.addStretch()

        # Storage Card instead of Pro
        self.storage_frame = QFrame()
        self.storage_frame.setObjectName("proFrame")
        self.storage_layout = QVBoxLayout(self.storage_frame)
        self.storage_layout.setContentsMargins(14, 14, 14, 14)
        self.storage_layout.setSpacing(6)

        # Header layout with title and "..."
        lbl_title_layout = QHBoxLayout()
        lbl_title = QLabel("Disk Storage")
        lbl_title.setStyleSheet("font-weight: bold; color: #ffffff; font-size: 13px; background: transparent;")
        lbl_dots = QLabel("•••")
        lbl_dots.setStyleSheet("color: #6b7590; font-size: 14px; background: transparent;")
        lbl_title_layout.addWidget(lbl_title)
        lbl_title_layout.addStretch()
        lbl_title_layout.addWidget(lbl_dots)
        self.storage_layout.addLayout(lbl_title_layout)

        # Content layout (Donut + stats side-by-side)
        h_layout = QHBoxLayout()
        h_layout.setSpacing(12)

        # Mini circular donut chart
        from gui.donut_chart import DonutChart
        self.storage_donut = DonutChart()
        self.storage_donut.setFixedSize(48, 48)
        self.storage_donut.color = "#2563eb"
        h_layout.addWidget(self.storage_donut)

        # Vertical text labels
        v_text_layout = QVBoxLayout()
        v_text_layout.setSpacing(2)
        self.lbl_free = QLabel("Free: —")
        self.lbl_free.setStyleSheet("color: #8892a8; font-size: 11px; background: transparent; font-weight: 500;")
        self.lbl_used = QLabel("Used: —")
        self.lbl_used.setStyleSheet("color: #8892a8; font-size: 11px; background: transparent; font-weight: 500;")
        self.lbl_total = QLabel("Total: —")
        self.lbl_total.setStyleSheet("color: #8892a8; font-size: 11px; background: transparent; font-weight: 500;")
        v_text_layout.addWidget(self.lbl_free)
        v_text_layout.addWidget(self.lbl_used)
        v_text_layout.addWidget(self.lbl_total)
        h_layout.addLayout(v_text_layout)

        self.storage_layout.addLayout(h_layout)
        layout.addWidget(self.storage_frame)

        # Select Torrents by default
        self.items["Torrents"].setChecked(True)
        
        # Periodic check for storage
        self.storage_timer = QTimer(self)
        self.storage_timer.timeout.connect(self._update_storage_usage)
        self.storage_timer.start(5000)
        self._update_storage_usage()

    def refresh_theme_icons(self):
        main_win = self.window()
        theme_name = getattr(main_win, "current_theme", "Midnight Blue")
        custom_accent = getattr(main_win, "custom_accent_color", None)
        
        colors = presets.get(theme_name, presets["Midnight Blue"])
        
        accent = custom_accent if custom_accent else colors["accent"]
        text_muted = colors["text_muted"]
        text_normal = colors["text"]
        
        for name, item in self.items.items():
            if name in SVG_ICONS:
                icon = make_svg_icon(SVG_ICONS[name], text_muted, accent, text_normal)
                item.setIcon(icon)

    def _update_storage_usage(self):
        try:
            total, used, free = shutil.disk_usage(".")
            free_gb = free / (1024**3)
            used_gb = used / (1024**3)
            total_gb = total / (1024**3)
            pct = int((used / total) * 100)
            
            self.storage_donut.set_value(pct, False)
            self.lbl_free.setText(f"Free: {free_gb:.1f} GB")
            self.lbl_used.setText(f"Used: {used_gb:.1f} GB")
            self.lbl_total.setText(f"Total: {total_gb:.1f} GB")
        except Exception:
            pass

    def _on_clicked(self, name):
        for key, item in self.items.items():
            item.setChecked(key == name)
        self.filter_changed.emit(name)

    def update_badges(self, total=0, downloading=0, completed=0, active=0, inactive=0):
        self.items["Torrents"].set_badge(total)
        self.items["Downloading"].set_badge(downloading)
        self.items["Completed"].set_badge(completed)
        self.items["Active"].set_badge(active)
        self.items["Inactive"].set_badge(inactive)
