from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QPointF, QSize, QByteArray
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap
from PyQt6.QtSvg import QSvgRenderer

STATS_SVGS = {
    "DL": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <line x1="12" y1="5" x2="12" y2="19"/>
      <polyline points="19 12 12 19 5 12"/>
    </svg>""",
    "UL": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <line x1="12" y1="19" x2="12" y2="5"/>
      <polyline points="5 12 12 5 19 12"/>
    </svg>""",
    "Seeds": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 3.5 1 8a7 7 0 0 1-9 10zm0 0v-8"/>
    </svg>""",
    "Peers": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
      <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
    </svg>""",
    "CPU": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
    </svg>""",
    "RAM": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <rect x="4" y="4" width="16" height="16" rx="2" ry="2"/>
      <rect x="9" y="9" width="6" height="6"/>
      <line x1="9" y1="1" x2="9" y2="4"/>
      <line x1="15" y1="1" x2="15" y2="4"/>
      <line x1="9" y1="20" x2="9" y2="23"/>
      <line x1="15" y1="20" x2="15" y2="23"/>
      <line x1="20" y1="9" x2="23" y2="9"/>
      <line x1="20" y1="15" x2="23" y2="15"/>
      <line x1="1" y1="9" x2="4" y2="9"/>
      <line x1="1" y1="15" x2="4" y2="15"/>
    </svg>""",
    "Disk": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
      <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
      <line x1="6" y1="6" x2="6.01" y2="6"/>
      <line x1="6" y1="18" x2="6.01" y2="18"/>
    </svg>"""
}

def render_svg_to_pixmap(svg_xml, color_hex, size=QSize(18, 18)):
    xml_colored = svg_xml.replace("currentColor", color_hex)
    renderer = QSvgRenderer(QByteArray(xml_colored.encode('utf-8')))
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap

class StatCard(QFrame):
    def __init__(self, svg_xml, label, value, color="#ffffff", parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.color = color
        self.svg_xml = svg_xml
        self.history = [0.0] * 20
        
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(20, 24, 40, 0.65), stop:1 rgba(15, 18, 32, 0.85));
                border: 1px solid {color}40;
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 24)
        layout.setSpacing(2)
        
        lbl_layout = QHBoxLayout()
        lbl_layout.setContentsMargins(0, 0, 0, 0)
        lbl_layout.setSpacing(6)
        
        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(18, 18)
        self.icon_lbl.setStyleSheet("background: transparent; border: none;")
        self.refresh_icon()
        
        self.lbl = QLabel(label)
        self.lbl.setStyleSheet("color: #6b7590; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        
        lbl_layout.addWidget(self.icon_lbl)
        lbl_layout.addWidget(self.lbl)
        lbl_layout.addStretch()
        
        self.trend_lbl = QLabel("")
        self.trend_lbl.setStyleSheet("font-size: 11px; font-weight: bold; background: transparent; border: none;")
        lbl_layout.addWidget(self.trend_lbl)
        
        layout.addLayout(lbl_layout)
        
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold; background: transparent; border: none;")
        layout.addWidget(self.val_lbl)

    def refresh_icon(self):
        pixmap = render_svg_to_pixmap(self.svg_xml, self.color, QSize(16, 16))
        self.icon_lbl.setPixmap(pixmap)

    def set_value(self, v):
        self.val_lbl.setText(v)
        
        try:
            cleaned = v.replace(" KB/s", "").replace(" MB/s", "").replace("%", "").replace(" MB", "").replace(" GB", "").replace(" B", "").strip()
            mult = 1.0
            if "MB/s" in v:
                mult = 1024.0
            val = float(cleaned) * mult
        except Exception:
            val = 0.0
            
        self.history.pop(0)
        self.history.append(val)
        self.update()
        
    def set_trend(self, trend_text, trend_color="#22c55e"):
        self.trend_lbl.setText(trend_text)
        self.trend_lbl.setStyleSheet(f"color: {trend_color}; font-size: 11px; font-weight: bold; background: transparent; border: none;")

    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        margin_left = 14
        margin_right = 14
        margin_bottom = 6
        plot_h = 16
        
        max_val = max(self.history)
        if max_val <= 0:
            max_val = 1.0
            
        points = []
        for idx, v in enumerate(self.history):
            x = margin_left + idx * ((w - margin_left - margin_right) / 19)
            y = h - margin_bottom - (v / max_val) * plot_h
            points.append(QPointF(x, y))
            
        pen = QPen(QColor(self.color), 1.8)
        painter.setPen(pen)
        
        for idx in range(len(points) - 1):
            painter.drawLine(points[idx], points[idx+1])


class StatsBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statsBar")
        self.setFixedHeight(102)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(10)
        
        self.dl_card = StatCard(STATS_SVGS["DL"], "Download", "0 KB/s", "#2563eb", self)
        self.ul_card = StatCard(STATS_SVGS["UL"], "Upload", "0 KB/s", "#ef4444", self)
        self.seeds_card = StatCard(STATS_SVGS["Seeds"], "Seeds", "0", "#22c55e", self)
        self.peers_card = StatCard(STATS_SVGS["Peers"], "Peers", "0", "#2563eb", self)
        self.cpu_card = StatCard(STATS_SVGS["CPU"], "CPU", "0%", "#f97316", self)
        self.ram_card = StatCard(STATS_SVGS["RAM"], "RAM", "0%", "#ef4444", self)
        self.disk_card = StatCard(STATS_SVGS["Disk"], "Disk", "0.0 MB/s", "#22c55e", self)
        
        self.dl_card.set_trend("▲ 8%", "#22c55e")
        self.ul_card.set_trend("▲ 2%", "#22c55e")
        self.seeds_card.set_trend("▲ Seeding", "#22c55e")
        self.peers_card.set_trend("▲ Active", "#22c55e")
        self.cpu_card.set_trend("▲ Load", "#22c55e")
        self.ram_card.set_trend("▼ Usage", "#22c55e")
        
        layout.addWidget(self.dl_card)
        layout.addWidget(self.ul_card)
        layout.addWidget(self.seeds_card)
        layout.addWidget(self.peers_card)
        layout.addWidget(self.cpu_card)
        layout.addWidget(self.ram_card)
        layout.addWidget(self.disk_card)

    def refresh_theme(self, theme_name, custom_accent=None):
        from gui.theme import presets
        colors = presets.get(theme_name, presets["Midnight Blue"])
        
        accent = custom_accent if custom_accent else colors["accent"]
        success = colors["success"]
        error = colors["error"]
        warning = colors["warning"]
        
        card_colors = {
            self.dl_card: accent,
            self.ul_card: error,
            self.seeds_card: success,
            self.peers_card: accent,
            self.cpu_card: warning,
            self.ram_card: error,
            self.disk_card: success
        }
        
        for card, color in card_colors.items():
            card.color = color
            card.refresh_icon()
            card.setStyleSheet(f"""
                QFrame#statCard {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(20, 24, 40, 0.65), stop:1 rgba(15, 18, 32, 0.85));
                    border: 1px solid {color}40;
                    border-radius: 12px;
                }}
            """)

    def update_stats(self, dl_speed="0 KB/s", ul_speed="0 KB/s", active_seeds=0, active_peers=0, cpu=0, ram=0, disk=0.0):
        self.dl_card.set_value(dl_speed)
        self.ul_card.set_value(ul_speed)
        self.seeds_card.set_value(str(active_seeds))
        self.peers_card.set_value(str(active_peers))
        self.cpu_card.set_value(f"{cpu}%")
        self.ram_card.set_value(f"{ram}%")
        self.disk_card.set_value(f"{disk:.1f} MB/s" if disk > 0 else "0.0 MB/s")
        
        if active_peers > 0:
            self.peers_card.set_trend("▲ Active", "#22c55e")
        else:
            self.peers_card.set_trend("▼ Idle", "#ef4444")
            
        if active_seeds > 0:
            self.seeds_card.set_trend("▲ Seeding", "#22c55e")
        else:
            self.seeds_card.set_trend("● Offline", "#6b7590")
