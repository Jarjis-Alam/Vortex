from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QPointF, QRectF, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont


class SparklineCard(QFrame):
    def __init__(self, title, unit="%", color="#2563eb", parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.color = color
        self.history = [0.0] * 60
        self.current_val = 0.0
        self.subtext = ""
        
        self.setObjectName("sparklineCard")
        self.setStyleSheet(f"""
            QFrame#sparklineCard {{
                background-color: #141828;
                border: 1px solid #1e2438;
                border-radius: 12px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)
        
        # Header layout
        hl = QHBoxLayout()
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #6b7590; font-size: 14px; font-weight: bold; background: transparent; border: none;")
        self.lbl_val = QLabel("0.0 " + unit)
        self.lbl_val.setStyleSheet("color: #ffffff; font-size: 22px; font-weight: bold; background: transparent; border: none;")
        hl.addWidget(self.lbl_title)
        hl.addStretch()
        hl.addWidget(self.lbl_val)
        layout.addLayout(hl)
        
        # Line plot container
        self.graph_widget = QWidget()
        self.graph_widget.setFixedHeight(120)
        self.graph_widget.paintEvent = self.paint_graph
        layout.addWidget(self.graph_widget)
        
        self.lbl_sub = QLabel("")
        self.lbl_sub.setStyleSheet("color: #5a6580; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(self.lbl_sub)
        
    def add_value(self, val, subtext=""):
        self.current_val = val
        self.subtext = subtext
        self.history.pop(0)
        self.history.append(float(val))
        
        if self.unit == "MB/s":
            if val >= 1.0:
                self.lbl_val.setText(f"{val:.2f} MB/s")
            else:
                self.lbl_val.setText(f"{val*1024:.0f} KB/s")
        else:
            self.lbl_val.setText(f"{val:.1f} {self.unit}")
            
        if subtext:
            self.lbl_sub.setText(subtext)
        self.graph_widget.update()
        
    def paint_graph(self, event):
        painter = QPainter(self.graph_widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.graph_widget.width()
        h = self.graph_widget.height()
        
        max_val = max(max(self.history), 1.0)
        
        # Draw background horizontal lines (dashed grid)
        grid_pen = QPen(QColor("#1a1f30"), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        painter.drawLine(0, int(h/3), w, int(h/3))
        painter.drawLine(0, int(2*h/3), w, int(2*h/3))
        
        # Plot data points
        points = []
        for idx, val in enumerate(self.history):
            x = idx * (w / 59)
            # scale y
            y = h - (val / max_val) * (h - 14) - 7
            points.append(QPointF(x, y))
            
        # Area fill under path
        from PyQt6.QtGui import QPainterPath
        path = QPainterPath()
        path.moveTo(0, h)
        for pt in points:
            path.lineTo(pt)
        path.lineTo(w, h)
        path.closeSubpath()
        
        grad = QLinearGradient(0, 0, 0, h)
        c_start = QColor(self.color)
        c_start.setAlpha(35)
        c_end = QColor(self.color)
        c_end.setAlpha(0)
        grad.setColorAt(0, c_start)
        grad.setColorAt(1, c_end)
        
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        
        # Line graph outline
        line_pen = QPen(QColor(self.color), 2)
        painter.setPen(line_pen)
        for idx in range(len(points) - 1):
            painter.drawLine(points[idx], points[idx+1])


class StatisticsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("detailPanel")
        
        # Title banner
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        title_lbl = QLabel("System Diagnostics & Client Performance")
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(title_lbl)
        
        # Sparklines grid
        grid = QGridLayout()
        grid.setSpacing(20)
        
        self.card_cpu = SparklineCard("Processor Usage", "%", "#ef4444", self)
        self.card_ram = SparklineCard("Memory Footprint", "%", "#f59e0b", self)
        self.card_disk = SparklineCard("Disk Transfer Rate", "MB/s", "#22c55e", self)
        self.card_dl = SparklineCard("Download Throughput", "MB/s", "#2563eb", self)
        self.card_ul = SparklineCard("Upload Throughput", "MB/s", "#ef4444", self)
        self.card_peers = SparklineCard("Swarm Peer Latency", "peers", "#bd93f9", self)
        
        grid.addWidget(self.card_cpu, 0, 0)
        grid.addWidget(self.card_ram, 0, 1)
        grid.addWidget(self.card_disk, 0, 2)
        grid.addWidget(self.card_dl, 1, 0)
        grid.addWidget(self.card_ul, 1, 1)
        grid.addWidget(self.card_peers, 1, 2)
        
        main_layout.addLayout(grid)
        main_layout.addStretch()
        
    def update_metrics(self, cpu, ram, disk, dl, ul, peers):
        self.card_cpu.add_value(cpu, f"Active cores load: {cpu}%")
        self.card_ram.add_value(ram, f"RAM usage: {ram}% of physical memory")
        self.card_disk.add_value(disk, f"Read/write I/O speed: {disk:.1f} MB/s")
        self.card_dl.add_value(dl, f"Global client incoming rate")
        self.card_ul.add_value(ul, f"Global client outgoing rate")
        self.card_peers.add_value(peers, f"Connected swarm members: {peers}")
