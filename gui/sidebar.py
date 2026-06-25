import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
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
        if self.badge_count > 0:
            self.setText(f"  {self.icon_char}  {self.text().strip().split('  ')[-1] if '  ' in self.text() else self.text().strip()}")
        else:
            base = self.text().strip().split('  ')[-1] if '  ' in self.text() else self.text().strip()
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

        # Nav items
        self.items = {}
        nav_data = [
            ("Torrents", "📥", 0),
            ("Downloading", "⬇", 0),
            ("Completed", "✅", 0),
            ("Active", "🔵", 0),
            ("Inactive", "⏹", 0),
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
            ("Labels", "🏷"),
            ("Feeds", "📡"),
            ("Devices", "💻"),
        ]
        for name, icon in nav_data2:
            item = SidebarItem(name, 0, icon, self)
            item.setObjectName(f"nav_{name.lower()}")
            item.clicked.connect(lambda checked, n=name: self._on_clicked(n))
            layout.addWidget(item)
            self.items[name] = item

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setObjectName("sidebarSep")
        layout.addWidget(sep2)

        nav_data3 = [
            ("Settings", "⚙"),
            ("Statistics", "📊"),
            ("About", "ℹ"),
        ]
        for name, icon in nav_data3:
            item = SidebarItem(name, 0, icon, self)
            item.setObjectName(f"nav_{name.lower()}")
            item.clicked.connect(lambda checked, n=name: self._on_clicked(n))
            layout.addWidget(item)
            self.items[name] = item

        layout.addStretch()

        # Pro promo
        pro_frame = QFrame()
        pro_frame.setObjectName("proFrame")
        pro_layout = QVBoxLayout(pro_frame)
        pro_layout.setContentsMargins(14, 14, 14, 14)
        pro_layout.setSpacing(8)

        pro_header = QHBoxLayout()
        pro_title = QLabel("Vortex Pro")
        pro_title.setObjectName("proTitle")
        pro_close = QLabel("×")
        pro_close.setObjectName("proClose")
        pro_header.addWidget(pro_title)
        pro_header.addStretch()
        pro_header.addWidget(pro_close)
        pro_layout.addLayout(pro_header)

        pro_desc = QLabel("Unlock advanced features and\nsupport development.")
        pro_desc.setObjectName("proDesc")
        pro_desc.setWordWrap(True)
        pro_layout.addWidget(pro_desc)

        go_pro_btn = QPushButton("Go Pro")
        go_pro_btn.setObjectName("goProBtn")
        go_pro_btn.setFixedHeight(42)
        go_pro_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pro_layout.addWidget(go_pro_btn)

        layout.addWidget(pro_frame)

        # Select Torrents by default
        self.items["Torrents"].setChecked(True)

    def _on_clicked(self, name):
        for key, item in self.items.items():
            item.setChecked(key == name)
        self.filter_changed.emit(name)

    def update_badges(self, total=0, downloading=0, completed=0, active=0, inactive=0):
        self.items["Torrents"].badge_count = total
        self.items["Downloading"].badge_count = downloading
        self.items["Completed"].badge_count = completed
        self.items["Active"].badge_count = active
        self.items["Inactive"].badge_count = inactive
