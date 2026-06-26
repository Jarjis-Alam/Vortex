import os
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QRect, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QFont


class SidebarItem(QPushButton):
    def __init__(self, text, badge_count=0, icon_char="", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.badge_count = badge_count
        self.icon_char = icon_char
        self.setCheckable(True)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_text()

    def _update_text(self):
        base = self.text().strip().split('  ')[-1] if '  ' in self.text() else self.text().strip()
        if " (" in base:
            base = base.split(" (")[0]
        if self.badge_count > 0:
            self.setText(f"  {self.icon_char}  {base} ({self.badge_count})")
        else:
            self.setText(f"  {self.icon_char}  {base}")

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
        logo_path = os.path.join(res_dir, "logo.png")
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

        # Indicator behind selected items
        self.indicator = QWidget(self)
        self.indicator.setStyleSheet("background-color: rgba(37, 99, 235, 0.12); border-radius: 10px; border-left: 3px solid #2563eb;")
        self.indicator.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.indicator.hide()

        # Nav items
        self.items = {}
        nav_data = [
            ("Torrents", "📂", 0),
            ("Downloading", "↓", 0),
            ("Completed", "✓", 0),
            ("Active", "●", 0),
            ("Inactive", "■", 0),
        ]
        for name, icon, badge in nav_data:
            item = SidebarItem(name, badge, icon, self)
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
            ("Labels", "🏷", 0),
            ("Feeds", "📡", 0),
            ("Devices", "💻", 0),
        ]
        for name, icon, badge in nav_data2:
            item = SidebarItem(name, badge, icon, self)
            item.setObjectName(f"nav_{name.lower()}")
            item.clicked.connect(lambda checked, n=name: self._on_clicked(n))
            layout.addWidget(item)
            self.items[name] = item

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setObjectName("sidebarSep")
        layout.addWidget(sep2)

        nav_data3 = [
            ("Settings", "⚙", 0),
            ("Statistics", "📊", 0),
            ("About", "ℹ", 0),
        ]
        for name, icon, badge in nav_data3:
            item = SidebarItem(name, badge, icon, self)
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
        QTimer.singleShot(100, self._init_indicator)
        
        # Periodic check for storage
        self.storage_timer = QTimer(self)
        self.storage_timer.timeout.connect(self._update_storage_usage)
        self.storage_timer.start(5000)
        self._update_storage_usage()

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

    def _init_indicator(self):
        selected_item = self.items.get("Torrents")
        if selected_item:
            self.indicator.setGeometry(selected_item.geometry())
            self.indicator.show()

    def _on_clicked(self, name):
        for key, item in self.items.items():
            item.setChecked(key == name)
            
        selected_item = self.items.get(name)
        if selected_item:
            self.anim = QPropertyAnimation(self.indicator, b"geometry")
            self.anim.setDuration(180)
            self.anim.setStartValue(self.indicator.geometry())
            self.anim.setEndValue(selected_item.geometry())
            self.anim.start()
            self.indicator.show()
            
        self.filter_changed.emit(name)

    def update_badges(self, total=0, downloading=0, completed=0, active=0, inactive=0):
        self.items["Torrents"].set_badge(total)
        self.items["Downloading"].set_badge(downloading)
        self.items["Completed"].set_badge(completed)
        self.items["Active"].set_badge(active)
        self.items["Inactive"].set_badge(inactive)
