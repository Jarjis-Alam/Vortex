import os
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QProgressBar,
    QTabWidget, QTextEdit, QFileDialog, QSplitter,
    QTreeWidget, QTreeWidgetItem, QLabel, QHeaderView,
    QAbstractItemView, QToolButton, QGraphicsEffect, QMessageBox,
    QMenu, QDialog, QLineEdit, QPushButton
)
from PyQt6.QtCore import QTimer, Qt, QObject, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty, QSize
from PyQt6.QtGui import QAction, QIcon, QColor, QPixmap

class BouncyButton(QToolButton):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setText(text)

class MagnetDialog(QDialog):
    def __init__(self, parent=None, default_save_dir="."):
        super().__init__(parent)
        self.setWindowTitle("Add Magnet Link")
        self.resize(500, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_magnet = QLabel("Magnet URI:")
        self.txt_magnet = QTextEdit()
        self.txt_magnet.setPlaceholderText("magnet:?xt=urn:btih:...")
        
        lbl_save = QLabel("Save Path:")
        self.txt_save = QLineEdit(default_save_dir)
        self.btn_browse = QPushButton("Browse")
        self.btn_browse.clicked.connect(self.browse_save_dir)
        
        save_layout = QHBoxLayout()
        save_layout.addWidget(self.txt_save)
        save_layout.addWidget(self.btn_browse)
        
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_download = QPushButton("Download")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_download.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_download)
        
        layout.addWidget(lbl_magnet)
        layout.addWidget(self.txt_magnet)
        layout.addWidget(lbl_save)
        layout.addLayout(save_layout)
        layout.addLayout(btn_layout)
        
    def browse_save_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Save Directory", self.txt_save.text())
        if dir_path:
            self.txt_save.setText(dir_path)
            
    def get_data(self):
        return self.txt_magnet.toPlainText().strip(), self.txt_save.text().strip()

from torrent_manager import TorrentManager

def format_speed(speed_mb):
    if speed_mb >= 1.0:
        return f"{speed_mb:.2f} MB/s"
    else:
        return f"{speed_mb * 1024:.1f} KB/s"

