from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QHeaderView, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from gui.donut_chart import DonutChart


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
        sl.addWidget(QLabel("Speed graph"))

        # Log tab
        self.log_w = QWidget()
        self.log_w.setObjectName("detailPanel")
        self.tabs.addTab(self.log_w, "Log")
        self._setup_log()

    def _setup_overview(self):
        layout = QHBoxLayout(self.overview)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(24)

        # Donut chart
        self.donut = DonutChart()
        layout.addWidget(self.donut)

        # Info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        # Torrent name
        self.lbl_name = QLabel("No torrent selected")
        self.lbl_name.setObjectName("detailName")
        info_layout.addWidget(self.lbl_name)

        # Details grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(6)

        k, self.v_save = _kv("Save Path")
        grid.addWidget(k, 0, 0); grid.addWidget(self.v_save, 0, 1)
        k, self.v_size = _kv("Total Size")
        grid.addWidget(k, 1, 0); grid.addWidget(self.v_size, 1, 1)
        k, self.v_pieces = _kv("Pieces")
        grid.addWidget(k, 2, 0); grid.addWidget(self.v_pieces, 2, 1)
        k, self.v_hash = _kv("Hash")
        grid.addWidget(k, 3, 0); grid.addWidget(self.v_hash, 3, 1)

        info_layout.addLayout(grid)
        info_layout.addStretch()
        layout.addLayout(info_layout, 1)

        # Right stats section
        right_grid = QGridLayout()
        right_grid.setHorizontalSpacing(40)
        right_grid.setVerticalSpacing(6)

        k, self.v_status = _kv("Status")
        right_grid.addWidget(k, 0, 0); right_grid.addWidget(self.v_status, 0, 1)
        k, self.v_downloaded = _kv("Downloaded")
        right_grid.addWidget(k, 1, 0); right_grid.addWidget(self.v_downloaded, 1, 1)
        k, self.v_remaining = _kv("Remaining")
        right_grid.addWidget(k, 2, 0); right_grid.addWidget(self.v_remaining, 2, 1)
        k, self.v_eta = _kv("ETA")
        right_grid.addWidget(k, 3, 0); right_grid.addWidget(self.v_eta, 3, 1)
        k, self.v_added = _kv("Added On")
        right_grid.addWidget(k, 4, 0); right_grid.addWidget(self.v_added, 4, 1)

        right_col = QVBoxLayout()
        right_col.addLayout(right_grid)
        right_col.addStretch()
        layout.addLayout(right_col, 1)

        # Far right stats
        far_grid = QGridLayout()
        far_grid.setHorizontalSpacing(40)
        far_grid.setVerticalSpacing(6)

        k, self.v_peers = _kv("Peers Connected")
        far_grid.addWidget(k, 0, 0); far_grid.addWidget(self.v_peers, 0, 1)
        k, self.v_seeds = _kv("Seeds")
        far_grid.addWidget(k, 1, 0); far_grid.addWidget(self.v_seeds, 1, 1)
        k, self.v_avail = _kv("Availability")
        far_grid.addWidget(k, 2, 0); far_grid.addWidget(self.v_avail, 2, 1)
        k, self.v_ratio = _kv("Share Ratio")
        far_grid.addWidget(k, 3, 0); far_grid.addWidget(self.v_ratio, 3, 1)
        k, self.v_active = _kv("Last Active")
        far_grid.addWidget(k, 4, 0); far_grid.addWidget(self.v_active, 4, 1)

        far_col = QVBoxLayout()
        far_col.addLayout(far_grid)
        far_col.addStretch()
        layout.addLayout(far_col, 1)

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
        self.table_peers.setColumnCount(6)
        self.table_peers.setHorizontalHeaderLabels([
            "IP Address", "Port", "Active?", "Avg Speed", "Block Successes", "Network Failures"
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
