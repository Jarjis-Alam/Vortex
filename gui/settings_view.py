import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFileDialog, QFrame, QGridLayout,
    QListWidget, QStackedWidget, QTextEdit, QScrollArea, QTabWidget,
    QAbstractButton, QSpinBox, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath

# ── Modern Toggle Switch Widget ──
class ModernSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(48, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_rect = self.rect()
        radius = bg_rect.height() / 2
        
        # Colors based on check status
        if self.isChecked():
            bg_color = QColor("#2563eb")  # Modern Blue
            handle_x = self.width() - self.height() + 2
        else:
            bg_color = QColor("#1e2438")  # Dark Slate Gray
            handle_x = 2
            
        # Draw background pill
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bg_rect, radius, radius)
        
        # Draw white handle knob
        handle_size = self.height() - 4
        handle_rect = QRectF(handle_x, 2, handle_size, handle_size)
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(handle_rect)

    def hitButton(self, pos):
        return self.rect().contains(pos)


# ── Setting Row Wrapper ──
class SettingRow(QFrame):
    hovered = pyqtSignal(str, str, str)  # Title, Description, Preview Key
    
    def __init__(self, title, description, control_widget, preview_key="", category="", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.preview_key = preview_key
        self.category = category
        self.control_widget = control_widget
        self.setObjectName("settingRow")
        self.setStyleSheet("""
            QFrame#settingRow {
                background: transparent;
                border: none;
                border-radius: 8px;
            }
            QFrame#settingRow:hover {
                background: rgba(255, 255, 255, 0.02);
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(16)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 600; background: transparent; border: none;")
        
        self.lbl_desc = QLabel(description)
        self.lbl_desc.setStyleSheet("color: #8892a8; font-size: 12px; background: transparent; border: none;")
        self.lbl_desc.setWordWrap(True)
        
        text_layout.addWidget(self.lbl_title)
        text_layout.addWidget(self.lbl_desc)
        
        layout.addLayout(text_layout, 1)
        layout.addWidget(control_widget)
        
    def enterEvent(self, event):
        self.hovered.emit(self.title, self.description, self.preview_key)
        super().enterEvent(event)


# ── Better Group Box Card Container ──
class SettingsCard(QFrame):
    def __init__(self, title, icon_char="", parent=None):
        super().__init__(parent)
        self.setObjectName("settingsCard")
        self.setStyleSheet("""
            QFrame#settingsCard {
                background-color: #141828;
                border: 1px solid #1e2438;
                border-radius: 12px;
            }
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(16)
        
        # Card Header
        self.header_lbl = QLabel(title)
        self.header_lbl.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: bold; border: none; background: transparent;")
        self.layout.addWidget(self.header_lbl)
        
        # Horizontal Separator line
        self.sep = QFrame()
        self.sep.setFrameShape(QFrame.Shape.HLine)
        self.sep.setStyleSheet("color: #1e2438; border: none; background-color: #1e2438; max-height: 1px;")
        self.layout.addWidget(self.sep)
        
    def add_setting_row(self, row):
        self.layout.addWidget(row)


# ── Sleek Interactive Help & Preview Panel ──
class HelpPreviewPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("helpPreviewPanel")
        self.setStyleSheet("""
            QFrame#helpPreviewPanel {
                background-color: #141828;
                border: 1px solid #1e2438;
                border-radius: 12px;
            }
        """)
        self.setFixedWidth(280)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)
        
        # Header
        self.lbl_header = QLabel("💡 Live Guide & Preview")
        self.lbl_header.setStyleSheet("color: #3b82f6; font-size: 11px; font-weight: bold; text-transform: uppercase; background: transparent; border: none;")
        layout.addWidget(self.lbl_header)
        
        # Title
        self.lbl_title = QLabel("Vortex Settings Control")
        self.lbl_title.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: bold; background: transparent; border: none;")
        self.lbl_title.setWordWrap(True)
        layout.addWidget(self.lbl_title)
        
        # Description
        self.lbl_desc = QLabel("Hover over any configuration on the left to see descriptive tips, settings references, and real-time interactive previews here.")
        self.lbl_desc.setStyleSheet("color: #8892a8; font-size: 12px; background: transparent; border: none;")
        self.lbl_desc.setWordWrap(True)
        layout.addWidget(self.lbl_desc)
        
        # Spacer
        layout.addSpacing(10)
        
        # Interactive Preview Widget Wrapper
        self.preview_container = QWidget()
        self.preview_container.setStyleSheet("background: transparent;")
        self.preview_layout = QVBoxLayout(self.preview_container)
        self.preview_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_layout.setSpacing(0)
        layout.addWidget(self.preview_container)
        
        layout.addStretch()
        
    def show_help(self, title, desc, preview_key, current_accent_color="Blue"):
        self.lbl_title.setText(title)
        self.lbl_desc.setText(desc)
        
        # Clear previous preview widget
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        preview_widget = self._create_preview(preview_key, current_accent_color)
        if preview_widget:
            self.preview_layout.addWidget(preview_widget)
            
    def _create_preview(self, key, accent_color):
        widget = QFrame()
        widget.setObjectName("previewInner")
        widget.setStyleSheet("""
            QFrame#previewInner {
                background-color: #0f1220;
                border: 1px solid #1e2438;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                background: transparent;
                border: none;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        
        accent_hex = {
            "Blue": "#2563eb",
            "Green": "#22c55e",
            "Orange": "#f97316",
            "Red": "#ef4444",
            "Purple": "#bd93f9",
            "None": "#2563eb"
        }.get(accent_color, "#2563eb")
        
        if key == "theme":
            title = QLabel("Theme Selection")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            # Draw color circle grids
            palette_layout = QGridLayout()
            palette_layout.setSpacing(8)
            colors = ["#0b0e18", "#282a36", "#000000", "#2e3440", "#1e1e2e", "#f0f2f5"]
            labels = ["Midnight", "Dracula", "AMOLED", "Nord", "Catppuccin", "Light"]
            for idx, (c, l) in enumerate(zip(colors, labels)):
                dot = QFrame()
                dot.setFixedSize(16, 16)
                dot.setStyleSheet(f"background-color: {c}; border: 1px solid #1e2438; border-radius: 8px;")
                lbl = QLabel(l)
                lbl.setStyleSheet("font-size: 11px; color: #8892a8;")
                
                cell = QHBoxLayout()
                cell.setSpacing(6)
                cell.addWidget(dot)
                cell.addWidget(lbl)
                palette_layout.addLayout(cell, idx // 2, idx % 2)
            layout.addLayout(palette_layout)
            return widget
            
        elif key == "accent":
            title = QLabel("Accent Live Preview")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            preview_btn = QPushButton("Active Accent State")
            preview_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {accent_hex};
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 12px;
                    font-weight: bold;
                }}
            """)
            layout.addWidget(preview_btn)
            return widget
            
        elif key == "font_size":
            title = QLabel("Typography Scale")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            lbl1 = QLabel("12px: Small Metadata text")
            lbl1.setStyleSheet("font-size: 12px; color: #8892a8;")
            lbl2 = QLabel("14px: Standard settings label")
            lbl2.setStyleSheet("font-size: 14px; color: #ffffff;")
            lbl3 = QLabel("16px: Section Header text")
            lbl3.setStyleSheet("font-size: 16px; color: #ffffff; font-weight: bold;")
            
            layout.addWidget(lbl1)
            layout.addWidget(lbl2)
            layout.addWidget(lbl3)
            return widget
            
        elif key == "animations":
            title = QLabel("Interface Micro-Animation")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            # Small visual indicator representing animation pulsing
            pulse_indicator = QFrame()
            pulse_indicator.setFixedHeight(30)
            pulse_indicator.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {accent_hex}40, stop:1 transparent);
                    border-left: 3px solid {accent_hex};
                    border-radius: 4px;
                }}
            """)
            lbl = QLabel("Smooth transition effect active")
            lbl.setStyleSheet("font-size: 11px; color: #ffffff; padding-left: 8px;")
            p_layout = QHBoxLayout(pulse_indicator)
            p_layout.setContentsMargins(0, 0, 0, 0)
            p_layout.addWidget(lbl)
            
            layout.addWidget(pulse_indicator)
            return widget
            
        elif key == "compact":
            title = QLabel("Row Format Layout")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            row_norm = QFrame()
            row_norm.setStyleSheet("background: #141828; border-radius: 4px; padding: 6px;")
            rn_l = QHBoxLayout(row_norm)
            rn_l.setContentsMargins(4, 4, 4, 4)
            rn_l.addWidget(QLabel("Normal view (48px)"))
            rn_l.addStretch()
            rn_l.addWidget(QLabel("📂"))
            
            row_comp = QFrame()
            row_comp.setStyleSheet("background: #141828; border-radius: 4px; padding: 2px;")
            rc_l = QHBoxLayout(row_comp)
            rc_l.setContentsMargins(4, 2, 4, 2)
            rc_l.addWidget(QLabel("Compact view (36px)"))
            rc_l.addStretch()
            rc_l.addWidget(QLabel("📂"))
            
            layout.addWidget(row_norm)
            layout.addWidget(row_comp)
            return widget
            
        elif key == "disk_space":
            title = QLabel("Disk Allocation Status")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            # Simple progress bar to simulate pre-allocation
            prog = QFrame()
            prog.setFixedHeight(8)
            prog.setStyleSheet(f"background: {accent_hex}; border-radius: 4px;")
            layout.addWidget(prog)
            
            lbl = QLabel("Preallocating 3.64 GB on disk...")
            lbl.setStyleSheet("font-size: 11px; color: #8892a8;")
            layout.addWidget(lbl)
            return widget
            
        elif key == "sequential":
            title = QLabel("Download Strategy Block Map")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            blocks = QHBoxLayout()
            blocks.setSpacing(4)
            for i in range(8):
                b = QFrame()
                b.setFixedSize(14, 14)
                # Left filled blocks (sequential) vs scattered
                color = accent_hex if i < 5 else "#1e2438"
                b.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
                blocks.addWidget(b)
            layout.addLayout(blocks)
            
            lbl = QLabel("Blocks filled sequentially [0-4]")
            lbl.setStyleSheet("font-size: 11px; color: #8892a8;")
            layout.addWidget(lbl)
            return widget
            
        elif key == "port":
            title = QLabel("Connection Listener Status")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            status_row = QHBoxLayout()
            status_row.setSpacing(8)
            dot = QFrame()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet("background-color: #22c55e; border-radius: 5px;")
            lbl = QLabel("Port check: Status OPEN")
            lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #ffffff;")
            status_row.addWidget(dot)
            status_row.addWidget(lbl)
            status_row.addStretch()
            layout.addLayout(status_row)
            return widget
            
        elif key == "encryption":
            title = QLabel("Traffic Encryption Shield")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            lbl = QLabel("🔒 Protocol RC4 Encryption active")
            lbl.setStyleSheet("font-size: 12px; color: #22c55e; font-weight: bold;")
            layout.addWidget(lbl)
            return widget
            
        elif key == "upnp":
            title = QLabel("Universal Plug and Play Mapping")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            lbl = QLabel("⚡ Router mapping active: TCP/UDP 6881")
            lbl.setStyleSheet("font-size: 11px; color: #8892a8;")
            layout.addWidget(lbl)
            return widget
            
        elif key == "dht":
            title = QLabel("Swarm DHT Discovery")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            lbl = QLabel("🌐 Swarm node mapping active:\n425 distributed routing table peers")
            lbl.setStyleSheet("font-size: 11px; color: #8892a8;")
            layout.addWidget(lbl)
            return widget
            
        elif key == "startup":
            title = QLabel("Autostart Manager")
            title.setStyleSheet("font-weight: bold; font-size: 12px; color: #8892a8;")
            layout.addWidget(title)
            
            lbl = QLabel("🖥 Startup daemon: Active")
            lbl.setStyleSheet("font-size: 12px; color: #ffffff;")
            layout.addWidget(lbl)
            return widget
            
        return None


# ── Main Settings View Class ──
class SettingsView(QWidget):
    def __init__(self, parent_window=None):
        super().__init__(parent_window)
        self.parent_win = parent_window
        self.setObjectName("detailPanel")
        
        self.saved_settings = {}
        self.all_setting_rows = []
        self.all_group_boxes = []
        self.tab_widget_list = []  # To track Advanced Page subtabs
        
        self._init_defaults()
        self._load_settings_file()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # 16. Header Breadcrumb & Search Row
        header_layout = QHBoxLayout()
        self.lbl_breadcrumb = QLabel("⚙ Settings  ›  General")
        self.lbl_breadcrumb.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff; background: transparent;")
        header_layout.addWidget(self.lbl_breadcrumb)
        
        header_layout.addStretch()
        
        # 11. Add Search Settings
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Search settings... (e.g. startup)")
        self.txt_search.setFixedWidth(240)
        self.txt_search.textChanged.connect(self._on_search_settings)
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background-color: #0f1220;
                border: 1px solid #1e2438;
                border-radius: 8px;
                padding: 6px 12px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        header_layout.addWidget(self.txt_search)
        main_layout.addLayout(header_layout)
        
        # Body Splitter
        body_layout = QHBoxLayout()
        body_layout.setSpacing(20)
        
        # 2. Better Settings Navigation & Left Panel
        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)
        
        self.cat_list = QListWidget()
        # 3. Increase Left Panel Width by 30px (180 -> 210)
        self.cat_list.setFixedWidth(210)
        self.cat_list.setObjectName("sidebarList")
        self.cat_list.setStyleSheet("""
            QListWidget#sidebarList {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QListWidget#sidebarList::item {
                padding: 12px 14px;
                color: #8892a8;
                font-weight: 500;
                font-size: 14px;
                border-radius: 8px;
                margin-bottom: 4px;
            }
            QListWidget#sidebarList::item:selected {
                background-color: rgba(37, 99, 235, 0.12);
                color: #ffffff;
                font-weight: bold;
                border-left: 4px solid #2563eb;
            }
            QListWidget#sidebarList::item:hover {
                background-color: rgba(255, 255, 255, 0.04);
                color: #ffffff;
            }
        """)
        
        # Navigation Items
        self.cat_list.addItems([
            "⚙ General",
            "⬇ Downloads",
            "🎨 Appearance",
            "🌐 Network",
            "🔧 Advanced"
        ])
        self.cat_list.setCurrentRow(0)
        self.cat_list.currentRowChanged.connect(self._category_changed)
        left_panel.addWidget(self.cat_list)
        
        # Left Panel Spacer
        left_panel.addStretch()
        
        # 15. Import / Export
        ie_layout = QHBoxLayout()
        btn_import = QPushButton("Import")
        btn_export = QPushButton("Export")
        btn_import.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1e2438;
                border-radius: 6px;
                color: #8892a8;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.04);
                color: #ffffff;
                border-color: #2563eb;
            }
        """)
        btn_export.setStyleSheet(btn_import.styleSheet())
        btn_import.clicked.connect(self._import_settings)
        btn_export.clicked.connect(self._export_settings)
        ie_layout.addWidget(btn_import)
        ie_layout.addWidget(btn_export)
        left_panel.addLayout(ie_layout)
        
        # 14. Add Restore Defaults
        btn_restore = QPushButton("Restore Defaults")
        btn_restore.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1e2438;
                border-radius: 6px;
                color: #8892a8;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.1);
                border-color: #ef4444;
                color: #ef4444;
            }
        """)
        btn_restore.clicked.connect(self._restore_defaults)
        left_panel.addWidget(btn_restore)
        
        body_layout.addLayout(left_panel)
        
        # 17. Content scrollable area container (Comfortably scales to 900px content width)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.setMaximumWidth(900)
        
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        
        self.settings_controls = {}
        self._init_pages()
        
        self.scroll_area.setWidget(self.stack)
        body_layout.addWidget(self.scroll_area, 1)
        
        # Right Side Guide/Preview Panel
        self.guide_panel = HelpPreviewPanel(self)
        body_layout.addWidget(self.guide_panel)
        
        main_layout.addLayout(body_layout, 1)
        
        # 8, 9, 10. Sticky Apply / Reset Bar at the bottom
        self.sticky_bar = QFrame()
        self.sticky_bar.setObjectName("stickyBar")
        self.sticky_bar.setStyleSheet("""
            QFrame#stickyBar {
                background-color: #141828;
                border: 1px solid #2563eb;
                border-radius: 12px;
                padding: 12px 24px;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
                background: transparent;
            }
        """)
        self.sticky_bar.setFixedHeight(64)
        self.sticky_bar.hide()  # Only shown when there are unsaved changes
        
        sticky_layout = QHBoxLayout(self.sticky_bar)
        sticky_layout.setContentsMargins(16, 0, 16, 0)
        
        self.lbl_unsaved = QLabel("⚠️ You have unsaved configuration changes")
        sticky_layout.addWidget(self.lbl_unsaved)
        
        sticky_layout.addStretch()
        
        btn_reset = QPushButton("Reset")
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1e2438;
                border-radius: 6px;
                color: #8892a8;
                font-weight: bold;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.04);
                color: #ffffff;
            }
        """)
        btn_reset.clicked.connect(self._reset_changes)
        sticky_layout.addWidget(btn_reset)
        
        # 9. Apply Button
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                border: none;
                border-radius: 6px;
                color: #ffffff;
                font-weight: bold;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3b82f6;
            }
        """)
        self.btn_apply.clicked.connect(self._apply_settings)
        sticky_layout.addWidget(self.btn_apply)
        
        main_layout.addWidget(self.sticky_bar)
        
        self._load_settings_into_controls()
        self._connect_signals()

    def _init_defaults(self):
        self.DEFAULTS = {
            "start_minimized": False,
            "associate_magnet": True,
            "skip_magnet_dialog": False,
            "launch_startup": False,
            "show_notifications": True,
            "play_sound": False,
            "download_folder": ".",
            "max_active_downloads": "4",
            "preallocate_space": True,
            "sequential_download": False,
            "theme": "Vortex Glass",
            "accent_color": "None (Use Theme Default)",
            "font_size": "14px",
            "animations": True,
            "compact_mode": False,
            "ui_scale": "100%",
            "corner_radius": "12px",
            "listening_port": "6881",
            "upnp": True,
            "nat_pmp": True,
            "encryption": "Prefer Encryption",
            "dht": True,
            "pex": True,
            "lsd": True,
            "download_limit": "Unlimited",
            "upload_limit": "Unlimited",
            "dht_rate_limit": False,
            "peer_exchange": True,
            "max_conn_torrent": "200",
            "max_conn_global": "500",
            "disk_cache_size": "64",
            "cache_writeback": True,
            "multithread_verify": True,
            "thread_pool_size": "Auto",
            "secure_scratch": False,
            "validate_ssl": True,
            "webui_v2": False,
            "experimental_discovery": False,
            "custom_qss": ""
        }
        self.saved_settings = dict(self.DEFAULTS)

    def _load_settings_file(self):
        try:
            from session_manager import get_vortex_dir
            path = os.path.join(get_vortex_dir(), "settings.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    loaded = json.load(f)
                    for k, v in loaded.items():
                        if k in self.saved_settings:
                            self.saved_settings[k] = v
        except Exception:
            pass

    def _save_settings_file(self):
        try:
            from session_manager import get_vortex_dir
            path = os.path.join(get_vortex_dir(), "settings.json")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(self.saved_settings, f, indent=4)
        except Exception:
            pass

    def _load_settings_into_controls(self):
        # Set values to GUI controls
        self.sw_start_min.setChecked(self.saved_settings["start_minimized"])
        self.sw_assoc_magnet.setChecked(self.saved_settings["associate_magnet"])
        self.sw_launch_startup.setChecked(self.saved_settings["launch_startup"])
        
        self.sw_notif.setChecked(self.saved_settings["show_notifications"])
        self.sw_sound.setChecked(self.saved_settings["play_sound"])
        
        self.txt_save.setText(self.saved_settings["download_folder"])
        self.txt_active_downloads.setText(self.saved_settings["max_active_downloads"])
        self.sw_preallocate.setChecked(self.saved_settings["preallocate_space"])
        self.sw_sequential.setChecked(self.saved_settings["sequential_download"])
        
        self.theme_combo.setCurrentText(self.saved_settings["theme"])
        self.accent_combo.setCurrentText(self.saved_settings["accent_color"])
        self.font_combo.setCurrentText(self.saved_settings["font_size"])
        self.sw_animations.setChecked(self.saved_settings["animations"])
        self.sw_compact.setChecked(self.saved_settings["compact_mode"])
        self.scale_combo.setCurrentText(self.saved_settings["ui_scale"])
        self.radius_combo.setCurrentText(self.saved_settings["corner_radius"])
        
        self.txt_port.setText(self.saved_settings["listening_port"])
        self.sw_upnp.setChecked(self.saved_settings["upnp"])
        self.sw_nat_pmp.setChecked(self.saved_settings["nat_pmp"])
        self.encryption_combo.setCurrentText(self.saved_settings["encryption"])
        self.sw_dht.setChecked(self.saved_settings["dht"])
        self.sw_pex.setChecked(self.saved_settings["pex"])
        self.sw_lsd.setChecked(self.saved_settings["lsd"])
        self.txt_dl_limit.setText(self.saved_settings["download_limit"])
        self.txt_ul_limit.setText(self.saved_settings["upload_limit"])
        
        self.sw_dht_rate.setChecked(self.saved_settings["dht_rate_limit"])
        self.sw_pex_adv.setChecked(self.saved_settings["peer_exchange"])
        self.txt_max_conn_torrent.setText(self.saved_settings["max_conn_torrent"])
        self.txt_max_conn_global.setText(self.saved_settings["max_conn_global"])
        self.txt_disk_cache.setText(self.saved_settings["disk_cache_size"])
        self.sw_cache_wb.setChecked(self.saved_settings["cache_writeback"])
        self.sw_workers.setChecked(self.saved_settings["multithread_verify"])
        self.thread_pool_combo.setCurrentText(self.saved_settings["thread_pool_size"])
        self.sw_secure_scratch.setChecked(self.saved_settings["secure_scratch"])
        self.sw_validate_ssl.setChecked(self.saved_settings["validate_ssl"])
        self.sw_webui.setChecked(self.saved_settings["webui_v2"])
        self.sw_experimental_disc.setChecked(self.saved_settings["experimental_discovery"])
        self.txt_custom_css.setPlainText(self.saved_settings["custom_qss"])
        
        # Hide sticky changes bar when newly loaded
        self.sticky_bar.hide()

    def _get_control_value(self, ctrl):
        if isinstance(ctrl, ModernSwitch):
            return ctrl.isChecked()
        elif isinstance(ctrl, QComboBox):
            return ctrl.currentText()
        elif isinstance(ctrl, QLineEdit):
            return ctrl.text()
        elif isinstance(ctrl, QTextEdit):
            return ctrl.toPlainText()
        return None

    def _connect_signals(self):
        for key, ctrl in self.settings_controls.items():
            if isinstance(ctrl, ModernSwitch):
                ctrl.toggled.connect(self._check_for_changes)
            elif isinstance(ctrl, QComboBox):
                ctrl.currentTextChanged.connect(self._check_for_changes)
            elif isinstance(ctrl, QLineEdit):
                ctrl.textChanged.connect(self._check_for_changes)
            elif isinstance(ctrl, QTextEdit):
                ctrl.textChanged.connect(self._check_for_changes)

    def _check_for_changes(self):
        changed = False
        for key, ctrl in self.settings_controls.items():
            current_val = self._get_control_value(ctrl)
            saved_val = self.saved_settings.get(key)
            if current_val != saved_val:
                changed = True
                break
        
        self.sticky_bar.setVisible(changed)
        
        # Check accent color instant live preview
        current_accent = self.accent_combo.currentText()
        if self.parent_win and hasattr(self.parent_win, "apply_custom_accent"):
            self.parent_win.apply_custom_accent(current_accent)

    def _reset_changes(self):
        self._load_settings_into_controls()
        self._check_for_changes()

    def _apply_settings(self):
        # Save all controls to dict
        for key, ctrl in self.settings_controls.items():
            self.saved_settings[key] = self._get_control_value(ctrl)
            
        self._save_settings_file()
        self.sticky_bar.hide()
        
        # Apply visual rules
        if self.parent_win:
            if hasattr(self.parent_win, "change_theme"):
                self.parent_win.change_theme(self.saved_settings["theme"])
            if hasattr(self.parent_win, "apply_custom_accent"):
                self.parent_win.apply_custom_accent(self.saved_settings["accent_color"])
            if hasattr(self.parent_win, "apply_custom_qss"):
                self.parent_win.apply_custom_qss(self.saved_settings["custom_qss"])
            if hasattr(self.parent_win, "_show_toast"):
                self.parent_win._show_toast("✓ Settings applied and saved successfully")

    def _restore_defaults(self):
        for k, v in self.DEFAULTS.items():
            ctrl = self.settings_controls.get(k)
            if ctrl:
                if isinstance(ctrl, ModernSwitch):
                    ctrl.setChecked(v)
                elif isinstance(ctrl, QComboBox):
                    ctrl.setCurrentText(v)
                elif isinstance(ctrl, QLineEdit):
                    ctrl.setText(v)
                elif isinstance(ctrl, QTextEdit):
                    ctrl.setPlainText(v)
        self._check_for_changes()

    def _import_settings(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Settings JSON", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "r") as f:
                    loaded = json.load(f)
                    for k, v in loaded.items():
                        ctrl = self.settings_controls.get(k)
                        if ctrl:
                            if isinstance(ctrl, ModernSwitch):
                                ctrl.setChecked(v)
                            elif isinstance(ctrl, QComboBox):
                                ctrl.setCurrentText(v)
                            elif isinstance(ctrl, QLineEdit):
                                ctrl.setText(v)
                            elif isinstance(ctrl, QTextEdit):
                                ctrl.setPlainText(v)
                self._check_for_changes()
                if self.parent_win and hasattr(self.parent_win, "_show_toast"):
                    self.parent_win._show_toast("✓ Settings imported (Click Apply to save)")
            except Exception as e:
                if self.parent_win and hasattr(self.parent_win, "_show_toast"):
                    self.parent_win._show_toast(f"✗ Failed to import settings: {e}", type="error")

    def _export_settings(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Settings JSON", "settings_export.json", "JSON Files (*.json)")
        if path:
            try:
                current_state = {}
                for key, ctrl in self.settings_controls.items():
                    current_state[key] = self._get_control_value(ctrl)
                with open(path, "w") as f:
                    json.dump(current_state, f, indent=4)
                if self.parent_win and hasattr(self.parent_win, "_show_toast"):
                    self.parent_win._show_toast("✓ Settings exported successfully")
            except Exception as e:
                if self.parent_win and hasattr(self.parent_win, "_show_toast"):
                    self.parent_win._show_toast(f"✗ Failed to export settings: {e}", type="error")

    def _category_changed(self, idx):
        if idx >= 0:
            self.stack.setCurrentIndex(idx)
            text = self.cat_list.item(idx).text()
            self.lbl_breadcrumb.setText(f"⚙ Settings  ›  {text.split()[-1]}")

    def _create_setting_row(self, title, desc, control, preview_key="", category=""):
        row = SettingRow(title, desc, control, preview_key, category, self)
        row.hovered.connect(lambda t, d, pk: self.guide_panel.show_help(t, d, pk, self.accent_combo.currentText()))
        self.all_setting_rows.append(row)
        return row

    def _on_search_settings(self, query):
        query = query.lower().strip()
        
        if not query:
            # Restore categories and group boxes
            for idx in range(self.cat_list.count()):
                self.cat_list.item(idx).setHidden(False)
            for row in self.all_setting_rows:
                row.show()
            for box in self.all_group_boxes:
                box.show()
            # Restore TabWidgets
            for tab_widget, pages in self.tab_widget_list:
                tab_widget.clear()
                for page, title in pages:
                    tab_widget.addTab(page, title)
            return

        matching_categories = set()
        
        # 1. Filter rows by query
        for row in self.all_setting_rows:
            match = (query in row.title.lower()) or (query in row.description.lower())
            row.setVisible(match)
            if match:
                matching_categories.add(row.category)
                
        # 2. Filter group boxes (hide if all children rows are hidden)
        for box in self.all_group_boxes:
            visible_rows = [r for r in box.findChildren(SettingRow) if r.isVisible()]
            box.setVisible(len(visible_rows) > 0)
            
        # 3. Filter Advanced page subtabs
        for tab_widget, pages in self.tab_widget_list:
            tab_widget.clear()
            for page, title in pages:
                visible_rows = [r for r in page.findChildren(SettingRow) if r.isVisible()]
                if len(visible_rows) > 0:
                    tab_widget.addTab(page, title)
                    
        # 4. Filter left category list
        first_match_idx = -1
        for idx in range(self.cat_list.count()):
            text = self.cat_list.item(idx).text().split()[-1]  # Get e.g. "General"
            has_match = text in matching_categories
            self.cat_list.item(idx).setHidden(not has_match)
            if has_match and first_match_idx == -1:
                first_match_idx = idx
                
        if first_match_idx != -1:
            self.cat_list.setCurrentRow(first_match_idx)

    def _browse_save_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Save Directory", self.txt_save.text())
        if d:
            self.txt_save.setText(d)

    def _init_pages(self):
        # Setup spacing variables
        # 13. Spacing between cards/sections: 32px
        vertical_spacing = 32
        
        # ── Page 0: General ──
        p0 = QWidget()
        l0 = QVBoxLayout(p0)
        l0.setContentsMargins(0, 0, 10, 0)
        l0.setSpacing(vertical_spacing)
        
        # Section 1: System Behavior
        c_sys = SettingsCard("System Behavior", "⚙")
        self.all_group_boxes.append(c_sys)
        
        self.sw_start_min = ModernSwitch()
        row_min = self._create_setting_row(
            "Start minimized",
            "Automatically starts Vortex minimized in the system tray instead of showing the main window.",
            self.sw_start_min, "startup", "General"
        )
        self.settings_controls["start_minimized"] = self.sw_start_min
        c_sys.add_setting_row(row_min)
        
        self.sw_assoc_magnet = ModernSwitch()
        self.sw_assoc_magnet.setToolTip("Allows magnet links opened from your browser to launch Vortex automatically.")
        row_assoc = self._create_setting_row(
            "Associate magnet links",
            "Enables browser magnet protocol interception. Allows magnet links opened from your browser to launch Vortex automatically.",
            self.sw_assoc_magnet, "encryption", "General"
        )
        self.settings_controls["associate_magnet"] = self.sw_assoc_magnet
        c_sys.add_setting_row(row_assoc)
        
        self.sw_launch_startup = ModernSwitch()
        row_startup = self._create_setting_row(
            "Launch application on startup",
            "Starts Vortex automatically when your system logs in, ensuring daemon is always active.",
            self.sw_launch_startup, "startup", "General"
        )
        self.settings_controls["launch_startup"] = self.sw_launch_startup
        c_sys.add_setting_row(row_startup)
        
        l0.addWidget(c_sys)
        
        # Section 2: Notifications
        c_notif = SettingsCard("Notifications", "🔔")
        self.all_group_boxes.append(c_notif)
        
        self.sw_notif = ModernSwitch()
        row_notif = self._create_setting_row(
            "Show desktop notifications",
            "Displays a bubble notification alert on your operating system upon download completion.",
            self.sw_notif, "animations", "General"
        )
        self.settings_controls["show_notifications"] = self.sw_notif
        c_notif.add_setting_row(row_notif)
        
        self.sw_sound = ModernSwitch()
        row_sound = self._create_setting_row(
            "Play sound alert on integrity checks",
            "Plays an audio cue when checking finishes on a torrent download.",
            self.sw_sound, "animations", "General"
        )
        self.settings_controls["play_sound"] = self.sw_sound
        c_notif.add_setting_row(row_sound)
        
        l0.addWidget(c_notif)
        l0.addStretch()
        self.stack.addWidget(p0)
        
        # ── Page 1: Downloads ──
        p1 = QWidget()
        l1 = QVBoxLayout(p1)
        l1.setContentsMargins(0, 0, 10, 0)
        l1.setSpacing(vertical_spacing)
        
        # 21. Downloads Page
        c_dirs = SettingsCard("Save Locations", "⬇")
        self.all_group_boxes.append(c_dirs)
        
        browse_container = QWidget()
        bc_layout = QHBoxLayout(browse_container)
        bc_layout.setContentsMargins(0, 0, 0, 0)
        bc_layout.setSpacing(8)
        self.txt_save = QLineEdit(".")
        self.txt_save.setMinimumWidth(260)
        self.btn_browse = QPushButton("Browse")
        self.btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #1e2438;
                border: 1px solid #2d3650;
                border-radius: 6px;
                padding: 6px 14px;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2d3650;
            }
        """)
        self.btn_browse.clicked.connect(self._browse_save_dir)
        bc_layout.addWidget(self.txt_save)
        bc_layout.addWidget(self.btn_browse)
        
        row_dir = self._create_setting_row(
            "Default Download Folder",
            "Set the path where downloaded torrent payloads will be saved.",
            browse_container, "theme", "Downloads"
        )
        self.settings_controls["download_folder"] = self.txt_save
        c_dirs.add_setting_row(row_dir)
        l1.addWidget(c_dirs)
        
        c_queue = SettingsCard("Queue Limits & Allocation", "⬇")
        self.all_group_boxes.append(c_queue)
        
        self.txt_active_downloads = QLineEdit("4")
        self.txt_active_downloads.setFixedWidth(80)
        self.txt_active_downloads.setStyleSheet("background-color: #0f1220; border: 1px solid #1e2438; border-radius: 6px; padding: 4px; color: #ffffff;")
        row_max_dl = self._create_setting_row(
            "Maximum Active Downloads",
            "Specify the maximum number of concurrent active downloads Vortex will allow.",
            self.txt_active_downloads, "font_size", "Downloads"
        )
        self.settings_controls["max_active_downloads"] = self.txt_active_downloads
        c_queue.add_setting_row(row_max_dl)
        
        self.sw_preallocate = ModernSwitch()
        row_prealloc = self._create_setting_row(
            "Preallocate Disk Space",
            "Allocates full disk storage size block prior to starting download of blocks, preventing write fragmentation.",
            self.sw_preallocate, "disk_space", "Downloads"
        )
        self.settings_controls["preallocate_space"] = self.sw_preallocate
        c_queue.add_setting_row(row_prealloc)
        
        self.sw_sequential = ModernSwitch()
        row_seq = self._create_setting_row(
            "Sequential Download",
            "Instructs the client to download file pieces in strict numerical order. Useful for live preview/streaming.",
            self.sw_sequential, "sequential", "Downloads"
        )
        self.settings_controls["sequential_download"] = self.sw_sequential
        c_queue.add_setting_row(row_seq)
        
        l1.addWidget(c_queue)
        l1.addStretch()
        self.stack.addWidget(p1)
        
        # ── Page 2: Appearance ──
        p2 = QWidget()
        l2 = QVBoxLayout(p2)
        l2.setContentsMargins(0, 0, 10, 0)
        l2.setSpacing(vertical_spacing)
        
        # 22. Appearance Settings Card
        c_appearance = SettingsCard("Appearance Settings", "🎨")
        self.all_group_boxes.append(c_appearance)
        
        # Theme Combobox
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Vortex Glass", "Midnight Blue", "Dracula", "AMOLED", "Nord", "Catppuccin", "Light"])
        self.theme_combo.setFixedWidth(160)
        row_theme = self._create_setting_row(
            "Theme",
            "Select the default graphical theme style presets for the application workspace.",
            self.theme_combo, "theme", "Appearance"
        )
        self.settings_controls["theme"] = self.theme_combo
        c_appearance.add_setting_row(row_theme)
        
        # Accent Color
        self.accent_combo = QComboBox()
        self.accent_combo.addItems(["None (Use Theme Default)", "Blue (#2563eb)", "Green (#22c55e)", "Orange (#f97316)", "Red (#ef4444)"])
        self.accent_combo.setFixedWidth(200)
        row_accent = self._create_setting_row(
            "Accent Color",
            "Override primary theme button colors. Live previews are displayed instantly.",
            self.accent_combo, "accent", "Appearance"
        )
        self.settings_controls["accent_color"] = self.accent_combo
        c_appearance.add_setting_row(row_accent)
        
        # Font Size
        self.font_combo = QComboBox()
        self.font_combo.addItems(["12px", "13px", "14px", "15px", "16px"])
        self.font_combo.setFixedWidth(100)
        row_font = self._create_setting_row(
            "Font Size",
            "Adjust scale typography sizing rules globally for client text layouts.",
            self.font_combo, "font_size", "Appearance"
        )
        self.settings_controls["font_size"] = self.font_combo
        c_appearance.add_setting_row(row_font)
        
        l2.addWidget(c_appearance)
        
        # UI Elements Card
        c_ui_el = SettingsCard("UI Configuration", "🎨")
        self.all_group_boxes.append(c_ui_el)
        
        self.sw_animations = ModernSwitch()
        row_anim = self._create_setting_row(
            "Animations",
            "Enable smooth visual transitions, hover highlights, and pulsed progress indicator animations.",
            self.sw_animations, "animations", "Appearance"
        )
        self.settings_controls["animations"] = self.sw_animations
        c_ui_el.add_setting_row(row_anim)
        
        self.sw_compact = ModernSwitch()
        row_comp = self._create_setting_row(
            "Compact Mode",
            "Reduces padding, spacing heights, and margins in Torrent tables for power-user screens.",
            self.sw_compact, "compact", "Appearance"
        )
        self.settings_controls["compact_mode"] = self.sw_compact
        c_ui_el.add_setting_row(row_comp)
        
        # UI Scale
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["100%", "110%", "120%", "125%", "150%"])
        self.scale_combo.setFixedWidth(100)
        row_scale = self._create_setting_row(
            "UI Scale",
            "Scale the entire application pixel layout bounds to support high-DPI screens.",
            self.scale_combo, "font_size", "Appearance"
        )
        self.settings_controls["ui_scale"] = self.scale_combo
        c_ui_el.add_setting_row(row_scale)
        
        # Corner Radius
        self.radius_combo = QComboBox()
        self.radius_combo.addItems(["4px", "8px", "12px", "16px", "999px"])
        self.radius_combo.setFixedWidth(100)
        row_radius = self._create_setting_row(
            "Corner Radius",
            "Adjust the rounding attributes of layouts, container panels, and hover indicators.",
            self.radius_combo, "compact", "Appearance"
        )
        self.settings_controls["corner_radius"] = self.radius_combo
        c_ui_el.add_setting_row(row_radius)
        
        l2.addWidget(c_ui_el)
        l2.addStretch()
        self.stack.addWidget(p2)
        
        # ── Page 3: Network ──
        p3 = QWidget()
        l3 = QVBoxLayout(p3)
        l3.setContentsMargins(0, 0, 10, 0)
        l3.setSpacing(vertical_spacing)
        
        # 23. Network Page
        c_ports = SettingsCard("Connection Ports", "🌐")
        self.all_group_boxes.append(c_ports)
        
        self.txt_port = QLineEdit("6881")
        self.txt_port.setFixedWidth(100)
        self.txt_port.setStyleSheet("background-color: #0f1220; border: 1px solid #1e2438; border-radius: 6px; padding: 4px; color: #ffffff;")
        row_port = self._create_setting_row(
            "Listening Port",
            "Specify the listener incoming TCP port Vortex uses to handshake with peers.",
            self.txt_port, "port", "Network"
        )
        self.settings_controls["listening_port"] = self.txt_port
        c_ports.add_setting_row(row_port)
        
        self.sw_upnp = ModernSwitch()
        row_upnp = self._create_setting_row(
            "UPnP Mapping",
            "Enable Universal Plug and Play automatic port-forwarding mappings in your residential router.",
            self.sw_upnp, "upnp", "Network"
        )
        self.settings_controls["upnp"] = self.sw_upnp
        c_ports.add_setting_row(row_upnp)
        
        self.sw_nat_pmp = ModernSwitch()
        row_nat = self._create_setting_row(
            "NAT-PMP mapping",
            "Use NAT Port Mapping Protocol to dynamically authorize incoming peer socket streams.",
            self.sw_nat_pmp, "upnp", "Network"
        )
        self.settings_controls["nat_pmp"] = self.sw_nat_pmp
        c_ports.add_setting_row(row_nat)
        
        # Encryption
        self.encryption_combo = QComboBox()
        self.encryption_combo.addItems(["Prefer Encryption", "Force Encryption", "Disable Encryption"])
        self.encryption_combo.setFixedWidth(160)
        row_enc = self._create_setting_row(
            "Encryption Level",
            "Choose default policy enforcement level for stream protocol security.",
            self.encryption_combo, "encryption", "Network"
        )
        self.settings_controls["encryption"] = self.encryption_combo
        c_ports.add_setting_row(row_enc)
        
        self.sw_dht = ModernSwitch()
        row_dht = self._create_setting_row(
            "DHT Network",
            "Enable Distributed Hash Table trackerless peer routing systems.",
            self.sw_dht, "dht", "Network"
        )
        self.settings_controls["dht"] = self.sw_dht
        c_ports.add_setting_row(row_dht)
        
        self.sw_pex = ModernSwitch()
        row_pex = self._create_setting_row(
            "Peer Exchange (PEX)",
            "Allows local peer lists to be exchanged directly among neighboring nodes.",
            self.sw_pex, "dht", "Network"
        )
        self.settings_controls["pex"] = self.sw_pex
        c_ports.add_setting_row(row_pex)
        
        self.sw_lsd = ModernSwitch()
        row_lsd = self._create_setting_row(
            "Local Service Discovery (LSD)",
            "Scans multicast routes to identify potential high-speed download seeds on local intranet nodes.",
            self.sw_lsd, "dht", "Network"
        )
        self.settings_controls["lsd"] = self.sw_lsd
        c_ports.add_setting_row(row_lsd)
        
        l3.addWidget(c_ports)
        
        # Bandwidth Limits Card
        c_bandwidth = SettingsCard("Bandwidth Limits", "🌐")
        self.all_group_boxes.append(c_bandwidth)
        
        self.txt_dl_limit = QLineEdit("Unlimited")
        self.txt_dl_limit.setFixedWidth(120)
        self.txt_dl_limit.setStyleSheet("background-color: #0f1220; border: 1px solid #1e2438; border-radius: 6px; padding: 4px; color: #ffffff;")
        row_dl_lim = self._create_setting_row(
            "Global Download limit (KB/s)",
            "Throttle maximum total client incoming download transfer speed.",
            self.txt_dl_limit, "font_size", "Network"
        )
        self.settings_controls["download_limit"] = self.txt_dl_limit
        c_bandwidth.add_setting_row(row_dl_lim)
        
        self.txt_ul_limit = QLineEdit("Unlimited")
        self.txt_ul_limit.setFixedWidth(120)
        self.txt_ul_limit.setStyleSheet("background-color: #0f1220; border: 1px solid #1e2438; border-radius: 6px; padding: 4px; color: #ffffff;")
        row_ul_lim = self._create_setting_row(
            "Global Upload limit (KB/s)",
            "Throttle maximum total client outgoing upload transfer speed.",
            self.txt_ul_limit, "font_size", "Network"
        )
        self.settings_controls["upload_limit"] = self.txt_ul_limit
        c_bandwidth.add_setting_row(row_ul_lim)
        
        l3.addWidget(c_bandwidth)
        l3.addStretch()
        self.stack.addWidget(p3)
        
        # ── Page 4: Advanced (Tabbed view) ──
        # 20. Advanced Page split into tabs
        p4 = QWidget()
        l4 = QVBoxLayout(p4)
        l4.setContentsMargins(0, 0, 10, 0)
        l4.setSpacing(12)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #1e2438;
                background-color: #141828;
                border-radius: 12px;
                padding: 10px;
            }
            QTabBar::tab {
                background: #0f1220;
                color: #8892a8;
                border: 1px solid #1e2438;
                padding: 10px 16px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: #141828;
                color: #ffffff;
                border-bottom-color: #141828;
                border-top: 2px solid #2563eb;
            }
            QTabBar::tab:hover {
                background: rgba(255, 255, 255, 0.04);
                color: #ffffff;
            }
        """)
        
        # Sub-tab: BitTorrent
        tab_bt = QWidget()
        tbl_bt = QVBoxLayout(tab_bt)
        tbl_bt.setSpacing(16)
        self.sw_dht_rate = ModernSwitch()
        row_dht_rate = self._create_setting_row(
            "Enable DHT Rate Limit",
            "Throttles incoming discovery packets to optimize CPU pipeline overhead.",
            self.sw_dht_rate, "dht", "Advanced"
        )
        self.settings_controls["dht_rate_limit"] = self.sw_dht_rate
        tbl_bt.addWidget(row_dht_rate)
        
        self.sw_pex_adv = ModernSwitch()
        row_pex_adv = self._create_setting_row(
            "Enable Peer exchange",
            "Direct peer-to-peer neighborhood table list lookup.",
            self.sw_pex_adv, "dht", "Advanced"
        )
        self.settings_controls["peer_exchange"] = self.sw_pex_adv
        tbl_bt.addWidget(row_pex_adv)
        tbl_bt.addStretch()
        
        # Sub-tab: Connections
        tab_conn = QWidget()
        tbl_conn = QVBoxLayout(tab_conn)
        tbl_conn.setSpacing(16)
        
        self.txt_max_conn_torrent = QLineEdit("50")
        self.txt_max_conn_torrent.setFixedWidth(80)
        self.txt_max_conn_torrent.setStyleSheet("background-color: #0f1220; border: 1px solid #1e2438; border-radius: 6px; padding: 4px; color: #ffffff;")
        row_max_ct = self._create_setting_row(
            "Max Connections per Torrent",
            "Hard connection caps enforced per distinct swarm slot.",
            self.txt_max_conn_torrent, "font_size", "Advanced"
        )
        self.settings_controls["max_conn_torrent"] = self.txt_max_conn_torrent
        tbl_conn.addWidget(row_max_ct)
        
        self.txt_max_conn_global = QLineEdit("200")
        self.txt_max_conn_global.setFixedWidth(80)
        self.txt_max_conn_global.setStyleSheet(self.txt_max_conn_torrent.styleSheet())
        row_max_cg = self._create_setting_row(
            "Max Global Connections",
            "Limits maximum combined sockets open concurrently on the server process.",
            self.txt_max_conn_global, "font_size", "Advanced"
        )
        self.settings_controls["max_conn_global"] = self.txt_max_conn_global
        tbl_conn.addWidget(row_max_cg)
        tbl_conn.addStretch()
        
        # Sub-tab: Cache
        tab_cache = QWidget()
        tbl_cache = QVBoxLayout(tab_cache)
        tbl_cache.setSpacing(16)
        
        self.txt_disk_cache = QLineEdit("64")
        self.txt_disk_cache.setFixedWidth(80)
        self.txt_disk_cache.setStyleSheet(self.txt_max_conn_torrent.styleSheet())
        row_cache = self._create_setting_row(
            "Disk Cache Size (MB)",
            "Main memory allocation threshold for queuing write chunks prior to commit IO.",
            self.txt_disk_cache, "disk_space", "Advanced"
        )
        self.settings_controls["disk_cache_size"] = self.txt_disk_cache
        tbl_cache.addWidget(row_cache)
        
        self.sw_cache_wb = ModernSwitch()
        row_wb = self._create_setting_row(
            "Enable Cache Write-back",
            "Buffer incoming pieces in RAM buffer before flushing in sorted sectors.",
            self.sw_cache_wb, "disk_space", "Advanced"
        )
        self.settings_controls["cache_writeback"] = self.sw_cache_wb
        tbl_cache.addWidget(row_wb)
        tbl_cache.addStretch()
        
        # Sub-tab: Performance
        tab_perf = QWidget()
        tbl_perf = QVBoxLayout(tab_perf)
        tbl_perf.setSpacing(16)
        
        self.sw_workers = ModernSwitch()
        row_workers = self._create_setting_row(
            "Enable multithreaded piece verifiers",
            "Leverages modern CPU hardware architecture core verification loops.",
            self.sw_workers, "animations", "Advanced"
        )
        self.settings_controls["multithread_verify"] = self.sw_workers
        tbl_perf.addWidget(row_workers)
        
        self.thread_pool_combo = QComboBox()
        self.thread_pool_combo.addItems(["Auto", "2", "4", "8", "16"])
        self.thread_pool_combo.setFixedWidth(100)
        row_tp = self._create_setting_row(
            "Thread pool size",
            "Customize active execution thread counts dedicated to integrity verification.",
            self.thread_pool_combo, "animations", "Advanced"
        )
        self.settings_controls["thread_pool_size"] = self.thread_pool_combo
        tbl_perf.addWidget(row_tp)
        tbl_perf.addStretch()
        
        # Sub-tab: Security
        tab_sec = QWidget()
        tbl_sec = QVBoxLayout(tab_sec)
        tbl_sec.setSpacing(16)
        
        self.sw_secure_scratch = ModernSwitch()
        row_scratch = self._create_setting_row(
            "Use secure scratch directory",
            "Encrypt intermediate buffer sectors dynamically while pieces assemble.",
            self.sw_secure_scratch, "encryption", "Advanced"
        )
        self.settings_controls["secure_scratch"] = self.sw_secure_scratch
        tbl_sec.addWidget(row_scratch)
        
        self.sw_validate_ssl = ModernSwitch()
        row_ssl = self._create_setting_row(
            "Validate SSL certificates",
            "Perform cryptographic verification on SSL handshake streams.",
            self.sw_validate_ssl, "encryption", "Advanced"
        )
        self.settings_controls["validate_ssl"] = self.sw_validate_ssl
        tbl_sec.addWidget(row_ssl)
        tbl_sec.addStretch()
        
        # Sub-tab: Experimental
        tab_exp = QWidget()
        tbl_exp = QVBoxLayout(tab_exp)
        tbl_exp.setSpacing(16)
        
        self.sw_webui = ModernSwitch()
        row_webui = self._create_setting_row(
            "Enable WebUI v2",
            "Test experimental new material design dashboard for web connections.",
            self.sw_webui, "animations", "Advanced"
        )
        self.settings_controls["webui_v2"] = self.sw_webui
        tbl_exp.addWidget(row_webui)
        
        self.sw_experimental_disc = ModernSwitch()
        row_disc = self._create_setting_row(
            "Experimental peer discovery",
            "Heuristic discovery routines testing local intranet nodes.",
            self.sw_experimental_disc, "dht", "Advanced"
        )
        self.settings_controls["experimental_discovery"] = self.sw_experimental_disc
        tbl_exp.addWidget(row_disc)
        tbl_exp.addStretch()
        
        # Add all tabs to the list to track references
        self.tab_widget_list.append((self.tab_widget, [
            (tab_bt, "BitTorrent"),
            (tab_conn, "Connections"),
            (tab_cache, "Cache"),
            (tab_perf, "Performance"),
            (tab_sec, "Security"),
            (tab_exp, "Experimental")
        ]))
        
        # Load sub-tabs into QTabWidget
        for tab, title in self.tab_widget_list[0][1]:
            self.tab_widget.addTab(tab, title)
            
        # Advanced page wrapper
        card_adv = SettingsCard("Advanced Configurations", "🔧")
        self.all_group_boxes.append(card_adv)
        card_adv.layout.addWidget(self.tab_widget)
        
        # Add Custom QSS Rule textedit at the bottom of Advanced Page
        css_container = QWidget()
        css_layout = QVBoxLayout(css_container)
        css_layout.setContentsMargins(0, 0, 0, 0)
        self.txt_custom_css = QTextEdit()
        self.txt_custom_css.setPlaceholderText("/* Override client QSS stylesheet properties directly */")
        self.txt_custom_css.setStyleSheet("""
            background-color: #0f1220; 
            border: 1px solid #1e2438; 
            border-radius: 8px; 
            color: #3b82f6; 
            font-family: monospace; 
            font-size: 13px; 
            min-height: 100px;
        """)
        css_layout.addWidget(self.txt_custom_css)
        row_qss = self._create_setting_row(
            "Custom QSS Stylesheet Override",
            "Inject raw Qt style code overrides directly into the active render buffer.",
            css_container, "theme", "Advanced"
        )
        self.settings_controls["custom_qss"] = self.txt_custom_css
        card_adv.add_setting_row(row_qss)
        
        l4.addWidget(card_adv)
        l4.addStretch()
        self.stack.addWidget(p4)
