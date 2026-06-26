from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen


class StatCard(QFrame):
    def __init__(self, icon, label, value, color="#ffffff", parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.color = color
        self.history = [0.0] * 20
        
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(20, 24, 40, 0.65), stop:1 rgba(15, 18, 32, 0.85));
                border: 1px solid {color}40;
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 24)  # Leave margin at the bottom for sparkline
        layout.setSpacing(2)
        
        lbl_layout = QHBoxLayout()
        lbl_layout.setContentsMargins(0, 0, 0, 0)
        lbl_layout.setSpacing(6)
        
        self.icon_lbl = QLabel(icon)
        self.icon_lbl.setStyleSheet(f"color: {color}; font-size: 15px; background: transparent; border: none;")
        
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

    def set_value(self, v):
        self.val_lbl.setText(v)
        
        # Populate history
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
        
        self.dl_card = StatCard("⬇", "Download", "0 KB/s", "#2563eb", self)
        self.ul_card = StatCard("⬆", "Upload", "0 KB/s", "#ef4444", self)
        self.seeds_card = StatCard("🌱", "Seeds", "0", "#22c55e", self)
        self.peers_card = StatCard("👥", "Peers", "0", "#2563eb", self)
        self.cpu_card = StatCard("⚡", "CPU", "0%", "#f97316", self)
        self.ram_card = StatCard("🧠", "RAM", "0%", "#ef4444", self)
        self.disk_card = StatCard("💾", "Disk", "0.0 MB/s", "#22c55e", self)
        
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
