from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt


class StatCard(QWidget):
    def __init__(self, icon, value, label, color="#ffffff", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(10)
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"color: {color}; font-size: 18px;")
        self.val_lbl = QLabel(value)
        self.val_lbl.setObjectName("statValue")
        self.val_lbl.setStyleSheet(f"color: {color};")
        self.lbl = QLabel(label)
        self.lbl.setObjectName("statLabel")
        layout.addWidget(icon_lbl)
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.lbl)

    def set_value(self, v):
        self.val_lbl.setText(v)


class StatsBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statsBar")
        self.setFixedHeight(60)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        self.dl_card = StatCard("↓", "0 KB/s", "Total Download", "#22c55e")
        self.ul_card = StatCard("↑", "0 KB/s", "Total Upload", "#3b82f6")
        self.active_card = StatCard("🖥", "0", "Active Torrents", "#f59e0b")
        self.total_card = StatCard("📦", "0 B", "Total Downloaded", "#22c55e")
        layout.addWidget(self.dl_card)
        layout.addWidget(self._sep())
        layout.addWidget(self.ul_card)
        layout.addWidget(self._sep())
        layout.addWidget(self.active_card)
        layout.addWidget(self._sep())
        layout.addWidget(self.total_card)

    def _sep(self):
        s = QFrame()
        s.setFrameShape(QFrame.Shape.VLine)
        s.setStyleSheet("color: #1a1f30;")
        return s

    def update_stats(self, dl_speed="0 KB/s", ul_speed="0 KB/s", active=0, total_dl="0 B"):
        self.dl_card.set_value(dl_speed)
        self.ul_card.set_value(ul_speed)
        self.active_card.set_value(str(active))
        self.total_card.set_value(total_dl)