def format_size(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"

def format_eta(seconds):
    if seconds is None or seconds < 0 or seconds == float('inf'):
        return "∞"
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    seconds %= 60
    if minutes < 60:
        return f"{minutes}m {seconds}s"
    hours = minutes // 60
    minutes %= 60
    return f"{hours}h {minutes}m"

class LogSignaler(QObject):
    log_signal = pyqtSignal(str)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vortex")
        self.resize(1000, 650)
        
        # Ensure icon resources exist
        import shutil
        src_resume = "/home/jarjis/.gemini/antigravity/brain/7d114df7-267c-421e-9513-46238f4a6f8a/media__1782303921094.png"
        src_pause = "/home/jarjis/.gemini/antigravity/brain/7d114df7-267c-421e-9513-46238f4a6f8a/media__1782304036316.png"
        src_remove = "/home/jarjis/.gemini/antigravity/brain/7d114df7-267c-421e-9513-46238f4a6f8a/media__1782304486047.png"
        src_about = "/home/jarjis/.gemini/antigravity/brain/7d114df7-267c-421e-9513-46238f4a6f8a/media__1782304173487.png"
        src_logo = "/home/jarjis/.gemini/antigravity/brain/7d114df7-267c-421e-9513-46238f4a6f8a/media__1782304275212.png"
        src_add = "/home/jarjis/.gemini/antigravity/brain/7d114df7-267c-421e-9513-46238f4a6f8a/media__1782304581869.png"
        src_magnet = "/home/jarjis/.gemini/antigravity/brain/7d114df7-267c-421e-9513-46238f4a6f8a/media__1782305106390.png"
        dest_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")
        os.makedirs(dest_dir, exist_ok=True)
        
        dest_resume = os.path.join(dest_dir, "resume.png")
        dest_pause = os.path.join(dest_dir, "pause.png")
        dest_remove = os.path.join(dest_dir, "remove.png")
        dest_about = os.path.join(dest_dir, "about.png")
        dest_logo = os.path.join(dest_dir, "logo.png")
        dest_add = os.path.join(dest_dir, "add.png")
        dest_magnet = os.path.join(dest_dir, "magnet.png")
        
        def make_icon_white(src_path, dest_path):
            if not os.path.exists(src_path):
                return
            try:
                from PyQt6.QtGui import QImage, QColor
                img = QImage(src_path)
                if not img.isNull():
                    img = img.convertToFormat(QImage.Format.Format_ARGB32)
                    for y in range(img.height()):
                        for x in range(img.width()):
                            c = QColor.fromRgba(img.pixel(x, y))
                            if c.alpha() > 0:
                                img.setPixel(x, y, QColor(255, 255, 255, c.alpha()).rgba())
                    img.save(dest_path)
            except Exception as e:
                print(f"Failed to colorize icon {src_path}: {e}")

        make_icon_white(src_resume, dest_resume)
        make_icon_white(src_pause, dest_pause)
        make_icon_white(src_remove, dest_remove)
        make_icon_white(src_about, dest_about)
        make_icon_white(src_add, dest_add)
        make_icon_white(src_magnet, dest_magnet)

        if os.path.exists(src_logo):
            try:
                shutil.copy(src_logo, dest_logo)
            except Exception as e:
                print(f"Failed to copy logo icon: {e}")

        if os.path.exists(dest_logo):
            self.setWindowIcon(QIcon(dest_logo))
        
        self.manager = TorrentManager()
        self.selected_task = None
        
        # Thread-safe logging signaler
        self.log_signaler = LogSignaler()
        self.log_signaler.log_signal.connect(self.append_log)
        
        self.init_ui()
        self.apply_theme()
        
        # Setup periodic GUI polling timer (1.0s interval)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gui_stats)
        self.timer.start(1000)
        
        self.log("Vortex GUI initialized.")
        
        # Single-shot timer for clipboard check on startup
        QTimer.singleShot(1000, self.check_clipboard_on_startup)

    def init_ui(self):
        # Create Toolbar
        toolbar = self.addToolBar("Controls")
        toolbar.setMovable(False)
        
        # Toolbar Actions
        self.btn_add = BouncyButton(" Add ▼", self)
        self.btn_add.setObjectName("btn_add")
        add_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "add.png")
        if os.path.exists(add_icon_path):
            self.btn_add.setIcon(QIcon(add_icon_path))
            self.btn_add.setIconSize(QSize(14, 14))
            self.btn_add.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        else:
            self.btn_add.setText("➕ Add ▼")
            
        # Add Dropdown Menu
        self.add_menu = QMenu(self)
        self.action_add_file = self.add_menu.addAction("Add Torrent File")
        self.action_add_magnet = self.add_menu.addAction("Add Magnet Link")
        self.action_paste_clipboard = self.add_menu.addAction("Paste from Clipboard")
        
        # Set icon for action_add_magnet
        magnet_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "magnet.png")
        if os.path.exists(magnet_icon_path):
            self.action_add_magnet.setIcon(QIcon(magnet_icon_path))
            
        self.action_add_file.triggered.connect(self.add_torrent_clicked)
        self.action_add_magnet.triggered.connect(self.add_magnet_clicked)
        self.action_paste_clipboard.triggered.connect(self.add_paste_clicked)
        
        self.btn_add.setMenu(self.add_menu)
        self.btn_add.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar.addWidget(self.btn_add)
        
        # Dedicated Magnet Link Button
        self.btn_magnet = BouncyButton(" Magnet Link", self)
        self.btn_magnet.setObjectName("btn_magnet")
        if os.path.exists(magnet_icon_path):
            self.btn_magnet.setIcon(QIcon(magnet_icon_path))
            self.btn_magnet.setIconSize(QSize(14, 14))
            self.btn_magnet.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        else:
            self.btn_magnet.setText("🧲 Magnet Link")
        self.btn_magnet.clicked.connect(self.add_magnet_clicked)
        toolbar.addWidget(self.btn_magnet)
        
        toolbar.addSeparator()
        
        self.btn_resume = BouncyButton(" Resume", self)
        self.btn_resume.setObjectName("btn_resume")
        resume_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "resume.png")
        if os.path.exists(resume_icon_path):
            self.btn_resume.setIcon(QIcon(resume_icon_path))
            self.btn_resume.setIconSize(QSize(14, 14))
            self.btn_resume.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        else:
            self.btn_resume.setText("▶️ Resume")
        self.btn_resume.clicked.connect(self.resume_clicked)
        toolbar.addWidget(self.btn_resume)
        
        self.btn_pause = BouncyButton(" Pause", self)
        self.btn_pause.setObjectName("btn_pause")
        pause_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "pause.png")
        if os.path.exists(pause_icon_path):
            self.btn_pause.setIcon(QIcon(pause_icon_path))
            self.btn_pause.setIconSize(QSize(14, 14))
            self.btn_pause.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        else:
            self.btn_pause.setText("⏸️ Pause")
        self.btn_pause.clicked.connect(self.pause_clicked)
        toolbar.addWidget(self.btn_pause)
        
        self.btn_remove = BouncyButton(" Remove", self)
        self.btn_remove.setObjectName("btn_remove")
        remove_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "remove.png")
        if os.path.exists(remove_icon_path):
            self.btn_remove.setIcon(QIcon(remove_icon_path))
            self.btn_remove.setIconSize(QSize(14, 14))
            self.btn_remove.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        else:
            self.btn_remove.setText("❌ Remove")
        self.btn_remove.clicked.connect(self.remove_clicked)
        toolbar.addWidget(self.btn_remove)
        
        toolbar.addSeparator()
        
        self.btn_about = BouncyButton(" About", self)
        self.btn_about.setObjectName("btn_about")
        about_icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "about.png")
        if os.path.exists(about_icon_path):
            self.btn_about.setIcon(QIcon(about_icon_path))
            self.btn_about.setIconSize(QSize(14, 14))
            self.btn_about.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        else:
            self.btn_about.setText("❓ About")
        self.btn_about.clicked.connect(self.show_about_dialog)
        toolbar.addWidget(self.btn_about)
        

        
        # Central layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Vertical Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)
        
        # Top Table: Torrents List
        self.table_torrents = QTableWidget()
        self.table_torrents.setColumnCount(8)
        self.table_torrents.setHorizontalHeaderLabels([
            "Name", "Size", "Progress", "Status", "Down Speed", "Up Speed", "ETA", "Peers"
        ])
        self.table_torrents.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_torrents.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table_torrents.horizontalHeader().resizeSection(0, 300)
        self.table_torrents.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_torrents.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_torrents.itemSelectionChanged.connect(self.torrent_selection_changed)
        splitter.addWidget(self.table_torrents)
        
        # Bottom Tabs
        self.tabs = QTabWidget()
        splitter.addWidget(self.tabs)
        
        # Tab 1: General Stats
        self.tab_general = QWidget()
        self.tab_general.setObjectName("tab_general")
        self.tabs.addTab(self.tab_general, "General")
        self.setup_general_tab()
        
        # Tab 2: File List
        self.tab_files = QWidget()
        self.tab_files.setObjectName("tab_files")
        self.tabs.addTab(self.tab_files, "Files")
        self.setup_files_tab()
        
        # Tab 3: Peer Connections
        self.tab_peers = QWidget()
        self.tab_peers.setObjectName("tab_peers")
        self.tabs.addTab(self.tab_peers, "Peers")
        self.setup_peers_tab()
        
        # Tab 4: Console Log
        self.tab_log = QWidget()
        self.tab_log.setObjectName("tab_log")
        self.tabs.addTab(self.tab_log, "Log Console")
        self.setup_log_tab()
        
        # Set splitter sizes
        splitter.setSizes([300, 250])

    def setup_general_tab(self):
        layout = QHBoxLayout(self.tab_general)
        
        # Left Panel (Download Details)
        self.panel_left = QVBoxLayout()
        self.lbl_downloaded = QLabel("Downloaded: 0 B")
        self.lbl_remaining = QLabel("Remaining: 0 B")
        self.lbl_duration = QLabel("Duration: 0s")
        self.lbl_eta = QLabel("ETA: ∞")
        self.lbl_pieces = QLabel("Pieces: 0 / 0")
        
        self.panel_left.addWidget(self.lbl_downloaded)
        self.panel_left.addWidget(self.lbl_remaining)
        self.panel_left.addWidget(self.lbl_duration)
        self.panel_left.addWidget(self.lbl_eta)
        self.panel_left.addWidget(self.lbl_pieces)
        self.panel_left.addStretch()
        
        # Right Panel (Swarm / Health Details)
        self.panel_right = QVBoxLayout()
        self.lbl_connected_peers = QLabel("Peers Connected: 0")
        self.lbl_active_peers = QLabel("Peers Active: 0")
        self.lbl_reconnects = QLabel("Swarm Reconnects: 0")
        self.lbl_hash_failures = QLabel("Hash Failures: 0")
        self.lbl_save_path = QLabel("Save Path: N/A")
        
        self.panel_right.addWidget(self.lbl_connected_peers)
        self.panel_right.addWidget(self.lbl_active_peers)
        self.panel_right.addWidget(self.lbl_reconnects)
        self.panel_right.addWidget(self.lbl_hash_failures)
        self.panel_right.addWidget(self.lbl_save_path)
        self.panel_right.addStretch()
        
        layout.addLayout(self.panel_left, stretch=1)
        layout.addLayout(self.panel_right, stretch=1)

    def setup_files_tab(self):
        layout = QVBoxLayout(self.tab_files)
        self.tree_files = QTreeWidget()
        self.tree_files.setHeaderLabels(["Filename / Path", "Size"])
        self.tree_files.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tree_files.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tree_files.header().resizeSection(0, 500)
        layout.addWidget(self.tree_files)

    def setup_peers_tab(self):
        layout = QVBoxLayout(self.tab_peers)
        self.table_peers = QTableWidget()
        self.table_peers.setColumnCount(6)
        self.table_peers.setHorizontalHeaderLabels([
            "IP Address", "Port", "Active?", "Avg Speed", "Block Successes", "Network Failures"
        ])
        self.table_peers.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_peers)

    def setup_log_tab(self):
        layout = QVBoxLayout(self.tab_log)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        layout.addWidget(self.txt_log)

    def apply_theme(self):
        # Dark glassmorphic style with neon blue/cyan gradients matching original design
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d0f17;
            }
            QWidget {
                color: #e2e8f0;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 13px;
            }
            QWidget#tab_general, QWidget#tab_files, QWidget#tab_peers, QWidget#tab_log {
                background-color: #171a26;
            }
            QMenuBar {
                background-color: #0d0f17;
                border-bottom: 1px solid #282e3e;
            }
            QMenuBar::item:selected {
                background-color: #282e3e;
                color: #ffffff;
            }
            QToolBar {
                background-color: #0d0f17;
                border-bottom: 1px solid #282e3e;
                spacing: 12px;
                padding: 10px;
            }
            QToolButton {
                background-color: #171a26;
                border: 1px solid #282e3e;
                border-radius: 20px;
                padding: 10px 24px;
                min-height: 20px;
                color: #ffffff;
                font-weight: bold;
                margin-top: 0px;
                margin-bottom: 0px;
            }
            QToolButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2d79f3, stop:1 #00d2ff);
                color: #ffffff;
                border: 1px solid #00d2ff;
                margin-top: -6px;
                margin-bottom: 6px;
            }
            QToolButton:pressed {
                background-color: #0d0f17;
                border: 1px solid #2d79f3;
            }
            QTableWidget, QTreeWidget {
                background-color: #171a26;
                alternate-background-color: #1a1e2b;
                border: 1px solid #282e3e;
                border-radius: 14px;
                gridline-color: #282e3e;
                color: #e2e8f0;
            }
            QTableWidget::item, QTreeWidget::item {
                padding: 10px;
                border-bottom: 1px solid #1f2330;
            }
            QTableWidget::item:selected, QTreeWidget::item:selected {
                background-color: rgba(45, 121, 243, 0.15);
                color: #00d2ff;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #171a26;
                color: #708090;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #282e3e;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #282e3e;
                border-radius: 14px;
                background-color: #171a26;
            }
            QTabBar::tab {
                background-color: #121520;
                border: 1px solid #282e3e;
                border-bottom-color: transparent;
                padding: 10px 22px;
                color: #708090;
                font-weight: bold;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                margin-right: 6px;
            }
            QTabBar::tab:selected {
                background-color: #171a26;
                color: #00d2ff;
                border-bottom-color: #171a26;
                border-top: 2px solid #2d79f3;
            }
            QProgressBar {
                border: 1px solid #282e3e;
                border-radius: 12px;
                text-align: center;
                background-color: #0d0f17;
                color: #ffffff;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2d79f3, stop:1 #00d2ff);
                border-radius: 12px;
            }
            QTextEdit {
                background-color: #0a0c12;
                border: 1px solid #282e3e;
                border-radius: 12px;
                color: #00d2ff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                padding: 10px;
            }
            QLabel {
                font-weight: bold;
                color: #ffffff;
            }
            QSplitter::handle {
                background-color: #282e3e;
            }
            QDialog, QMessageBox {
                background-color: #171a26;
                border: 1px solid #282e3e;
            }
            QPushButton {
                background-color: #171a26;
                border: 1px solid #282e3e;
                border-radius: 12px;
                padding: 6px 16px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2d79f3, stop:1 #00d2ff);
                color: #ffffff;
                border: 1px solid #00d2ff;
            }
            QLineEdit {
                background-color: #0d0f17;
                border: 1px solid #282e3e;
                border-radius: 8px;
                padding: 6px 12px;
                color: #ffffff;
            }
            QMenu {
                background-color: #171a26;
                border: 1px solid #282e3e;
                color: #ffffff;
            }
            QMenu::item {
                background-color: transparent;
                padding: 8px 24px;
            }
            QMenu::item:selected {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2d79f3, stop:1 #00d2ff);
                color: #ffffff;
            }
        """)

    def show_about_dialog(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About Vortex")
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            msg.setIconPixmap(scaled_pixmap)
        else:
            msg.setIcon(QMessageBox.Icon.Information)
            
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        
        text = """
        <div style='font-family: Segoe UI, Inter, sans-serif; color: #e2e8f0;'>
            <h2 style='color: #00d2ff; margin-top: 0;'>Vortex</h2>
            <p>A powerful BitTorrent client.</p>
            <p><b>Version:</b> 1.0.0</p>
            <hr style='border: none; border-top: 1px solid #282e3e; margin: 12px 0;'/>
            <h3 style='color: #00d2ff;'>Developer Details</h3>
            <p><b>Name:</b> Munshi Jarjis Alam</p>
            <p><b>Instagram:</b> <a href="https://www.instagram.com/jarvis._exe_" style="color: #00d2ff; text-decoration: none;">https://www.instagram.com/jarvis._exe_</a></p>
            <p><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/jarjisalam/" style="color: #00d2ff; text-decoration: none;">https://www.linkedin.com/in/jarjisalam/</a></p>
            <p><b>GitHub:</b> <a href="https://github.com/Jarjis-Alam" style="color: #00d2ff; text-decoration: none;">https://github.com/Jarjis-Alam</a></p>
        </div>
        """
        msg.setText(text)
        msg.exec()

    def log(self, msg):
        self.log_signaler.log_signal.emit(msg)

    def append_log(self, msg):
        timestamp = time.strftime("[%H:%M:%S]")
        self.txt_log.append(f"{timestamp} {msg}")

    def update_cell(self, table, row, col, text):
        item = table.item(row, col)
        if not item:
            item = QTableWidgetItem(text)
            table.setItem(row, col, item)
        elif item.text() != text:
            item.setText(text)

    def add_torrent_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Torrent File", "", "Torrent Files (*.torrent)"
        )
        if not file_path:
            return
            
        task = self.manager.add_torrent(file_path)
        self.log(f"Adding torrent: {os.path.basename(file_path)}")
        
        # Start download task
        task.start()
        self.selected_task = task
        
        # Populate Files list immediately
        self.populate_files_list(task)
        
        # Refresh the torrents table
        self.refresh_torrents_table()

    def add_magnet_clicked(self):
        dialog = MagnetDialog(self, default_save_dir=".")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            magnet_uri, save_dir = dialog.get_data()
            if magnet_uri:
                self.process_add_magnet(magnet_uri, save_dir)
                
    def add_paste_clicked(self):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard().text().strip()
        if clipboard.startswith("magnet:?"):
            self.add_magnet_by_uri(clipboard)
        else:
            QMessageBox.information(
                self,
                "Paste from Clipboard",
                "No valid magnet link found in clipboard."
            )
            
    def add_magnet_by_uri(self, uri):
        dialog = MagnetDialog(self, default_save_dir=".")
        dialog.txt_magnet.setPlainText(uri)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            magnet_uri, save_dir = dialog.get_data()
            if magnet_uri:
                self.process_add_magnet(magnet_uri, save_dir)
                
    def process_add_magnet(self, magnet_uri, save_dir):
        task = self.manager.add_magnet(magnet_uri, save_dir)
        if task:
            task.start()
            self.selected_task = task
            self.populate_files_list(task)
            self.refresh_torrents_table()
            self.log(f"Added magnet link: {magnet_uri[:60]}...")
            
    def check_clipboard_on_startup(self):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard().text().strip()
        if clipboard.startswith("magnet:?"):
            reply = QMessageBox.question(
                self,
                "Magnet Link Detected",
                f"A magnet link was detected in your clipboard:\n\n{clipboard[:100]}...\n\nDo you want to download it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.add_magnet_by_uri(clipboard)

    def resume_clicked(self):
        if self.selected_task:
            self.selected_task.resume()
            self.log(f"Resumed torrent: {self.selected_task.torrent.get_name().decode('utf-8', errors='ignore')}")
            self.refresh_torrents_table()

    def pause_clicked(self):
        if self.selected_task:
            self.selected_task.pause()
            self.log(f"Paused torrent: {self.selected_task.torrent.get_name().decode('utf-8', errors='ignore')}")
            self.refresh_torrents_table()

    def remove_clicked(self):
        if self.selected_task:
            task_name = self.selected_task.torrent.get_name().decode('utf-8', errors='ignore')
            self.log(f"Removing torrent: {task_name}")
            self.manager.remove_torrent(self.selected_task)
            self.selected_task = None
            
            # Clear files list, peers, and stats
            self.tree_files.clear()
            self.table_peers.setRowCount(0)
            self.clear_general_stats()
            
            self.refresh_torrents_table()

    def torrent_selection_changed(self):
        selected_rows = self.table_torrents.selectedItems()
        if not selected_rows:
            self.selected_task = None
            self.tree_files.clear()
            self.table_peers.setRowCount(0)
            self.clear_general_stats()
            return
            
        row = selected_rows[0].row()
        if row < len(self.manager.tasks):
            self.selected_task = self.manager.tasks[row]
            
            # Hook the download manager's log callback
            if self.selected_task.manager:
                self.selected_task.manager.log_callback = self.log
                
            self.populate_files_list(self.selected_task)
            self.update_gui_stats()

    def populate_files_list(self, task):
        self.tree_files.clear()
        torrent = task.torrent
        
        # Single-file torrent
        if b'length' in torrent.info:
            name = torrent.get_name().decode('utf-8', errors='ignore')
            size = torrent.info[b'length']
            item = QTreeWidgetItem([name, format_size(size)])
            self.tree_files.addTopLevelItem(item)
            return
            
        # Multi-file torrent
        if b'files' in torrent.info:
            root_name = torrent.get_name().decode('utf-8', errors='ignore')
            root_item = QTreeWidgetItem([root_name, ""])
            self.tree_files.addTopLevelItem(root_item)
            
            for f in torrent.info[b'files']:
                path_parts = [p.decode('utf-8', errors='ignore') for p in f[b'path']]
                size = f[b'length']
                
                # Traverse tree to insert node
                current_node = root_item
                for part in path_parts[:-1]:
                    # Search for existing child
                    found = False
                    for i in range(current_node.childCount()):
                        if current_node.child(i).text(0) == part:
                            current_node = current_node.child(i)
                            found = True
                            break
                    if not found:
                        new_node = QTreeWidgetItem([part, ""])
                        current_node.addChild(new_node)
                        current_node = new_node
                
                # Append leaf
                leaf = QTreeWidgetItem([path_parts[-1], format_size(size)])
                current_node.addChild(leaf)
            root_item.setExpanded(True)

    def refresh_torrents_table(self):
        self.table_torrents.setRowCount(len(self.manager.tasks))
        for idx, task in enumerate(self.manager.tasks):
            name = task.torrent.get_name().decode('utf-8', errors='ignore')
            size_bytes = task.torrent.get_size()
            
            completed_count = 0
            if task.manager:
                with task.manager.completed_lock:
                    completed_count = len(task.manager.completed)
            piece_count = task.torrent.get_piece_count()
            
            progress = (completed_count / piece_count) * 100.0 if piece_count > 0 else 0.0
            
            status = task.status
            
            # Speeds and ETA
            down_speed = 0.0
            up_speed = 0.0
            eta = None
            peers = 0
            
            if task.manager:
                total_elapsed = time.time() - task.manager.start_time if task.manager.start_time else 0
                with task.manager.stats_lock:
                    downloaded_bytes = task.manager.session_bytes
                
                if total_elapsed > 0:
                    down_speed = (downloaded_bytes / (1024 * 1024)) / total_elapsed
                
                if task.status == "Paused":
                    down_speed = 0.0
                    
                # Simple ETA
                if down_speed > 0:
                    remaining_bytes = size_bytes - (completed_count * task.torrent.get_piece_length())
                    if remaining_bytes > 0:
                        eta = (remaining_bytes / (1024 * 1024)) / down_speed
                
                with task.manager.pool.lock:
                    peers = len([p for p in task.manager.pool.active_peers if p['in_use']])
            
            # Row contents
            self.update_cell(self.table_torrents, idx, 0, name)
            self.update_cell(self.table_torrents, idx, 1, format_size(size_bytes))
            
            # Progress bar widget
            pbar = self.table_torrents.cellWidget(idx, 2)
            if not pbar:
                pbar = QProgressBar()
                self.table_torrents.setCellWidget(idx, 2, pbar)
            pbar.setValue(int(progress))
            
            self.update_cell(self.table_torrents, idx, 3, status)
            self.update_cell(self.table_torrents, idx, 4, format_speed(down_speed))
            self.update_cell(self.table_torrents, idx, 5, format_speed(up_speed))
            self.update_cell(self.table_torrents, idx, 6, format_eta(eta))
            self.update_cell(self.table_torrents, idx, 7, str(peers))

    def clear_general_stats(self):
        self.lbl_downloaded.setText("Downloaded: 0 B")
        self.lbl_remaining.setText("Remaining: 0 B")
        self.lbl_duration.setText("Duration: 0s")
        self.lbl_eta.setText("ETA: ∞")
        self.lbl_pieces.setText("Pieces: 0 / 0")
        
        self.lbl_connected_peers.setText("Peers Connected: 0")
        self.lbl_active_peers.setText("Peers Active: 0")
        self.lbl_reconnects.setText("Swarm Reconnects: 0")
        self.lbl_hash_failures.setText("Hash Failures: 0")
        self.lbl_save_path.setText("Save Path: N/A")

    def update_gui_stats(self):
        # Refresh primary table
        self.refresh_torrents_table()
        
        if not self.selected_task:
            return
            
        task = self.selected_task
        torrent = task.torrent
        
        completed_count = 0
        if task.manager:
            with task.manager.completed_lock:
                completed_count = len(task.manager.completed)
        piece_count = torrent.get_piece_count()
        piece_length = torrent.get_piece_length()
        
        # Compute sizes
        total_size = torrent.get_size()
        downloaded = completed_count * piece_length
        if downloaded > total_size:
            downloaded = total_size
        remaining = total_size - downloaded
        
        self.lbl_downloaded.setText(f"Downloaded: {format_size(downloaded)}")
        self.lbl_remaining.setText(f"Remaining: {format_size(remaining)}")
        
        # Duration & ETA
        if task.manager:
            duration = int(time.time() - task.manager.start_time) if task.manager.start_time else 0
            self.lbl_duration.setText(f"Duration: {duration}s")
            
            # ETA
            with task.manager.stats_lock:
                downloaded_bytes = task.manager.session_bytes
            down_speed = (downloaded_bytes / (1024 * 1024)) / duration if duration > 0 else 0
            if task.status == "Paused":
                down_speed = 0.0
                
            eta = None
            if down_speed > 0:
                eta = (remaining / (1024 * 1024)) / down_speed
            self.lbl_eta.setText(f"ETA: {format_eta(eta)}")
            
            self.lbl_pieces.setText(f"Pieces: {completed_count} / {piece_count}")
            
            # Swarm stats
            with task.manager.pool.lock:
                connected = len(task.manager.pool.active_peers)
                active = sum(1 for p in task.manager.pool.active_peers if p['in_use'])
                reconnects = task.manager.pool.reconnect_count
                
            with task.manager.stats_lock:
                failures = task.manager.hash_failures
                
            self.lbl_connected_peers.setText(f"Peers Connected: {connected}")
            self.lbl_active_peers.setText(f"Peers Active: {active}")
            self.lbl_reconnects.setText(f"Swarm Reconnects: {reconnects}")
            self.lbl_hash_failures.setText(f"Hash Failures: {failures}")
            self.lbl_save_path.setText(f"Save Path: {task.output_filename}")
            
            # Populate Peers Tab Table
            self.update_peers_tab_table(task)

    def update_peers_tab_table(self, task):
        if not task.manager or not task.manager.pool:
            self.table_peers.setRowCount(0)
            return
            
        with task.manager.pool.lock:
            active_peers = list(task.manager.pool.active_peers)
            
        self.table_peers.setRowCount(len(active_peers))
        
        for idx, p in enumerate(active_peers):
            peer_conn = p['peer']
            ip = peer_conn.ip
            port = peer_conn.port
            in_use = "Yes" if p['in_use'] else "No"
            
            stats = task.manager.pool.peer_stats.get(f"{ip}:{port}")
            if stats:
                speed = format_speed(stats['average_speed'])
                successes = str(stats['successes'])
                failures = str(stats['failures'] + stats['timeouts'])
            else:
                speed = "0.00 KB/s"
                successes = "0"
                failures = "0"
                
            self.update_cell(self.table_peers, idx, 0, ip)
            self.update_cell(self.table_peers, idx, 1, str(port))
            self.update_cell(self.table_peers, idx, 2, in_use)
            self.update_cell(self.table_peers, idx, 3, speed)
            self.update_cell(self.table_peers, idx, 4, successes)
            self.update_cell(self.table_peers, idx, 5, failures)

    def closeEvent(self, event):
        # Stop all tasks when window closes to avoid background orphan threads
        self.log("Closing main window. Stopping all torrent tasks...")
        for task in self.manager.tasks:
            task.stop()
        event.accept()
