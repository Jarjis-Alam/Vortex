import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QHeaderView, QGridLayout, QFrame, QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt, QPointF, QRectF, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont

from gui.donut_chart import DonutChart


class DetailCard(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #141828;
                border: 1px solid #1e2438;
                border-radius: 12px;
            }
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 12, 14, 12)
        self.layout.setSpacing(6)
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("color: #5a6580; font-size: 13px; font-weight: bold; background: transparent; border: none;")
        self.layout.addWidget(self.title_lbl)


class SpeedGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dl_history = [0.0] * 60
        self.ul_history = [0.0] * 60
        self.setFixedHeight(220)
        self.setStyleSheet("background-color: #0b0e18; border-radius: 12px;")

    def add_speeds(self, dl, ul):
        self.dl_history.pop(0)
        self.dl_history.append(dl)
        self.ul_history.pop(0)
        self.ul_history.append(ul)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        margin_left = 60
        margin_right = 20
        margin_top = 20
        margin_bottom = 30
        
        plot_w = w - margin_left - margin_right
        plot_h = h - margin_top - margin_bottom
        
        max_speed = max(max(self.dl_history), max(self.ul_history), 1.0)
        if max_speed < 1.0:
            max_val = 1.0
        elif max_speed < 5.0:
            max_val = 5.0
        elif max_speed < 10.0:
            max_val = 10.0
        elif max_speed < 50.0:
            max_val = 50.0
        else:
            max_val = max_speed * 1.1

        # Draw grid
        grid_pen = QPen(QColor("#1a1f30"), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        
        for i in range(4):
            y = margin_top + i * (plot_h / 3)
            painter.drawLine(margin_left, int(y), w - margin_right, int(y))
            
            val = max_val - i * (max_val / 3)
            val_str = f"{val:.1f} MB/s" if val >= 1.0 else f"{val*1024:.0f} KB/s"
            painter.setPen(QColor("#5a6580"))
            painter.setFont(QFont("Inter", 8))
            painter.drawText(QRectF(10, y - 8, 45, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, val_str)
            painter.setPen(grid_pen)
            
        for i in range(7):
            x = margin_left + i * (plot_w / 6)
            painter.drawLine(int(x), margin_top, int(x), h - margin_bottom)
            
            sec = 60 - i * 10
            sec_str = f"-{sec}s" if sec > 0 else "Now"
            painter.setPen(QColor("#5a6580"))
            painter.setFont(QFont("Inter", 8))
            painter.drawText(QRectF(x - 20, h - margin_bottom + 4, 40, 16), Qt.AlignmentFlag.AlignCenter, sec_str)
            painter.setPen(grid_pen)

        def draw_plot(history, color_line, color_fill):
            path_points = []
            for idx, speed in enumerate(history):
                x = margin_left + idx * (plot_w / 59)
                y = margin_top + plot_h - (speed / max_val) * plot_h
                path_points.append(QPointF(x, y))
                
            from PyQt6.QtGui import QPainterPath
            fill_path = QPainterPath()
            fill_path.moveTo(margin_left, margin_top + plot_h)
            for pt in path_points:
                fill_path.lineTo(pt)
            fill_path.lineTo(w - margin_right, margin_top + plot_h)
            fill_path.closeSubpath()
            
            gradient = QLinearGradient(0, margin_top, 0, margin_top + plot_h)
            c_fill_start = QColor(color_fill)
            c_fill_start.setAlpha(60)
            c_fill_end = QColor(color_fill)
            c_fill_end.setAlpha(0)
            gradient.setColorAt(0, c_fill_start)
            gradient.setColorAt(1, c_fill_end)
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(fill_path)
            
            line_pen = QPen(QColor(color_line), 2)
            painter.setPen(line_pen)
            for idx in range(len(path_points) - 1):
                painter.drawLine(path_points[idx], path_points[idx + 1])

        draw_plot(self.dl_history, "#2563eb", "#2563eb")
        draw_plot(self.ul_history, "#ef4444", "#ef4444")


class PieceMapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.completed_pieces = set()
        self.total_pieces = 0
        self.downloading_pieces = set()
        self.hovered_idx = -1
        self.setMouseTracking(True)
        self.setStyleSheet("background-color: #0b0e18;")
        
    def update_pieces(self, completed, total, downloading=None):
        self.completed_pieces = set(completed)
        self.total_pieces = total
        self.downloading_pieces = set(downloading) if downloading else set()
        self.update()
        
    def mouseMoveEvent(self, event):
        w = self.width()
        box_size = 9
        spacing = 3
        margin = 12
        cols = int((w - 2 * margin) / (box_size + spacing))
        if cols <= 0:
            cols = 1
            
        pos = event.position()
        mx, my = pos.x(), pos.y()
        
        col = int((mx - margin) / (box_size + spacing))
        row = int((my - margin) / (box_size + spacing))
        
        idx = row * cols + col
        if 0 <= idx < self.total_pieces:
            bx = margin + col * (box_size + spacing)
            by = margin + row * (box_size + spacing)
            if bx <= mx <= bx + box_size and by <= my <= by + box_size:
                if self.hovered_idx != idx:
                    self.hovered_idx = idx
                    
                    status = "Missing"
                    if idx in self.completed_pieces:
                        status = "Verified"
                    elif idx in self.downloading_pieces:
                        status = "Downloading"
                        
                    from PyQt6.QtWidgets import QToolTip
                    peer_num = (idx % 6) + 1
                    QToolTip.showText(
                        event.globalPosition().toPoint(),
                        f"Piece #{idx}\nStatus: {status}\nSource: Peer {peer_num}",
                        self
                    )
            else:
                self.hovered_idx = -1
        else:
            self.hovered_idx = -1

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        if self.total_pieces <= 0:
            painter.setPen(QColor("#5a6580"))
            painter.setFont(QFont("Inter", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No active torrent selected")
            return
            
        box_size = 9
        spacing = 3
        margin = 12
        
        cols = int((w - 2 * margin) / (box_size + spacing))
        if cols <= 0:
            cols = 1
            
        for i in range(self.total_pieces):
            row = i // cols
            col = i % cols
            
            x = margin + col * (box_size + spacing)
            y = margin + row * (box_size + spacing)
            
            if y + box_size > h:
                break
                
            if i in self.completed_pieces:
                color = QColor("#22c55e")
            elif i in self.downloading_pieces:
                color = QColor("#2563eb")
            else:
                color = QColor("#1e2438")
                
            painter.fillRect(x, y, box_size, box_size, color)


class SwarmWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.peers = []
        self.setStyleSheet("background-color: #0b0e18;")
        self.setMouseTracking(True)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.timer.start(50)
        self.angle_offset = 0.0
        self.hovered_peer = None

    def _rotate(self):
        self.angle_offset += 0.015
        self.update()

    def set_peers(self, active_peers):
        import hashlib
        self.peers = []
        
        countries = [
            ("🇩🇪", "Germany", "qBittorrent/4.6.3", "8.2 MB/s"),
            ("🇺🇸", "United States", "uTorrent/3.5.5", "4.1 MB/s"),
            ("🇯🇵", "Japan", "Transmission/4.0.2", "1.2 MB/s"),
            ("🇮🇳", "India", "Deluge/2.1.1", "5.6 MB/s"),
            ("🇳🇱", "Netherlands", "qBittorrent/4.6.0", "3.0 MB/s"),
            ("🇨🇦", "Canada", "libtorrent/1.2.19", "0.9 MB/s"),
            ("🇬🇧", "United Kingdom", "uTorrent/3.6.0", "2.1 MB/s")
        ]
        
        for idx, p in enumerate(active_peers):
            ip = p['peer'].ip
            in_use = p['in_use']
            status = 'downloading' if in_use else 'connected'
            
            h_idx = int(hashlib.md5(ip.encode()).hexdigest(), 16) % len(countries)
            flag, country_name, client, mock_speed = countries[h_idx]
            
            self.peers.append({
                'ip': ip,
                'status': status,
                'flag': flag,
                'country': country_name,
                'client': client,
                'speed': mock_speed,
                'x': 0.0,
                'y': 0.0,
                'radius_click': 12
            })
            
        for i in range(max(0, 12 - len(self.peers))):
            ip = f"192.168.1.{i+10}"
            h_idx = int(hashlib.md5(ip.encode()).hexdigest(), 16) % len(countries)
            flag, country_name, client, mock_speed = countries[h_idx]
            self.peers.append({
                'ip': ip,
                'status': 'known',
                'flag': flag,
                'country': country_name,
                'client': client,
                'speed': '0 KB/s',
                'x': 0.0,
                'y': 0.0,
                'radius_click': 12
            })

    def mouseMoveEvent(self, event):
        pos = event.position()
        mx, my = pos.x(), pos.y()
        self.hovered_peer = None
        
        for p in self.peers:
            dist = math.sqrt((p['x'] - mx) ** 2 + (p['y'] - my) ** 2)
            if dist <= p['radius_click']:
                self.hovered_peer = p
                
                from PyQt6.QtWidgets import QToolTip
                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    f"Peer: {p['ip']}\nCountry: {p['flag']} {p['country']}\nSpeed: {p['speed']}\nClient: {p['client']}",
                    self
                )
                break

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        
        # Center node: YOU
        painter.setBrush(QBrush(QColor("#2563eb")))
        painter.setPen(QPen(QColor("#ffffff"), 2))
        painter.drawEllipse(int(cx - 16), int(cy - 16), 32, 32)
        
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Inter", 8, QFont.Weight.Bold))
        painter.drawText(QRectF(cx - 20, cy - 8, 40, 16), Qt.AlignmentFlag.AlignCenter, "YOU")
        
        if not self.peers:
            return
            
        for idx, peer in enumerate(self.peers):
            if peer['status'] == 'downloading':
                radius = 65
                color = QColor("#2563eb")
                line_pen = QPen(color, 1.5, Qt.PenStyle.DashLine)
            elif peer['status'] == 'connected':
                radius = 100
                color = QColor("#22c55e")
                line_pen = QPen(color, 1.2, Qt.PenStyle.SolidLine)
            else:
                radius = 135
                color = QColor("#4b5563")
                line_pen = Qt.PenStyle.NoPen
                
            angle = (idx * (2 * math.pi / len(self.peers))) + self.angle_offset
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            
            peer['x'] = px
            peer['y'] = py
            
            if line_pen != Qt.PenStyle.NoPen:
                painter.setPen(line_pen)
                painter.drawLine(int(cx), int(cy), int(px), int(py))
                
                pulse_pos = (time.time() * 2.0) % 1.0
                dot_x = cx + (px - cx) * pulse_pos
                dot_y = cy + (py - cy) * pulse_pos
                painter.setBrush(QBrush(QColor("#06b6d4")))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(int(dot_x - 3), int(dot_y - 3), 6, 6)
                
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.drawEllipse(int(px - 10), int(py - 10), 20, 20)
            
            painter.setFont(QFont("Inter", 11))
            painter.drawText(QRectF(px - 10, py - 10, 20, 20), Qt.AlignmentFlag.AlignCenter, peer['flag'])


def _kv(key, val="—"):
    kl = QLabel(key)
    kl.setObjectName("detailKey")
    vl = QLabel(str(val))
    vl.setObjectName("detailVal")
    return kl, vl


class DetailPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("detailPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("detailTabs")
        layout.addWidget(self.tabs)

        # Overview tab
        self.overview = QWidget()
        self.overview.setObjectName("detailPanel")
        self.tabs.addTab(self.overview, "Overview")
        self._setup_overview()

        # Files tab
        self.files_w = QWidget()
        self.files_w.setObjectName("detailPanel")
        self.tabs.addTab(self.files_w, "Files")
        self._setup_files()

        # Piece Map tab
        self.piecemap_w = QWidget()
        self.piecemap_w.setObjectName("detailPanel")
        self.tabs.addTab(self.piecemap_w, "Piece Map")
        p_layout = QVBoxLayout(self.piecemap_w)
        self.piece_map = PieceMapWidget(self)
        p_layout.addWidget(self.piece_map)

        # Swarm visualizer tab
        self.swarm_w = QWidget()
        self.swarm_w.setObjectName("detailPanel")
        self.tabs.addTab(self.swarm_w, "Swarm")
        sw_layout = QVBoxLayout(self.swarm_w)
        self.swarm_visualizer = SwarmWidget(self)
        sw_layout.addWidget(self.swarm_visualizer)

        # Peers tab
        self.peers_w = QWidget()
        self.peers_w.setObjectName("detailPanel")
        self.tabs.addTab(self.peers_w, "Peers")
        self._setup_peers()

        # Trackers tab
        self.trackers_w = QWidget()
        self.trackers_w.setObjectName("detailPanel")
        self.tabs.addTab(self.trackers_w, "Trackers")
        fl = QVBoxLayout(self.trackers_w)
        fl.addWidget(QLabel("Tracker information"))

        # Speed tab
        self.speed_w = QWidget()
        self.speed_w.setObjectName("detailPanel")
        self.tabs.addTab(self.speed_w, "Speed")
        sl = QVBoxLayout(self.speed_w)
        self.graph = SpeedGraph()
        sl.addWidget(self.graph)
        sl.addStretch()

        # Log tab
        self.log_w = QWidget()
        self.log_w.setObjectName("detailPanel")
        self.tabs.addTab(self.log_w, "Log")
        self._setup_log()

    def _setup_overview(self):
        layout = QHBoxLayout(self.overview)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Left Card containing Name + Donut Chart + Open Folder button
        self.card_left = DetailCard("No torrent selected", self)
        self.lbl_name = self.card_left.title_lbl
        self.lbl_name.setWordWrap(True)
        self.lbl_name.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold; background: transparent; border: none;")
        
        self.donut = DonutChart()
        self.donut.setFixedSize(90, 90)
        donut_hlayout = QHBoxLayout()
        donut_hlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        donut_hlayout.addWidget(self.donut)
        self.card_left.layout.addLayout(donut_hlayout)
        
        self.btn_open_folder = QPushButton("📁 Open Folder")
        self.btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_folder.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1.5px solid #2563eb;
                border-radius: 999px;
                padding: 8px 16px;
                color: #2563eb;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(37, 99, 235, 0.08);
                color: #3b82f6;
            }
        """)
        self.btn_open_folder.clicked.connect(self._on_open_folder_clicked)
        self.card_left.layout.addWidget(self.btn_open_folder)
        self.card_left.layout.addStretch()

        # 1. Progress Card (Pill progress bar + Sizes)
        self.card_progress = DetailCard("Progress", self)
        
        prog_layout = QHBoxLayout()
        prog_layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1a1f30;
                border-radius: 999px;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2F7CF6, stop:1 #47B2FF);
                border-radius: 999px;
            }
        """)
        
        self.lbl_progress_text = QLabel("0.00 MB / 0.00 MB | 0%")
        self.lbl_progress_text.setStyleSheet("color: #2563eb; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        
        prog_layout.addWidget(self.progress_bar, 1)
        prog_layout.addWidget(self.lbl_progress_text)
        
        self.card_progress.layout.addLayout(prog_layout)
        
        grid_prog = QGridLayout()
        grid_prog.setContentsMargins(0, 4, 0, 0)
        grid_prog.setSpacing(4)
        
        k1, self.v_downloaded = _kv("Downloaded")
        k2, self.v_size = _kv("Total Size")
        k3, self.v_pieces = _kv("Pieces")
        k4, self.v_remaining = _kv("Remaining")
        
        grid_prog.addWidget(k1, 0, 0); grid_prog.addWidget(self.v_downloaded, 0, 1)
        grid_prog.addWidget(k2, 1, 0); grid_prog.addWidget(self.v_size, 1, 1)
        grid_prog.addWidget(k3, 2, 0); grid_prog.addWidget(self.v_pieces, 2, 1)
        grid_prog.addWidget(k4, 3, 0); grid_prog.addWidget(self.v_remaining, 3, 1)
        
        for lbl in [k1, self.v_downloaded, k2, self.v_size, k3, self.v_pieces, k4, self.v_remaining]:
            lbl.setStyleSheet(lbl.styleSheet() + "; background: transparent; border: none;")
            
        self.card_progress.layout.addLayout(grid_prog)
        self.card_progress.layout.addStretch()
        
        # 2. Peers Card (with connected dots)
        self.card_peers = DetailCard("Peers", self)
        self.v_peers = QLabel("0")
        self.v_peers.setStyleSheet("color: #2563eb; font-size: 32px; font-weight: bold; background: transparent; border: none;")
        self.lbl_peer_sub = QLabel("Connected")
        self.lbl_peer_sub.setStyleSheet("color: #8892a8; font-size: 12px; font-weight: 500; background: transparent; border: none;")
        self.lbl_peer_dots = QLabel("•••••")
        self.lbl_peer_dots.setStyleSheet("color: #2563eb; font-size: 18px; font-weight: bold; background: transparent; border: none;")
        self.lbl_peer_swarm = QLabel("In swarm: 0")
        self.lbl_peer_swarm.setStyleSheet("color: #8892a8; font-size: 12px; background: transparent; border: none;")
        
        self.card_peers.layout.addWidget(self.v_peers)
        self.card_peers.layout.addWidget(self.lbl_peer_sub)
        self.card_peers.layout.addWidget(self.lbl_peer_dots)
        self.card_peers.layout.addWidget(self.lbl_peer_swarm)
        self.card_peers.layout.addStretch()
        
        # 3. Seeds Card
        self.card_seeds = DetailCard("Seeds", self)
        self.v_seeds = QLabel("0")
        self.v_seeds.setStyleSheet("color: #22c55e; font-size: 32px; font-weight: bold; background: transparent; border: none;")
        self.lbl_seed_sub = QLabel("Active")
        self.lbl_seed_sub.setStyleSheet("color: #8892a8; font-size: 12px; font-weight: 500; background: transparent; border: none;")
        self.lbl_seed_dots = QLabel("•••••")
        self.lbl_seed_dots.setStyleSheet("color: #22c55e; font-size: 18px; font-weight: bold; background: transparent; border: none;")
        self.lbl_seed_swarm = QLabel("In swarm: 0")
        self.lbl_seed_swarm.setStyleSheet("color: #8892a8; font-size: 12px; background: transparent; border: none;")
        
        self.card_seeds.layout.addWidget(self.v_seeds)
        self.card_seeds.layout.addWidget(self.lbl_seed_sub)
        self.card_seeds.layout.addWidget(self.lbl_seed_dots)
        self.card_seeds.layout.addWidget(self.lbl_seed_swarm)
        self.card_seeds.layout.addStretch()

        # 5. Health Card
        self.card_health = DetailCard("Torrent Health", self)
        self.lbl_health_status = QLabel("🟢 Excellent")
        self.lbl_health_status.setStyleSheet("color: #22c55e; font-size: 14px; font-weight: bold; background: transparent; border: none;")
        
        self.lbl_health_stars = QLabel("★★★★★")
        self.lbl_health_stars.setStyleSheet("color: #22c55e; font-size: 16px; background: transparent; border: none;")
        
        grid_health = QGridLayout()
        grid_health.setContentsMargins(0, 4, 0, 0)
        grid_health.setSpacing(4)
        
        kh1, self.v_health_avail = _kv("Availability")
        kh2, self.v_health_seeds = _kv("Seeds")
        kh3, self.v_health_peers = _kv("Peers")
        kh4, self.v_health_tracker = _kv("Tracker")
        
        grid_health.addWidget(kh1, 0, 0); grid_health.addWidget(self.v_health_avail, 0, 1)
        grid_health.addWidget(kh2, 1, 0); grid_health.addWidget(self.v_health_seeds, 1, 1)
        grid_health.addWidget(kh3, 2, 0); grid_health.addWidget(self.v_health_peers, 2, 1)
        grid_health.addWidget(kh4, 3, 0); grid_health.addWidget(self.v_health_tracker, 3, 1)
        
        for lbl in [kh1, self.v_health_avail, kh2, self.v_health_seeds, kh3, self.v_health_peers, kh4, self.v_health_tracker]:
            lbl.setStyleSheet(lbl.styleSheet() + "; background: transparent; border: none;")
            
        self.card_health.layout.addWidget(self.lbl_health_status)
        self.card_health.layout.addWidget(self.lbl_health_stars)
        self.card_health.layout.addLayout(grid_health)
        self.card_health.layout.addStretch()

        # 6. Timeline Card
        self.card_timeline = DetailCard("Download Timeline", self)
        
        self.vbox_timeline = QVBoxLayout()
        self.vbox_timeline.setSpacing(4)
        self.vbox_timeline.setContentsMargins(0, 4, 0, 0)
        
        self.item_added_title = QLabel("🟢 Added")
        self.item_added_title.setStyleSheet("color: #22c55e; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        self.item_added_time = QLabel("—")
        self.item_added_time.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none; margin-left: 18px;")
        
        self.item_conn_title = QLabel("○ Connecting")
        self.item_conn_title.setStyleSheet("color: #6b7590; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        self.item_conn_time = QLabel("—")
        self.item_conn_time.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none; margin-left: 18px;")
        
        self.item_dl_title = QLabel("○ Downloading")
        self.item_dl_title.setStyleSheet("color: #6b7590; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        self.item_dl_time = QLabel("—")
        self.item_dl_time.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none; margin-left: 18px;")
        
        self.item_seed_title = QLabel("○ Seeding")
        self.item_seed_title.setStyleSheet("color: #6b7590; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        self.item_seed_time = QLabel("—")
        self.item_seed_time.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none; margin-left: 18px;")
        
        self.vbox_timeline.addWidget(self.item_added_title)
        self.vbox_timeline.addWidget(self.item_added_time)
        self.vbox_timeline.addWidget(self.item_conn_title)
        self.vbox_timeline.addWidget(self.item_conn_time)
        self.vbox_timeline.addWidget(self.item_dl_title)
        self.vbox_timeline.addWidget(self.item_dl_time)
        self.vbox_timeline.addWidget(self.item_seed_title)
        self.vbox_timeline.addWidget(self.item_seed_time)
        
        self.card_timeline.layout.addLayout(self.vbox_timeline)
        self.card_timeline.layout.addStretch()

        # 4. Details Card (Copy button next to Hash)
        self.card_details = DetailCard("Details", self)
        det_grid = QGridLayout()
        det_grid.setContentsMargins(0, 0, 0, 0)
        det_grid.setSpacing(4)
        
        kd1, self.v_save = _kv("Save Path")
        kd2, self.v_status = _kv("Status")
        kd3, self.v_eta = _kv("ETA")
        
        kd4 = QLabel("Hash")
        kd4.setObjectName("detailKey")
        self.v_hash = QLabel("—")
        self.v_hash.setObjectName("detailVal")
        
        self.btn_copy_hash = QPushButton("📋")
        self.btn_copy_hash.setFixedSize(22, 22)
        self.btn_copy_hash.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_hash.setStyleSheet("background: transparent; border: none; font-size: 12px; color: #8892a8; padding: 0;")
        self.btn_copy_hash.clicked.connect(self._copy_details_hash)
        
        hash_layout = QHBoxLayout()
        hash_layout.setContentsMargins(0, 0, 0, 0)
        hash_layout.setSpacing(6)
        hash_layout.addWidget(self.v_hash)
        hash_layout.addWidget(self.btn_copy_hash)
        hash_layout.addStretch()
        
        kd5, self.v_added = _kv("Added On")
        kd6, self.v_avail = _kv("Availability")
        kd7, self.v_ratio = _kv("Share Ratio")
        kd8, self.v_active = _kv("Last Active")
        
        det_grid.addWidget(kd1, 0, 0); det_grid.addWidget(self.v_save, 0, 1)
        det_grid.addWidget(kd2, 1, 0); det_grid.addWidget(self.v_status, 1, 1)
        det_grid.addWidget(kd3, 2, 0); det_grid.addWidget(self.v_eta, 2, 1)
        det_grid.addWidget(kd4, 3, 0); det_grid.addLayout(hash_layout, 3, 1)
        det_grid.addWidget(kd5, 4, 0); det_grid.addWidget(self.v_added, 4, 1)
        det_grid.addWidget(kd6, 5, 0); det_grid.addWidget(self.v_avail, 5, 1)
        det_grid.addWidget(kd7, 6, 0); det_grid.addWidget(self.v_ratio, 6, 1)
        det_grid.addWidget(kd8, 7, 0); det_grid.addWidget(self.v_active, 7, 1)
        
        for lbl in [kd1, self.v_save, kd2, self.v_status, kd3, self.v_eta, kd4,
                    kd5, self.v_added, kd6, self.v_avail, kd7,
                    self.v_ratio, kd8, self.v_active]:
            lbl.setStyleSheet(lbl.styleSheet() + "; background: transparent; border: none;")
            
        self.card_details.layout.addLayout(det_grid)
        self.card_details.layout.addStretch()

        layout.addWidget(self.card_left, 3)
        layout.addWidget(self.card_progress, 4)
        layout.addWidget(self.card_peers, 3)
        layout.addWidget(self.card_seeds, 3)
        layout.addWidget(self.card_health, 3)
        layout.addWidget(self.card_timeline, 3)
        layout.addWidget(self.card_details, 4)

    def _on_open_folder_clicked(self):
        p = self.window()
        if hasattr(p, "_open_folder"):
            p._open_folder()

    def _copy_details_hash(self):
        h = self.v_hash.text()
        if h and h != "—":
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(h)
            p = self.window()
            if hasattr(p, "_show_toast"):
                p._show_toast("✓ Hash Copied")

    def _setup_files(self):
        layout = QVBoxLayout(self.files_w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.tree_files = QTreeWidget()
        self.tree_files.setObjectName("fileTree")
        self.tree_files.setHeaderLabels(["Filename / Path", "Size"])
        self.tree_files.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tree_files.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tree_files.header().resizeSection(0, 500)
        layout.addWidget(self.tree_files)

    def _setup_peers(self):
        layout = QVBoxLayout(self.peers_w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table_peers = QTableWidget()
        self.table_peers.setObjectName("peerTable")
        self.table_peers.setColumnCount(7)
        self.table_peers.setHorizontalHeaderLabels([
            "IP Address", "Country", "Client", "Speed", "Pieces", "Latency", "Progress"
        ])
        self.table_peers.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_peers)

    def _setup_log(self):
        layout = QVBoxLayout(self.log_w)
        layout.setContentsMargins(0, 0, 0, 0)
        self.txt_log = QTextEdit()
        self.txt_log.setObjectName("logConsole")
        self.txt_log.setReadOnly(True)
        layout.addWidget(self.txt_log)
