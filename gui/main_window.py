import os
import time
import datetime
import random
import math
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QProgressBar,
    QFileDialog, QSplitter, QLabel, QHeaderView,
    QAbstractItemView, QPushButton, QMessageBox,
    QMenu, QDialog, QLineEdit, QTextEdit, QTreeWidgetItem,
    QStackedWidget, QRadioButton, QButtonGroup, QFrame,
    QScrollArea, QGridLayout, QGraphicsDropShadowEffect, QCheckBox
)
from PyQt6.QtCore import QTimer, Qt, QObject, pyqtSignal, QSize, QRect, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF
from PyQt6.QtGui import (
    QAction, QIcon, QPixmap, QDragEnterEvent, QDropEvent,
    QShortcut, QKeySequence, QPainter, QColor, QRadialGradient,
    QLinearGradient
)

from gui.sidebar import Sidebar
from gui.stats_bar import StatsBar
from gui.detail_panel import DetailPanel
from gui.theme import get_theme_qss
from gui.statistics_view import StatisticsView
from gui.settings_view import SettingsView
from gui.about_dialog import AboutDialog
from gui.command_palette import CommandPalette
from torrent_manager import TorrentManager


class SegmentedControl(QFrame):
    toggled = pyqtSignal(int)

    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setObjectName("segmentedControl")
        self.setStyleSheet("""
            #segmentedControl {
                background-color: #141824;
                border: 1px solid #1e2438;
                border-radius: 8px;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                color: #8892a8;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #1c2136;
            }
            QPushButton:checked {
                color: #ffffff;
                background-color: #2563eb;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        self.buttons = []
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        
        for i, text in enumerate(items):
            btn = QPushButton(text)
            btn.setCheckable(True)
            if i == 0:
                btn.setChecked(True)
            self.group.addButton(btn, i)
            layout.addWidget(btn)
            self.buttons.append(btn)
            
        self.group.idClicked.connect(self.toggled.emit)
        
    def select_index(self, index):
        if 0 <= index < len(self.buttons):
            self.buttons[index].setChecked(True)
            self.toggled.emit(index)


class ChoiceCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, icon_char, title, subtext, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                background-color: #141824;
                border: 1px solid #20263d;
                border-radius: 12px;
            }
            QFrame:hover {
                background-color: #1c2136;
                border-color: #2563eb;
            }
            QLabel {
                background-color: transparent;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_icon = QLabel(icon_char)
        lbl_icon.setStyleSheet("font-size: 36px;")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_sub = QLabel(subtext)
        lbl_sub.setStyleSheet("font-size: 12px; color: #8892a8;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setWordWrap(True)
        
        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class DropZone(QFrame):
    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #20263d;
                border-radius: 12px;
                background-color: #0e111a;
            }
            QFrame#dragActive {
                border-color: #2563eb;
                background-color: rgba(37, 99, 235, 0.08);
            }
            QLabel {
                background-color: transparent;
                color: #8892a8;
                font-size: 13px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_text = QLabel("📥 Drag & Drop .torrent file here or Browse")
        layout.addWidget(self.lbl_text)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith(".torrent"):
                    self.setObjectName("dragActive")
                    self.setStyle(self.style())
                    event.acceptProposedAction()
                    return
        event.ignore()
        
    def dragLeaveEvent(self, event):
        self.setObjectName("")
        self.setStyle(self.style())
        
    def dropEvent(self, event):
        self.setObjectName("")
        self.setStyle(self.style())
        for url in event.mimeData().urls():
            fp = url.toLocalFile()
            if fp.endswith(".torrent"):
                self.file_dropped.emit(fp)
                event.acceptProposedAction()
                return


class FileSelectorCard(QFrame):
    browse_clicked = pyqtSignal()
    change_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #141824;
                border: 1px solid #1e2438;
                border-radius: 10px;
            }
            QLabel {
                background-color: transparent;
            }
        """)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        
        self.stack = QStackedWidget(self)
        self.layout.addWidget(self.stack)
        
        self.page_empty = QWidget()
        pe_layout = QHBoxLayout(self.page_empty)
        pe_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_empty = QLabel("No torrent selected")
        self.lbl_empty.setStyleSheet("color: #8892a8; font-size: 13px;")
        
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #1e2438;
                border: 1px solid #2d3650;
                border-radius: 6px;
                color: #ffffff;
                font-weight: bold;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2d3650;
            }
        """)
        self.btn_browse.clicked.connect(self.browse_clicked.emit)
        pe_layout.addWidget(self.lbl_empty)
        pe_layout.addStretch()
        pe_layout.addWidget(self.btn_browse)
        self.stack.addWidget(self.page_empty)
        
        self.page_selected = QWidget()
        ps_layout = QHBoxLayout(self.page_selected)
        ps_layout.setContentsMargins(0, 0, 0, 0)
        
        vbox = QVBoxLayout()
        vbox.setSpacing(2)
        self.lbl_filename = QLabel("ubuntu.torrent")
        self.lbl_filename.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 13px;")
        self.lbl_filesize = QLabel("3.2 KB")
        self.lbl_filesize.setStyleSheet("color: #8892a8; font-size: 11px;")
        vbox.addWidget(self.lbl_filename)
        vbox.addWidget(self.lbl_filesize)
        
        self.btn_change = QPushButton("Change")
        self.btn_change.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #2d3650;
                border-radius: 6px;
                color: #c8d0e0;
                font-weight: bold;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1e2438;
                color: #ffffff;
            }
        """)
        self.btn_change.clicked.connect(self.change_clicked.emit)
        
        ps_layout.addLayout(vbox)
        ps_layout.addStretch()
        ps_layout.addWidget(self.btn_change)
        self.stack.addWidget(self.page_selected)
        
    def set_file(self, filename, size_str):
        if filename:
            self.lbl_filename.setText(filename)
            self.lbl_filesize.setText(size_str)
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)


class AddTorrentDialog(QDialog):
    def __init__(self, parent=None, default_save_dir="."):
        super().__init__(parent)
        self.setWindowTitle("Add Torrent")
        self.resize(680, 480)
        self.setAcceptDrops(True)
        self._is_valid_magnet = False
        self._has_enough_space = True
        
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0e14;
                border: 1px solid #1e2438;
            }
            QLabel {
                color: #c8d0e0;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #141824;
                border: 1px solid #2c3247;
                border-radius: 8px;
                padding: 8px 12px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:hover {
                border-color: #4169e1;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
            QCheckBox {
                color: #c8d0e0;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #2c3247;
                border-radius: 4px;
                background-color: #141824;
            }
            QCheckBox::indicator:hover {
                border-color: #4169e1;
            }
            QCheckBox::indicator:checked {
                background-color: #2563eb;
                border-color: #2563eb;
            }
        """)
        
        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(150)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
            
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_stack = QStackedWidget(self)
        main_layout.addWidget(self.main_stack)
        
        # PAGE 0: CHOICE SCREEN
        self.page_choice = QWidget()
        pc_layout = QVBoxLayout(self.page_choice)
        pc_layout.setContentsMargins(30, 30, 30, 30)
        pc_layout.setSpacing(20)
        
        ch_vbox = QVBoxLayout()
        ch_vbox.setSpacing(4)
        lbl_c_title = QLabel("📥 Add Torrent")
        lbl_c_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff;")
        lbl_c_subtitle = QLabel("Add a .torrent file or paste a magnet link to start downloading.")
        lbl_c_subtitle.setStyleSheet("font-size: 13px; color: #8892a8;")
        ch_vbox.addWidget(lbl_c_title)
        ch_vbox.addWidget(lbl_c_subtitle)
        pc_layout.addLayout(ch_vbox)
        
        cards_hbox = QHBoxLayout()
        cards_hbox.setSpacing(20)
        
        self.card_file = ChoiceCard("📄", "Open Torrent File", "Browse for a local .torrent file")
        self.card_magnet = ChoiceCard("🧲", "Use Magnet Link", "Paste a magnet link directly")
        self.card_file.clicked.connect(self._choose_file_mode)
        self.card_magnet.clicked.connect(self._choose_magnet_mode)
        
        cards_hbox.addWidget(self.card_file)
        cards_hbox.addWidget(self.card_magnet)
        pc_layout.addLayout(cards_hbox)
        
        self.choice_drop = DropZone()
        self.choice_drop.file_dropped.connect(self._load_torrent_file)
        pc_layout.addWidget(self.choice_drop)
        
        cf_layout = QHBoxLayout()
        btn_c_cancel = QPushButton("Cancel")
        btn_c_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #2d3650;
                border-radius: 8px;
                color: #ffffff;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1e2438;
            }
        """)
        btn_c_cancel.clicked.connect(self.reject)
        cf_layout.addStretch()
        cf_layout.addWidget(btn_c_cancel)
        pc_layout.addLayout(cf_layout)
        
        self.main_stack.addWidget(self.page_choice)
        
        # PAGE 1: FORM SCREEN
        self.page_form = QWidget()
        pf_layout = QVBoxLayout(self.page_form)
        pf_layout.setContentsMargins(30, 24, 30, 24)
        pf_layout.setSpacing(14)
        
        fh_vbox = QVBoxLayout()
        fh_vbox.setSpacing(4)
        lbl_f_title = QLabel("📥 Add Torrent")
        lbl_f_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff;")
        self.lbl_f_subtitle = QLabel("Add a .torrent file or paste a magnet link to start downloading.")
        self.lbl_f_subtitle.setStyleSheet("font-size: 13px; color: #8892a8;")
        fh_vbox.addWidget(lbl_f_title)
        fh_vbox.addWidget(self.lbl_f_subtitle)
        pf_layout.addLayout(fh_vbox)
        
        self.segmented_control = SegmentedControl(["📄 Torrent File", "🧲 Magnet Link"])
        self.segmented_control.toggled.connect(self._segmented_toggled)
        pf_layout.addWidget(self.segmented_control)
        
        self.radio_file = QRadioButton()
        self.radio_magnet = QRadioButton()
        self.radio_file.setChecked(True)
        
        self.stack_source = QStackedWidget()
        
        self.src_file_page = QWidget()
        sfp_layout = QVBoxLayout(self.src_file_page)
        sfp_layout.setContentsMargins(0, 0, 0, 0)
        sfp_layout.setSpacing(10)
        
        self.file_selector = FileSelectorCard()
        self.file_selector.browse_clicked.connect(self._browse_source)
        self.file_selector.change_clicked.connect(self._browse_source)
        sfp_layout.addWidget(self.file_selector)
        
        self.info_group = QFrame()
        self.info_group.setVisible(False)
        self.info_group.setStyleSheet("""
            QFrame {
                background-color: #0e111a;
                border: 1px solid #1c2136;
                border-radius: 10px;
            }
            QLabel {
                font-size: 12px;
                color: #c8d0e0;
            }
        """)
        info_layout = QGridLayout(self.info_group)
        info_layout.setContentsMargins(12, 12, 12, 12)
        info_layout.setSpacing(6)
        
        self.lbl_info_name = QLabel("Name: —")
        self.lbl_info_size = QLabel("Size: —")
        self.lbl_info_pieces = QLabel("Pieces: —")
        self.lbl_info_files = QLabel("Files: —")
        self.lbl_info_created_by = QLabel("Created By: —")
        
        info_layout.addWidget(self.lbl_info_name, 0, 0, 1, 2)
        info_layout.addWidget(self.lbl_info_size, 1, 0)
        info_layout.addWidget(self.lbl_info_pieces, 1, 1)
        info_layout.addWidget(self.lbl_info_files, 2, 0)
        info_layout.addWidget(self.lbl_info_created_by, 2, 1)
        
        sfp_layout.addWidget(self.info_group)
        self.stack_source.addWidget(self.src_file_page)
        
        self.src_magnet_page = QWidget()
        smp_layout = QVBoxLayout(self.src_magnet_page)
        smp_layout.setContentsMargins(0, 0, 0, 0)
        smp_layout.setSpacing(6)
        
        self.txt_source = QLineEdit()
        self.txt_source.setPlaceholderText("Paste magnet link here...")
        self.txt_source.setStyleSheet("""
            QLineEdit {
                background-color: #141824;
                border: 2px solid #20263d;
                border-radius: 12px;
                padding: 12px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:hover {
                border-color: #4169e1;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        self.txt_source.textChanged.connect(self._source_text_changed)
        
        self.lbl_magnet_validation = QLabel("")
        self.lbl_magnet_validation.setStyleSheet("font-size: 11px;")
        
        smp_layout.addWidget(self.txt_source)
        smp_layout.addWidget(self.lbl_magnet_validation)
        
        self.stack_source.addWidget(self.src_magnet_page)
        
        pf_layout.addWidget(self.stack_source)
        
        dest_vbox = QVBoxLayout()
        dest_vbox.setSpacing(6)
        lbl_dest_label = QLabel("📁 Destination")
        lbl_dest_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        dest_vbox.addWidget(lbl_dest_label)
        
        self.dest_card = QFrame()
        self.dest_card.setStyleSheet("""
            QFrame {
                background-color: #141824;
                border: 1px solid #1e2438;
                border-radius: 10px;
            }
        """)
        dest_card_layout = QHBoxLayout(self.dest_card)
        dest_card_layout.setContentsMargins(12, 12, 12, 12)
        
        dest_details = QVBoxLayout()
        dest_details.setSpacing(2)
        self.lbl_dest_folder_title = QLabel("📁 Downloads")
        self.lbl_dest_folder_title.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 13px; background: transparent;")
        self.lbl_dest_path = QLabel("/home/jarjis/Downloads")
        self.lbl_dest_path.setStyleSheet("color: #8892a8; font-size: 11px; background: transparent;")
        dest_details.addWidget(self.lbl_dest_folder_title)
        dest_details.addWidget(self.lbl_dest_path)
        dest_card_layout.addLayout(dest_details)
        dest_card_layout.addStretch()
        
        self.btn_browse_dest = QPushButton("Browse...")
        self.btn_browse_dest.setStyleSheet("""
            QPushButton {
                background-color: #1e2438;
                border: 1px solid #2d3650;
                border-radius: 6px;
                color: #ffffff;
                font-weight: bold;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2d3650;
            }
        """)
        self.btn_browse_dest.clicked.connect(self._browse_dest)
        dest_card_layout.addWidget(self.btn_browse_dest)
        dest_vbox.addWidget(self.dest_card)
        
        self.recent_layout = QHBoxLayout()
        self.recent_layout.setSpacing(6)
        self.recent_layout.setContentsMargins(2, 0, 0, 0)
        lbl_recent_tag = QLabel("Recent:")
        lbl_recent_tag.setStyleSheet("color: #6b7590; font-size: 11px; font-weight: bold;")
        self.recent_layout.addWidget(lbl_recent_tag)
        
        recent_paths = {
            "Downloads": os.path.expanduser("~/Downloads"),
            "Movies": os.path.expanduser("~/Videos") if os.path.exists(os.path.expanduser("~/Videos")) else os.path.expanduser("~/Downloads/Movies"),
            "ISOs": os.path.expanduser("~/Downloads/ISOs") if os.path.exists(os.path.expanduser("~/Downloads/ISOs")) else os.path.expanduser("~/Downloads"),
            "Documents": os.path.expanduser("~/Documents")
        }
        for name, path in recent_paths.items():
            btn = QPushButton(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #161a2e;
                    border: 1px solid #20263d;
                    border-radius: 6px;
                    color: #8892a8;
                    padding: 3px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                    border-color: #2563eb;
                    color: #ffffff;
                }
            """)
            btn.clicked.connect(lambda checked, p=path, n=name: self._set_destination_path(p, n))
            self.recent_layout.addWidget(btn)
        self.recent_layout.addStretch()
        dest_vbox.addLayout(self.recent_layout)
        
        pf_layout.addLayout(dest_vbox)
        
        self.lbl_space_status = QLabel("")
        pf_layout.addWidget(self.lbl_space_status)
        
        self.btn_toggle_advanced = QPushButton("▶ Advanced Options")
        self.btn_toggle_advanced.setCheckable(True)
        self.btn_toggle_advanced.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_advanced.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #8892a8;
                font-weight: bold;
                font-size: 12px;
                text-align: left;
                padding: 4px 0px;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        self.btn_toggle_advanced.clicked.connect(self._toggle_advanced)
        pf_layout.addWidget(self.btn_toggle_advanced)
        
        self.advanced_container = QWidget()
        self.advanced_container.setVisible(False)
        adv_layout = QVBoxLayout(self.advanced_container)
        adv_layout.setContentsMargins(0, 0, 0, 0)
        adv_layout.setSpacing(8)
        
        self.chk_sequential = QCheckBox("Download sequentially")
        self.chk_skip_hash = QCheckBox("Skip hash check")
        
        adv_grid = QGridLayout()
        adv_grid.setSpacing(8)
        self.txt_bw_limit = QLineEdit()
        self.txt_bw_limit.setPlaceholderText("No Limit")
        self.txt_bw_limit.setStyleSheet("padding: 6px;")
        self.txt_bw_limit.setFixedWidth(100)
        
        max_conn_default = "200"
        if parent and hasattr(parent, "page_settings") and hasattr(parent.page_settings, "saved_settings"):
            max_conn_default = parent.page_settings.saved_settings.get("max_conn_torrent", "200")
        self.txt_max_conn = QLineEdit(max_conn_default)
        self.txt_max_conn.setStyleSheet("padding: 6px;")
        self.txt_max_conn.setFixedWidth(100)
        
        adv_grid.addWidget(QLabel("Bandwidth limit (KB/s):"), 0, 0)
        adv_grid.addWidget(self.txt_bw_limit, 0, 1)
        adv_grid.addWidget(QLabel("Maximum connections:"), 1, 0)
        adv_grid.addWidget(self.txt_max_conn, 1, 1)
        
        adv_layout.addWidget(self.chk_sequential)
        adv_layout.addWidget(self.chk_skip_hash)
        adv_layout.addLayout(adv_grid)
        pf_layout.addWidget(self.advanced_container)
        
        ff_layout = QHBoxLayout()
        self.lbl_footer_info = QLabel("Downloaded files will be stored in <b>Downloads</b>")
        self.lbl_footer_info.setStyleSheet("color: #6b7590; font-size: 11px;")
        
        btn_f_cancel = QPushButton("Cancel")
        btn_f_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #2d3650;
                border-radius: 8px;
                color: #ffffff;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1e2438;
            }
        """)
        btn_f_cancel.clicked.connect(self.reject)
        
        self.btn_download = QPushButton("Start Download")
        self.btn_download.clicked.connect(self.accept)
        
        ff_layout.addWidget(self.lbl_footer_info)
        ff_layout.addStretch()
        ff_layout.addWidget(btn_f_cancel)
        ff_layout.addWidget(self.btn_download)
        pf_layout.addLayout(ff_layout)
        
        self.main_stack.addWidget(self.page_form)
        
        self.txt_dest = QLineEdit(default_save_dir)
        self.txt_dest.setVisible(False)
        self._set_destination_path(default_save_dir)
        
        self.main_stack.setCurrentIndex(0)
        self._update_download_button_state()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith(".torrent"):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            fp = url.toLocalFile()
            if fp.endswith(".torrent"):
                self._load_torrent_file(fp)
                event.acceptProposedAction()
                return

    def exec(self):
        is_magnet = self.radio_magnet.isChecked()
        if is_magnet or self.txt_source.text().strip():
            self.main_stack.setCurrentIndex(1)
            if is_magnet:
                self.segmented_control.select_index(1)
        return super().exec()

    def _choose_file_mode(self):
        self.radio_file.setChecked(True)
        self.segmented_control.select_index(0)
        self.main_stack.setCurrentIndex(1)
        self._source_changed()

    def _choose_magnet_mode(self):
        self.radio_magnet.setChecked(True)
        self.segmented_control.select_index(1)
        self.main_stack.setCurrentIndex(1)
        self._source_changed()

    def _segmented_toggled(self, index):
        if index == 0:
            self.radio_file.setChecked(True)
        else:
            self.radio_magnet.setChecked(True)
        self._source_changed()

    def _source_changed(self):
        is_magnet = self.radio_magnet.isChecked()
        self.stack_source.setCurrentIndex(1 if is_magnet else 0)
        self.lbl_f_subtitle.setText("Paste a magnet link to start downloading." if is_magnet else "Add a .torrent file to start downloading.")
        self._update_download_button_state()

    def _source_text_changed(self, text):
        if self.radio_magnet.isChecked():
            self._validate_magnet(text)
        else:
            self._update_download_button_state()

    def _validate_magnet(self, text):
        text = text.strip()
        if not text:
            self.lbl_magnet_validation.setText("")
            self._is_valid_magnet = False
        elif text.startswith("magnet:?xt=urn:btih:"):
            self.lbl_magnet_validation.setText("✓ Valid Magnet Link")
            self.lbl_magnet_validation.setStyleSheet("color: #22c55e; font-weight: bold; font-size: 11px;")
            self._is_valid_magnet = True
        else:
            self.lbl_magnet_validation.setText("❌ Invalid Magnet Link")
            self.lbl_magnet_validation.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 11px;")
            self._is_valid_magnet = False
        self._update_download_button_state()

    def _browse_source(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Open Torrent File", "", "Torrent Files (*.torrent)")
        if fp:
            self._load_torrent_file(fp)

    def _load_torrent_file(self, file_path):
        if not file_path or not os.path.exists(file_path):
            return
        
        self.txt_source.setText(file_path)
        
        try:
            from torrent import Torrent
            t = Torrent(file_path)
            name = t.get_name().decode('utf-8', errors='ignore')
            size = t.get_size()
            pieces = t.get_number_of_pieces()
            files_count = len(t.info[b'files']) if b'files' in t.info else 1
            
            import math
            def format_size(bytes_size):
                if bytes_size == 0: return "0 B"
                size_name = ("B", "KB", "MB", "GB", "TB")
                i = int(math.floor(math.log(bytes_size, 1024)))
                p = math.pow(1024, i)
                s = round(bytes_size / p, 2)
                return f"{s} {size_name[i]}"
                
            formatted_size = format_size(size)
            created_by = t.meta.get(b'created by', b'Unknown').decode('utf-8', errors='ignore')
            
            self.file_selector.set_file(os.path.basename(file_path), formatted_size)
            
            self.lbl_info_name.setText(f"<b>Name:</b> {name}")
            self.lbl_info_size.setText(f"<b>Size:</b> {formatted_size}")
            self.lbl_info_pieces.setText(f"<b>Pieces:</b> {pieces}")
            self.lbl_info_files.setText(f"<b>Files:</b> {files_count}")
            self.lbl_info_created_by.setText(f"<b>Created By:</b> {created_by}")
            self.info_group.setVisible(True)
            
            self._update_disk_space_check(size)
        except Exception as e:
            QMessageBox.warning(self, "Invalid Torrent", f"Failed to parse torrent file: {e}")
            self.file_selector.set_file("", "")
            self.info_group.setVisible(False)
            self.lbl_space_status.setText("")
            self.txt_source.clear()
            
        self.radio_file.setChecked(True)
        self.segmented_control.select_index(0)
        self.stack_source.setCurrentIndex(0)
        self.main_stack.setCurrentIndex(1)
        self._update_download_button_state()

    def _browse_dest(self):
        d = QFileDialog.getExistingDirectory(self, "Select Save Directory", self.txt_dest.text())
        if d:
            self._set_destination_path(d)

    def _set_destination_path(self, path, name=None):
        self.txt_dest.setText(path)
        folder_name = name if name else os.path.basename(path)
        if not folder_name:
            folder_name = path
        self.lbl_dest_folder_title.setText(f"📁 {folder_name}")
        self.lbl_dest_path.setText(path)
        self.lbl_footer_info.setText(f"Downloaded files will be stored in <font color='#ffffff'><b>{folder_name}</b></font>")
        
        torrent_size = None
        torrent_path = self.txt_source.text().strip()
        if torrent_path and os.path.exists(torrent_path) and not self.radio_magnet.isChecked():
            try:
                from torrent import Torrent
                t = Torrent(torrent_path)
                torrent_size = t.get_size()
            except Exception:
                pass
        self._update_disk_space_check(torrent_size)

    def _update_disk_space_check(self, torrent_size=None):
        dest_path = self.txt_dest.text().strip()
        
        import shutil
        def get_free_space(path):
            path = os.path.abspath(path)
            while not os.path.exists(path):
                parent = os.path.dirname(path)
                if parent == path:
                    break
                path = parent
            try:
                total, used, free = shutil.disk_usage(path)
                return free
            except Exception:
                return None
                
        free_space = get_free_space(dest_path)
        if free_space is None:
            self.lbl_space_status.setText("")
            return
            
        import math
        def format_size(bytes_size):
            if bytes_size == 0: return "0 B"
            size_name = ("B", "KB", "MB", "GB", "TB")
            i = int(math.floor(math.log(bytes_size, 1024)))
            p = math.pow(1024, i)
            s = round(bytes_size / p, 2)
            return f"{s} {size_name[i]}"
            
        free_str = format_size(free_space)
        if torrent_size is not None:
            size_str = format_size(torrent_size)
            if free_space >= torrent_size:
                self.lbl_space_status.setText(f"✓ Enough Space (Free: {free_str} | Size: {size_str})")
                self.lbl_space_status.setStyleSheet("color: #22c55e; font-weight: bold; font-size: 11px; background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.2); border-radius: 6px; padding: 6px 12px;")
                self._has_enough_space = True
            else:
                self.lbl_space_status.setText(f"❌ Insufficient Disk Space (Free: {free_str} | Size: {size_str})")
                self.lbl_space_status.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 11px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 6px; padding: 6px 12px;")
                self._has_enough_space = False
        else:
            self.lbl_space_status.setText(f"Free Space: {free_str}")
            self.lbl_space_status.setStyleSheet("color: #8892a8; font-weight: 500; font-size: 11px; background: rgba(136, 146, 168, 0.1); border: 1px solid rgba(136, 146, 168, 0.2); border-radius: 6px; padding: 6px 12px;")
            self._has_enough_space = True

    def _update_download_button_state(self):
        is_magnet = self.radio_magnet.isChecked()
        valid = False
        if is_magnet:
            valid = self._is_valid_magnet
        else:
            file_path = self.txt_source.text().strip()
            valid = bool(file_path and os.path.exists(file_path) and file_path.endswith(".torrent"))
            
        self.btn_download.setEnabled(valid)
        if valid:
            self.btn_download.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                    border: none;
                    border-radius: 8px;
                    color: #ffffff;
                    font-weight: bold;
                    padding: 8px 24px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3b82f6, stop:1 #2563eb);
                }
            """)
        else:
            self.btn_download.setStyleSheet("""
                QPushButton {
                    background-color: #141824;
                    border: 1px solid #1e2438;
                    border-radius: 8px;
                    color: #4a5568;
                    font-weight: bold;
                    padding: 8px 24px;
                    font-size: 13px;
                }
            """)

    def _toggle_advanced(self, checked):
        self.advanced_container.setVisible(checked)
        self.btn_toggle_advanced.setText("▼ Advanced Options" if checked else "▶ Advanced Options")

    def get_data(self):
        is_magnet = self.radio_magnet.isChecked()
        return is_magnet, self.txt_source.text().strip(), self.txt_dest.text().strip()

    def get_advanced_data(self):
        return (
            self.chk_sequential.isChecked(),
            self.chk_skip_hash.isChecked(),
            self.txt_bw_limit.text().strip(),
            self.txt_max_conn.text().strip()
        )


class EmptyStateWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        card = QFrame()
        card.setObjectName("emptyCard")
        card.setStyleSheet("""
            QFrame#emptyCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(20, 24, 40, 0.65), stop:1 rgba(15, 18, 32, 0.85));
                border: 1.5px solid rgba(37, 99, 235, 0.25);
                border-radius: 24px;
                max-width: 520px;
                max-height: 420px;
            }
        """)
        
        clayout = QVBoxLayout(card)
        clayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clayout.setSpacing(20)
        clayout.setContentsMargins(35, 35, 35, 35)
        
        icon = QLabel("🌀")
        icon.setStyleSheet("font-size: 80px; background: transparent; border: none;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clayout.addWidget(icon)
        
        title = QLabel("Vortex Downloader")
        title.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold; background: transparent; border: none; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clayout.addWidget(title)
        
        text = QLabel("Drop torrent files anywhere, paste a magnet link,\nor click below to start downloading.")
        text.setStyleSheet("color: #8892a8; font-size: 14px; background: transparent; border: none; line-height: 20px;")
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clayout.addWidget(text)
        
        bl = QHBoxLayout()
        bl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bl.setSpacing(12)
        
        self.btn_file = QPushButton("  Browse Torrent")
        self.btn_file.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_file.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: bold;
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
            }
        """)
        
        self.btn_magnet = QPushButton("  Paste Magnet Link")
        self.btn_magnet.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_magnet.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1e2438;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: bold;
                color: #c8d0e0;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.04);
                border-color: #2563eb;
                color: #ffffff;
            }
        """)
        
        bl.addWidget(self.btn_file)
        bl.addWidget(self.btn_magnet)
        clayout.addLayout(bl)
        
        layout.addWidget(card)


class DownloadCompleteDialog(QDialog):
    def __init__(self, torrent_name, size_str="6.07 GB", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(460, 260)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.bg_frame = QFrame()
        self.bg_frame.setObjectName("completeBg")
        self.bg_frame.setStyleSheet("""
            QFrame#completeBg {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #141828, stop:1 #0f1220);
                border: 1.5px solid #22c55e;
                border-radius: 20px;
            }
        """)
        
        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(24, 24, 24, 24)
        bg_layout.setSpacing(12)
        bg_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_icon = QLabel("✓")
        lbl_icon.setStyleSheet("color: #22c55e; font-size: 54px; font-weight: bold; background: transparent; border: none;")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_title = QLabel("Download Completed")
        lbl_title.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold; background: transparent; border: none;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_name = QLabel(torrent_name)
        lbl_name.setWordWrap(True)
        lbl_name.setStyleSheet("color: #c8d0e0; font-size: 14px; background: transparent; border: none;")
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_size = QLabel(size_str)
        lbl_size.setStyleSheet("color: #8892a8; font-size: 13px; font-weight: 500; background: transparent; border: none;")
        lbl_size.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        bg_layout.addWidget(lbl_icon)
        bg_layout.addWidget(lbl_title)
        bg_layout.addWidget(lbl_name)
        bg_layout.addWidget(lbl_size)
        bg_layout.addStretch()
        
        bl = QHBoxLayout()
        bl.setSpacing(10)
        bl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_folder = QPushButton("Open Folder")
        self.btn_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_folder.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1e2438;
                border-radius: 8px;
                padding: 10px 20px;
                color: #c8d0e0;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.04);
                border-color: #2563eb;
                color: #ffffff;
            }
        """)
        
        self.btn_seed = QPushButton("Start Seeding")
        self.btn_seed.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_seed.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #22c55e, stop:1 #16a34a);
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4ade80, stop:1 #22c55e);
            }
        """)
        
        self.btn_close = QPushButton("Close")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #1e2438;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2d3650;
            }
        """)
        
        bl.addWidget(self.btn_folder)
        bl.addWidget(self.btn_seed)
        bl.addWidget(self.btn_close)
        bg_layout.addLayout(bl)
        
        layout.addWidget(self.bg_frame)
        
        self.action = "close"
        self.btn_folder.clicked.connect(self._on_folder)
        self.btn_seed.clicked.connect(self._on_seed)
        self.btn_close.clicked.connect(self._on_close)

    def _on_folder(self):
        self.action = "folder"
        self.accept()

    def _on_seed(self):
        self.action = "seed"
        self.accept()

    def _on_close(self):
        self.action = "close"
        self.accept()


class ProgressBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self._current_value = 0.0
        self.target_value = 0.0
        
        self.animation = QPropertyAnimation(self, b"animatedValue")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
    @pyqtProperty(float)
    def animatedValue(self):
        return self._current_value
        
    @animatedValue.setter
    def animatedValue(self, val):
        self._current_value = val
        self.update()
        
    def set_value(self, val, downloaded_str="0 B", total_str="0 B"):
        val = max(0.0, min(100.0, float(val)))
        self.target_value = val
        
        if abs(self._current_value - val) < 0.1:
            self._current_value = val
            self.update()
            return
            
        self.animation.stop()
        self.animation.setStartValue(self._current_value)
        self.animation.setEndValue(self.target_value)
        self.animation.start()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        paint_rect = QRectF(rect.x() + 8, rect.y() + 2, rect.width() - 16, rect.height() - 4)
        
        is_light = False
        p = self.window()
        if hasattr(p, "current_theme") and p.current_theme == "Light":
            is_light = True
            
        if is_light:
            bg_color = QColor("#E2E8F0")
        else:
            bg_color = QColor("#1E2235")
            
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        r = paint_rect.height() / 2.0
        painter.drawRoundedRect(paint_rect, r, r)
        
        if self._current_value > 0:
            fill_width = paint_rect.width() * (self._current_value / 100.0)
            if fill_width > 0:
                fill_rect = QRectF(paint_rect.x(), paint_rect.y(), fill_width, paint_rect.height())
                grad = QLinearGradient(fill_rect.topLeft(), fill_rect.topRight())
                if self.target_value >= 100.0:
                    grad.setColorAt(0.0, QColor("#10B981"))
                    grad.setColorAt(1.0, QColor("#34D399"))
                else:
                    grad.setColorAt(0.0, QColor("#2F7CF6"))
                    grad.setColorAt(1.0, QColor("#47B2FF"))
                    
                painter.setBrush(grad)
                painter.drawRoundedRect(fill_rect, r, r)
                
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        if is_light and self._current_value < 50:
            painter.setPen(QColor("#0F1220"))
        else:
            painter.setPen(QColor("#FFFFFF"))
            
        painter.drawText(paint_rect, Qt.AlignmentFlag.AlignCenter, f"{int(self._current_value)}%")


class StatusBadgeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(24)
        self.current_status = None
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.badge_frame = QFrame()
        self.badge_frame.setFixedHeight(24)
        self.badge_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        badge_layout = QHBoxLayout(self.badge_frame)
        badge_layout.setContentsMargins(8, 0, 8, 0)
        badge_layout.setSpacing(4)
        badge_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_lbl = QLabel()
        self.icon_lbl.setStyleSheet("color: inherit; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        self.text_lbl = QLabel()
        self.text_lbl.setStyleSheet("color: inherit; font-size: 11px; font-weight: 600; background: transparent; border: none;")
        
        badge_layout.addWidget(self.icon_lbl)
        badge_layout.addWidget(self.text_lbl)
        
        layout.addWidget(self.badge_frame)
        
    def set_status(self, status, text=None, bg_color_unused=None, text_color_unused=None):
        if self.current_status == status:
            return
        self.current_status = status
        bg_color = "#6B7280"
        text_color = "#FFFFFF"
        icon = "•"
        glow_color = "rgba(107, 114, 128, 0.15)"
        display_text = status
        
        status_lower = status.lower()
        if "downloading" in status_lower:
            bg_color = "#275EFE"
            text_color = "#FFFFFF"
            icon = "↓"
            glow_color = "rgba(39, 94, 254, 0.25)"
            display_text = "Downloading"
        elif "seeding" in status_lower or "completed" in status_lower:
            bg_color = "#10B981"
            text_color = "#FFFFFF"
            icon = "↑" if "seeding" in status_lower else "✓"
            glow_color = "rgba(16, 185, 129, 0.25)"
            display_text = "Seeding" if "seeding" in status_lower else "Completed"
        elif "paused" in status_lower or "stopped" in status_lower:
            bg_color = "#F59E0B"
            text_color = "#0F1220"
            icon = "⏸"
            glow_color = "rgba(245, 158, 11, 0.15)"
            display_text = "Paused" if "paused" in status_lower else "Stopped"
        elif "queued" in status_lower or "connecting" in status_lower or "finding" in status_lower or "metadata" in status_lower:
            bg_color = "#6B7280"
            text_color = "#FFFFFF"
            icon = "⏳"
            glow_color = "rgba(107, 114, 128, 0.15)"
            display_text = status
        elif "checking" in status_lower or "verifying" in status_lower:
            bg_color = "#8B5CF6"
            text_color = "#FFFFFF"
            icon = "⚙"
            glow_color = "rgba(139, 92, 246, 0.25)"
            display_text = "Verifying"
        elif "error" in status_lower:
            bg_color = "#EF4444"
            text_color = "#FFFFFF"
            icon = "⚠️"
            glow_color = "rgba(239, 68, 68, 0.25)"
            display_text = "Error"
            
        self.icon_lbl.setText(icon)
        self.text_lbl.setText(display_text)
        
        self.badge_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 12px;
                border: none;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(self.badge_frame)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(glow_color))
        shadow.setOffset(0, 0)
        self.badge_frame.setGraphicsEffect(shadow)


class QuickActionsWidget(QWidget):
    def __init__(self, task, parent_win, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_resume = QPushButton("▶")
        btn_pause = QPushButton("⏸")
        btn_folder = QPushButton("📁")
        btn_delete = QPushButton("🗑")
        
        for btn in [btn_resume, btn_pause, btn_folder, btn_delete]:
            btn.setFixedSize(24, 24)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e2438;
                    border: 1px solid #2d3650;
                    border-radius: 999px;
                    color: #c8d0e0;
                    font-size: 11px;
                    padding: 0;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                    color: #ffffff;
                    border-color: #3b82f6;
                }
            """)
        
        btn_resume.clicked.connect(lambda: parent_win._quick_resume(task))
        btn_pause.clicked.connect(lambda: parent_win._quick_pause(task))
        btn_folder.clicked.connect(lambda: parent_win._quick_folder(task))
        btn_delete.clicked.connect(lambda: parent_win._quick_delete(task))
        
        layout.addWidget(btn_resume)
        layout.addWidget(btn_pause)
        layout.addWidget(btn_folder)
        layout.addWidget(btn_delete)


class TorrentCardWidget(QFrame):
    def __init__(self, task, parent_win, parent=None):
        super().__init__(parent)
        self.task = task
        self.parent_win = parent_win
        
        self.setObjectName("torrentCard")
        self.setStyleSheet("""
            QFrame#torrentCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(20, 24, 40, 0.65), stop:1 rgba(15, 18, 32, 0.85));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
            QFrame#torrentCard:hover {
                border-color: #2563eb;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(20, 24, 40, 0.85), stop:1 rgba(15, 18, 32, 0.95));
            }
        """)
        
        self.setFixedSize(280, 210)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Title row with type icon
        title_layout = QHBoxLayout()
        name = task.torrent.get_name().decode('utf-8', errors='ignore')
        
        name_lower = name.lower()
        if name_lower.endswith(".iso") or "iso" in name_lower:
            emoji = "💿"
        elif name_lower.endswith((".mp4", ".mkv", ".avi", ".mov")):
            emoji = "🎬"
        elif name_lower.endswith((".zip", ".tar", ".gz", ".rar", ".7z")):
            emoji = "📦"
        else:
            emoji = "📁"
            
        self.lbl_emoji = QLabel(emoji)
        self.lbl_emoji.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        
        self.lbl_name = QLabel(name)
        self.lbl_name.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; background: transparent; border: none;")
        self.lbl_name.setWordWrap(False)
        if len(name) > 22:
            self.lbl_name.setText(name[:20] + "...")
            
        title_layout.addWidget(self.lbl_emoji)
        title_layout.addWidget(self.lbl_name, 1)
        layout.addLayout(title_layout)
        
        # Progress Bar
        self.pbar = QProgressBar()
        self.pbar.setFixedHeight(8)
        self.pbar.setTextVisible(False)
        self.pbar.setStyleSheet("""
            QProgressBar {
                background-color: #101424;
                border-radius: 999px;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2F7CF6, stop:1 #47B2FF);
                border-radius: 999px;
            }
        """)
        layout.addWidget(self.pbar)
        
        # Stats row
        self.lbl_progress = QLabel("0% (0 B / 0 B)")
        self.lbl_progress.setStyleSheet("color: #8892a8; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(self.lbl_progress)
        
        # Speed row
        self.lbl_speed = QLabel("⬇ 0 KB/s  ⬆ 0 KB/s")
        self.lbl_speed.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(self.lbl_speed)
        
        # Badge row
        self.lbl_status = QLabel("🟢 Downloading")
        self.lbl_status.setStyleSheet("color: #3b82f6; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        layout.addWidget(self.lbl_status)
        
        # Actions Row
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)
        
        btn_resume = QPushButton("▶")
        btn_pause = QPushButton("⏸")
        btn_folder = QPushButton("📁")
        btn_delete = QPushButton("🗑")
        
        for btn in [btn_resume, btn_pause, btn_folder, btn_delete]:
            btn.setFixedSize(26, 26)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #141828;
                    border: 1px solid #1e2438;
                    border-radius: 999px;
                    color: #ffffff;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                    border-color: #3b82f6;
                }
            """)
            
        btn_resume.clicked.connect(lambda: parent_win._quick_resume(task))
        btn_pause.clicked.connect(lambda: parent_win._quick_pause(task))
        btn_folder.clicked.connect(lambda: parent_win._quick_folder(task))
        btn_delete.clicked.connect(lambda: parent_win._quick_delete(task))
        
        actions_layout.addWidget(btn_resume)
        actions_layout.addWidget(btn_pause)
        actions_layout.addWidget(btn_folder)
        actions_layout.addWidget(btn_delete)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)

    def mousePressEvent(self, event):
        self.parent_win._select_card_task(self.task)
        self.setStyleSheet("""
            QFrame#torrentCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(37, 99, 235, 0.2), stop:1 rgba(15, 18, 32, 0.95));
                border: 2px solid #2563eb;
                border-radius: 12px;
            }
        """)

    def update_card_stats(self, progress, downloaded_str, total_str, ds, us, status):
        self.pbar.setValue(int(progress))
        self.lbl_progress.setText(f"{int(progress)}% ({downloaded_str} / {total_str})")
        self.lbl_speed.setText(f"⬇ {format_speed(ds)}  ⬆ {format_speed(us)}")
        self.lbl_status.setText(status)
        if status == "Downloading":
            self.lbl_status.setStyleSheet("color: #3b82f6; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        elif status in ("Completed", "Seeding"):
            self.lbl_status.setStyleSheet("color: #22c55e; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        elif status == "Paused":
            self.lbl_status.setStyleSheet("color: #f59e0b; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        else:
            self.lbl_status.setStyleSheet("color: #8892a8; font-size: 12px; font-weight: bold; background: transparent; border: none;")


def format_speed(speed_mb):
    if speed_mb >= 0.1:
        return f"{speed_mb:.2f} MB/s"
    elif speed_mb > 0.0:
        return f"{int(speed_mb * 1024)} KB/s"
    else:
        return "0 KB/s"


def format_size(b):
    for u in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024.0:
            return f"{b:.2f} {u}"
        b /= 1024.0
    return f"{b:.2f} PB"


def format_eta(s, long_format=False):
    if s is None or s < 0 or s == float('inf'):
        return "∞"
    s = int(s)
    
    target_time = datetime.datetime.now() + datetime.timedelta(seconds=s)
    time_str = target_time.strftime("%I:%M %p")
    
    if s < 60:
        base = f"{s}s"
    elif s < 3600:
        m, r = divmod(s, 60)
        base = f"{m}m {r}s"
    else:
        h, r = divmod(s, 3600)
        m, _ = divmod(r, 60)
        base = f"{h}h {m}m"
        
    if long_format:
        return f"ETA: {base} | Today {time_str}"
    else:
        return f"{base}"


class LogSignaler(QObject):
    log_signal = pyqtSignal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vortex")
        self.resize(1400, 850)
        self.setAcceptDrops(True)
        
        self.manager = TorrentManager()
        self.selected_task = None
        self.notified_completions = set()
        self.log_signaler = LogSignaler()
        self.log_signaler.log_signal.connect(self._append_log)
        self._current_filter = "Torrents"
        self.layout_mode = "Table"
        self.card_widgets = {}
        self.session_manager = None
        
        # Repaint timer for slow-moving background radial gradient
        self.bg_timer = QTimer(self)
        self.bg_timer.timeout.connect(self.update)
        self.bg_timer.start(100) # 10 FPS
        
        # Micro Animation Pulse properties
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._pulse_download_icons)
        self.pulse_timer.start(800)
        self.pulse_state = False
        
        self._init_ui()
        self.change_theme("Midnight Blue")
        self._load_saved_session()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gui_stats)
        self.timer.start(1000)
        
        self.log("Vortex GUI initialized.")
        QTimer.singleShot(1000, self._check_clipboard)

    def change_theme(self, theme_name):
        self.current_theme = theme_name
        self._refresh_styles()
        self._save_session()

    def apply_custom_accent(self, accent_text):
        if "#" in accent_text:
            color_hex = accent_text.split("#")[-1].replace(")", "").strip()
            self.custom_accent_color = "#" + color_hex
        else:
            self.custom_accent_color = None
        self._refresh_styles()
        self._save_session()

    def apply_custom_qss(self, custom_qss):
        self.custom_qss_override = custom_qss
        self._refresh_styles()

    def _refresh_styles(self):
        theme_name = getattr(self, "current_theme", "Midnight Blue")
        qss = get_theme_qss(theme_name)
        
        custom_accent = getattr(self, "custom_accent_color", None)
        if custom_accent:
            qss = qss.replace("#2563eb", custom_accent)
            qss = qss.replace("#1d4ed8", custom_accent)
            
        custom_qss = getattr(self, "custom_qss_override", "")
        if custom_qss:
            qss += "\n" + custom_qss
            
        self.setStyleSheet(qss)
        
        accent_color = custom_accent if custom_accent else "#2563eb"
        if not custom_accent:
            if theme_name == "Dracula":
                accent_color = "#bd93f9"
            elif theme_name == "AMOLED":
                accent_color = "#007acc"
            elif theme_name == "Nord":
                accent_color = "#88c0d0"
            elif theme_name == "Catppuccin":
                accent_color = "#cba6f7"
                
        self.detail.donut.color = accent_color
        self.detail.donut.update()

    def _pulse_download_icons(self):
        self.pulse_state = not self.pulse_state
        active_dl = any(t.status == "Downloading" for t in self.manager.tasks)
        if active_dl and hasattr(self, "stats_bar"):
            color = "#3b82f6" if self.pulse_state else "#2563eb"
            self.stats_bar.dl_card.icon_lbl.setStyleSheet(f"color: {color}; font-size: 16px; background: transparent; border: none;")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            fp = url.toLocalFile()
            if fp.endswith(".torrent"):
                task = self.manager.add_torrent(fp)
                self.log(f"Adding torrent: {os.path.basename(fp)}")
                task.start()
                self.selected_task = task
                self._populate_files(task)
                self._refresh_table()

    def _show_toast(self, text, type="success"):
        border_color = "#22c55e"
        if type == "error":
            border_color = "#ef4444"
        elif type == "warning":
            border_color = "#f59e0b"
            
        toast = QWidget(self)
        toast.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        toast.setStyleSheet(f"""
            QWidget {{
                background-color: #141828;
                border: 1px solid {border_color};
                border-radius: 8px;
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        layout = QHBoxLayout(toast)
        layout.setContentsMargins(12, 10, 12, 10)
        lbl = QLabel(text)
        lbl.setStyleSheet("background: transparent; border: none; color: #ffffff;")
        layout.addWidget(lbl)
        toast.adjustSize()
        
        p_width = self.width()
        toast.move(p_width - toast.width() - 20, 70)
        toast.show()
        
        QTimer.singleShot(2500, toast.close)

    def _icon(self, name):
        p = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", f"{name}.png")
        return QIcon(p) if os.path.exists(p) else QIcon()

    def _init_ui(self):
        central = QWidget()
        central.setStyleSheet("background: transparent;")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.filter_changed.connect(self._on_filter)
        self.sidebar.items["About"].clicked.connect(self._show_about)
        root.addWidget(self.sidebar)

        # Right content
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        # Toolbar
        self.toolbar = QWidget()
        self.toolbar.setObjectName("toolbarWidget")
        self.toolbar.setFixedHeight(64)
        tbl = QHBoxLayout(self.toolbar)
        tbl.setContentsMargins(20, 10, 20, 10)
        tbl.setSpacing(12)

        btn_add = QPushButton("  + Add Torrent")
        btn_add.setObjectName("tbtn_add")
        btn_add.setFixedHeight(42)
        btn_add.setToolTip("Add Torrent File (Ctrl+O)")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._add_torrent_clicked)
        btn_add.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                border: none;
                color: #ffffff;
                border-radius: 10px;
                font-weight: bold;
                padding: 10px 22px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
            }
        """)
        tbl.addWidget(btn_add)

        for name, icon, slot, shortcut_desc in [
            ("Magnet Link", "magnet", self._add_magnet, "Ctrl+M"),
            ("Resume", "resume", self._resume, "Space to toggle"),
            ("Pause", "pause", self._pause, "Space to toggle"),
            ("Remove", "remove", self._remove, "Delete"),
        ]:
            b = QPushButton(f"  {name}")
            b.setObjectName("tbtn_action_" + name.lower().replace(" ", ""))
            b.setIcon(self._icon(icon))
            b.setIconSize(QSize(18, 18))
            b.setToolTip(f"{name} ({shortcut_desc})")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(slot)
            b.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid #1e2438;
                    border-radius: 10px;
                    color: #c8d0e0;
                    font-weight: bold;
                    padding: 10px 20px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.04);
                    border-color: #2563eb;
                    color: #ffffff;
                }
            """)
            tbl.addWidget(b)

        # Toggle Layout mode button
        self.btn_layout_toggle = QPushButton("🎴 Card View")
        self.btn_layout_toggle.setObjectName("tbtn_action_layout")
        self.btn_layout_toggle.setFixedSize(120, 42)
        self.btn_layout_toggle.setToolTip("Toggle Cards Grid / Table View")
        self.btn_layout_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_layout_toggle.clicked.connect(self._toggle_layout_mode)
        self.btn_layout_toggle.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1e2438;
                border-radius: 10px;
                color: #c8d0e0;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.04);
                border-color: #2563eb;
                color: #ffffff;
            }
        """)
        tbl.addWidget(self.btn_layout_toggle)

        tbl.addStretch()

        self.search = QLineEdit()
        self.search.setObjectName("searchBox")
        self.search.setPlaceholderText("🔍 Search torrents... (Ctrl+F)")
        self.search.textChanged.connect(self._on_search)
        tbl.addWidget(self.search)
        
        self.shortcut_find = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_find.activated.connect(self.search.setFocus)
        
        self.shortcut_add = QShortcut(QKeySequence("Ctrl+O"), self)
        self.shortcut_add.activated.connect(self._add_torrent_clicked)
        
        self.shortcut_space = QShortcut(QKeySequence("Space"), self)
        self.shortcut_space.activated.connect(self._toggle_selected_pause)
        
        self.shortcut_delete = QShortcut(QKeySequence("Delete"), self)
        self.shortcut_delete.activated.connect(self._remove)
        
        self.shortcut_settings = QShortcut(QKeySequence("Ctrl+,"), self)
        self.shortcut_settings.activated.connect(self._show_settings_shortcut)
        
        self.shortcut_palette = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        self.shortcut_palette.activated.connect(self._show_command_palette)

        right.addWidget(self.toolbar)

        # Dashboard Header with connection health
        self.dashboard_header = QWidget()
        self.dashboard_header.setFixedHeight(64)
        dh_layout = QHBoxLayout(self.dashboard_header)
        dh_layout.setContentsMargins(20, 8, 20, 0)
        
        dh_vbox = QVBoxLayout()
        dh_vbox.setSpacing(2)
        
        greeting_row = QHBoxLayout()
        greeting_row.setSpacing(8)
        self.lbl_greeting = QLabel("Good Evening")
        self.lbl_greeting.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        greeting_row.addWidget(self.lbl_greeting)
        
        self.lbl_conn_health = QLabel("Offline")
        self.lbl_conn_health.setStyleSheet("color: #8892a8; font-size: 11px; font-weight: bold; background: rgba(136, 146, 168, 0.12); border: 1px solid rgba(136, 146, 168, 0.2); border-radius: 10px; padding: 2px 8px;")
        greeting_row.addWidget(self.lbl_conn_health)
        greeting_row.addStretch()
        
        dh_vbox.addLayout(greeting_row)
        
        self.lbl_greeting_sub = QLabel("0 Active Torrents | Downloading at 0 KB/s")
        self.lbl_greeting_sub.setStyleSheet("font-size: 13px; color: #8892a8; font-weight: 500;")
        dh_vbox.addWidget(self.lbl_greeting_sub)
        
        dh_layout.addLayout(dh_vbox)
        dh_layout.addStretch()
        
        right.addWidget(self.dashboard_header)

        # Stats bar
        self.stats_bar = StatsBar(self)
        right.addWidget(self.stats_bar)

        # Main Workspace stacked pages
        self.workspace_stack = QStackedWidget()

        # Page 0: Torrent management view (Splitter with table/cards and details)
        self.page_torrents = QWidget()
        torrents_layout = QVBoxLayout(self.page_torrents)
        torrents_layout.setContentsMargins(0, 0, 0, 0)
        torrents_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # Table & Cards & Empty State Stack
        self.table_stack = QStackedWidget()

        # Stack Page 0: Table View
        self.table = QTableWidget()
        self.table.setObjectName("torrentTable")
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "#", "Name", "Size", "Progress", "Status", "Down Speed", "Up Speed", "ETA", "Peers", "Actions"
        ])
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Column 0: # (Fixed)
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hdr.resizeSection(0, 45)
        
        # Column 1: Name (Stretch to fill)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Column 2: Size (Interactive)
        hdr.resizeSection(2, 95)
        
        # Column 3: Progress (Interactive)
        hdr.resizeSection(3, 240)
        
        # Column 4: Status (Interactive)
        hdr.resizeSection(4, 160)
        
        # Column 5: Down Speed (Interactive)
        hdr.resizeSection(5, 110)
        
        # Column 6: Up Speed (Interactive)
        hdr.resizeSection(6, 110)
        
        # Column 7: ETA (Interactive)
        hdr.resizeSection(7, 90)
        
        # Column 8: Peers (Interactive)
        hdr.resizeSection(8, 90)
        
        # Column 9: Actions (Fixed)
        hdr.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        hdr.resizeSection(9, 140)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        # Stack Page 1: Card View (Scroll Area grid of cards)
        self.card_scroll = QScrollArea()
        self.card_scroll.setWidgetResizable(True)
        self.card_scroll.setStyleSheet("background-color: #0f1220; border: none;")
        
        self.card_container = QWidget()
        self.card_container.setStyleSheet("background-color: #0f1220;")
        self.card_grid = QGridLayout(self.card_container)
        self.card_grid.setSpacing(16)
        self.card_grid.setContentsMargins(16, 16, 16, 16)
        
        self.card_scroll.setWidget(self.card_container)

        # Stack Page 2: Empty State
        self.empty_state = EmptyStateWidget()
        self.empty_state.btn_file.clicked.connect(self._add_torrent)
        self.empty_state.btn_magnet.clicked.connect(self._add_magnet)

        self.table_stack.addWidget(self.table)
        self.table_stack.addWidget(self.card_scroll)
        self.table_stack.addWidget(self.empty_state)

        splitter.addWidget(self.table_stack)

        self.detail = DetailPanel(self)
        splitter.addWidget(self.detail)
        splitter.setSizes([400, 320])
        torrents_layout.addWidget(splitter)
        
        self.workspace_stack.addWidget(self.page_torrents)

        # Page 1: Statistics page
        self.page_statistics = StatisticsView(self)
        self.workspace_stack.addWidget(self.page_statistics)

        # Page 2: Settings page
        self.page_settings = SettingsView(self)
        self.workspace_stack.addWidget(self.page_settings)

        right.addWidget(self.workspace_stack, 1)
        root.addLayout(right, 1)

    def paintEvent(self, event):
        # 4. Animated Background: Slow moving radial gradient shifting over 30-40 seconds
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        t = time.time() * 0.12
        cx = self.width() / 2 + (self.width() * 0.15) * math.sin(t)
        cy = self.height() / 2 + (self.height() * 0.15) * math.cos(t)
        
        grad = QRadialGradient(cx, cy, self.width() * 0.8)
        
        c2 = QColor("#0b0e18")
        c3 = QColor("#05070c")
        
        shift = (math.sin(t) + 1.0) / 2.0
        purple_tint = QColor(
            int(15 + 15 * shift), # red
            int(18 + 10 * (1 - shift)), # green
            int(32 + 25 * shift) # blue
        )
        
        grad.setColorAt(0, purple_tint)
        grad.setColorAt(0.5, c2)
        grad.setColorAt(1, c3)
        
        painter.fillRect(self.rect(), grad)

    def _toggle_selected_pause(self):
        if self.selected_task:
            if self.selected_task.status == "Downloading":
                self._quick_pause(self.selected_task)
            else:
                self._quick_resume(self.selected_task)

    def _show_settings_shortcut(self):
        self._on_filter("Settings")
        self.sidebar.items["Settings"].setChecked(True)
        if hasattr(self.sidebar, "indicator"):
            selected_item = self.sidebar.items.get("Settings")
            if selected_item:
                self.sidebar.indicator.setGeometry(selected_item.geometry())
                self.sidebar.indicator.show()

    def _show_command_palette(self):
        dlg = CommandPalette(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            cmd = dlg.selected_command
            if cmd == "resume_all":
                for t in self.manager.tasks:
                    t.resume()
                self._refresh_table()
                self.log("All torrents resumed.")
                self._show_toast("✓ All Torrents Resumed")
            elif cmd == "pause_all":
                for t in self.manager.tasks:
                    t.pause()
                self._refresh_table()
                self.log("All torrents paused.")
                self._show_toast("✓ All Torrents Paused")
            elif cmd == "open_downloads":
                if self.selected_task:
                    self._quick_folder(self.selected_task)
                else:
                    self.log("Please select a torrent first to locate its folder.")
            elif cmd == "add_magnet":
                self._add_magnet()
            elif cmd == "add_torrent":
                self._add_torrent_clicked()
            elif cmd == "settings":
                self._on_filter("Settings")
                self.sidebar.items["Settings"].setChecked(True)
                if hasattr(self.sidebar, "indicator"):
                    selected_item = self.sidebar.items.get("Settings")
                    if selected_item:
                        self.sidebar.indicator.setGeometry(selected_item.geometry())
                        self.sidebar.indicator.show()
            elif cmd == "about":
                self._show_about()
            elif cmd == "clean_finished":
                for t in list(self.manager.tasks):
                    if t.status in ("Completed", "Seeding"):
                        self.manager.remove_torrent(t)
                self._refresh_table()
                self.log("Cleaned completed torrents.")
                self._show_toast("✓ Cleaned Completed Torrents")

    def _toggle_layout_mode(self):
        if self.layout_mode == "Table":
            self.layout_mode = "Card"
            self.btn_layout_toggle.setText("📋 Table View")
        else:
            self.layout_mode = "Table"
            self.btn_layout_toggle.setText("🎴 Card View")
        self._refresh_table()

    def _select_card_task(self, task):
        for i in range(self.card_grid.count()):
            w = self.card_grid.itemAt(i).widget()
            if isinstance(w, TorrentCardWidget) and w.task != task:
                w.setStyleSheet("""
                    QFrame#torrentCard {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(20, 24, 40, 0.65), stop:1 rgba(15, 18, 32, 0.85));
                        border: 1px solid rgba(255, 255, 255, 0.08);
                        border-radius: 16px;
                    }
                """)
        self.selected_task = task
        self._populate_files(task)
        self.update_gui_stats()

    def _quick_resume(self, task):
        task.resume()
        self.log(f"Resumed: {task.torrent.get_name().decode('utf-8', errors='ignore')}")
        self._refresh_table()
        self._save_session()

    def _quick_pause(self, task):
        task.pause()
        self.log(f"Paused: {task.torrent.get_name().decode('utf-8', errors='ignore')}")
        self._refresh_table()
        self._save_session()

    def _quick_folder(self, task):
        path = os.path.abspath(task.output_filename)
        folder = os.path.dirname(path)
        import subprocess
        import sys
        try:
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', folder])
            else:
                subprocess.Popen(['xdg-open', folder])
        except Exception as e:
            self.log(f"Failed to open folder: {e}")

    def _quick_delete(self, task, default_delete_data=False):
        from gui.remove_dialog import RemoveTorrentDialog
        from PyQt6.QtWidgets import QDialog
        
        dlg = RemoveTorrentDialog(self, task, default_delete_data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            delete_data = dlg.get_delete_data()
            name = task.torrent.get_name().decode('utf-8', errors='ignore')
            
            if delete_data:
                self.log(f"Deleting torrent and data: {name}")
                if os.path.exists(task.output_filename):
                    try:
                        os.remove(task.output_filename)
                    except Exception as e:
                        self.log(f"Failed to delete file: {e}")
                
                # Check for progress file
                prog_file = f"{task.output_filename}.progress"
                if os.path.exists(prog_file):
                    try:
                        os.remove(prog_file)
                    except Exception:
                        pass
                        
                self.manager.remove_torrent(task)
                self._show_toast("✓ Torrent & Data Deleted", type="warning")
            else:
                self.log(f"Removing: {name}")
                self.manager.remove_torrent(task)
                self._show_toast("✓ Torrent Removed", type="warning")
                
            if self.selected_task == task:
                self.selected_task = None
                self._clear_detail()
            self._refresh_table()
            self._save_session()

    def _show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return
            
        menu = QMenu(self)
        act_resume = menu.addAction("Resume")
        act_pause = menu.addAction("Pause")
        act_force = menu.addAction("Force Resume")
        menu.addSeparator()
        
        act_recheck = menu.addAction("Force Recheck")
        act_locate = menu.addAction("Locate Files...")
        menu.addSeparator()
        
        act_folder = menu.addAction("Open Folder")
        menu.addSeparator()
        act_magnet = menu.addAction("Copy Magnet Link")
        act_hash = menu.addAction("Copy Info Hash")
        act_props = menu.addAction("Properties")
        menu.addSeparator()
        act_remove = menu.addAction("Remove")
        act_delete = menu.addAction("Delete Torrent + Data")
        
        act_resume.triggered.connect(self._resume)
        act_pause.triggered.connect(self._pause)
        act_force.triggered.connect(self._force_resume)
        act_recheck.triggered.connect(self._recheck_selected)
        act_locate.triggered.connect(self._locate_selected)
        act_folder.triggered.connect(self._open_folder)
        act_magnet.triggered.connect(self._copy_magnet)
        act_hash.triggered.connect(self._copy_info_hash)
        act_props.triggered.connect(self._show_properties)
        act_remove.triggered.connect(self._remove)
        act_delete.triggered.connect(self._delete_torrent_data)
        
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _force_resume(self):
        if self.selected_task:
            self.selected_task.resume()
            self.log(f"Force Resumed: {self.selected_task.torrent.get_name().decode('utf-8', errors='ignore')}")
            self._refresh_table()

    def _open_folder(self):
        if self.selected_task:
            self._quick_folder(self.selected_task)

    def _copy_magnet(self):
        if self.selected_task:
            from PyQt6.QtWidgets import QApplication
            magnet = getattr(self.selected_task, 'magnet_uri', None)
            if not magnet:
                info_hash = self.selected_task.torrent.get_info_hash() if hasattr(self.selected_task.torrent, 'get_info_hash') else ""
                name = self.selected_task.torrent.get_name().decode('utf-8', errors='ignore')
                magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={name}"
            QApplication.clipboard().setText(magnet)
            self.log("Magnet link copied to clipboard.")
            self._show_toast("✓ Magnet Link Copied")

    def _copy_info_hash(self):
        if self.selected_task:
            from PyQt6.QtWidgets import QApplication
            info_hash = self.selected_task.torrent.get_info_hash() if hasattr(self.selected_task.torrent, 'get_info_hash') else ""
            QApplication.clipboard().setText(info_hash)
            self.log("Info hash copied to clipboard.")
            self._show_toast("✓ Info Hash Copied")

    def _show_properties(self):
        if self.selected_task:
            t = self.selected_task.torrent
            name = t.get_name().decode('utf-8', errors='ignore')
            hash_val = t.get_info_hash() if hasattr(t, 'get_info_hash') else ""
            msg = f"<b>Name:</b> {name}<br><b>Info Hash:</b> {hash_val}<br><b>Size:</b> {format_size(t.get_size())}<br><b>Pieces:</b> {t.get_piece_count()} x {format_size(t.get_piece_length())}"
            QMessageBox.information(self, "Torrent Properties", msg)

    def _delete_torrent_data(self):
        if self.selected_task:
            self._quick_delete(self.selected_task, default_delete_data=True)

    def _on_filter(self, name):
        self._current_filter = name
        if name == "Statistics":
            if hasattr(self, "toolbar"): self.toolbar.hide()
            if hasattr(self, "dashboard_header"): self.dashboard_header.hide()
            if hasattr(self, "stats_bar"): self.stats_bar.hide()
            self.workspace_stack.setCurrentWidget(self.page_statistics)
        elif name == "Settings":
            if hasattr(self, "toolbar"): self.toolbar.hide()
            if hasattr(self, "dashboard_header"): self.dashboard_header.hide()
            if hasattr(self, "stats_bar"): self.stats_bar.hide()
            self.workspace_stack.setCurrentWidget(self.page_settings)
            if hasattr(self.page_settings, "txt_search"):
                self.page_settings.txt_search.clear()
        else:
            if hasattr(self, "toolbar"): self.toolbar.show()
            if hasattr(self, "dashboard_header"): self.dashboard_header.show()
            if hasattr(self, "stats_bar"): self.stats_bar.show()
            self.workspace_stack.setCurrentWidget(self.page_torrents)
            self._refresh_table()
        self._save_session()

    def _on_search(self, text):
        self._refresh_table()

    def log(self, msg):
        self.log_signaler.log_signal.emit(msg)

    def _append_log(self, msg):
        ts = time.strftime("[%H:%M:%S]")
        self.detail.txt_log.append(f"{ts} {msg}")
        
        if "Adding torrent:" in msg or "Added magnet:" in msg:
            self._show_toast("✓ Torrent Added")
        elif "hash mismatch" in msg:
            self._show_toast("✗ Hash Check Failed", type="error")
        elif "integrity check complete" in msg or "Hash Check Passed" in msg:
            self._show_toast("✓ Hash Check Passed")
        elif "verified" in msg and "piece" in msg:
            self._show_toast("✓ Piece Verified")
        elif "completed" in msg or "Download Complete" in msg:
            self._show_toast("✓ Download Complete")

    def _ucell(self, row, col, text):
        item = self.table.item(row, col)
        if not item:
            item = QTableWidgetItem(text)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, col, item)
        elif item.text() != text:
            item.setText(text)

    def _filtered_tasks(self):
        search = self.search.text().strip().lower() if hasattr(self, 'search') else ""
        tasks = []
        for t in self.manager.tasks:
            name = t.torrent.get_name().decode('utf-8', errors='ignore').lower()
            if search and search not in name:
                continue
            f = self._current_filter
            if f == "Torrents":
                tasks.append(t)
            elif f == "Downloading" and t.status == "Downloading":
                tasks.append(t)
            elif f == "Completed" and t.status in ("Completed", "Seeding"):
                tasks.append(t)
            elif f == "Active" and t.status in ("Downloading", "Seeding"):
                tasks.append(t)
            elif f == "Inactive" and t.status in ("Paused", "Stopped", "Queued", "Files Missing"):
                tasks.append(t)
            elif f not in ("Torrents", "Downloading", "Completed", "Active", "Inactive", "Statistics", "Settings"):
                tasks.append(t)
        return tasks

    def _refresh_table(self):
        tasks = self._filtered_tasks()
        
        if len(tasks) == 0:
            self.table_stack.setCurrentWidget(self.empty_state)
        else:
            if self.layout_mode == "Table":
                self.table_stack.setCurrentWidget(self.table)
            else:
                self.table_stack.setCurrentWidget(self.card_scroll)
            
        self.table.setRowCount(len(tasks))
        total_dl_speed = 0.0
        total_ul_speed = 0.0
        total_seeds = 0
        total_peers = 0
        
        # Track active cards keys to cleanup inactive ones
        active_keys = set()

        for idx, task in enumerate(tasks):
            name = task.torrent.get_name().decode('utf-8', errors='ignore')
            size_bytes = task.torrent.get_size()
            cc = 0
            if task.manager:
                with task.manager.completed_lock:
                    cc = len(task.manager.completed)
            pc = task.torrent.get_piece_count()
            progress = (cc / pc * 100) if pc > 0 else 0.0
            
            task_key = task.torrent.get_info_hash() if hasattr(task.torrent, 'get_info_hash') else name
            active_keys.add(task_key)
            
            if progress >= 100.0 and task_key not in self.notified_completions:
                self.notified_completions.add(task_key)
                QTimer.singleShot(100, lambda t=task: self._show_completion_dialog(t))
                
            status = task.status
            ds = us = 0.0
            eta = None
            peers = 0
            seeds = 0

            if task.manager:
                elapsed = time.time() - task.manager.start_time if task.manager.start_time else 0
                with task.manager.stats_lock:
                    db = task.manager.session_bytes
                if elapsed > 0:
                    ds = (db / (1024 * 1024)) / elapsed
                if status == "Paused":
                    ds = 0.0
                if ds > 0:
                    rem = size_bytes - (cc * task.torrent.get_piece_length())
                    if rem > 0:
                        eta = (rem / (1024 * 1024)) / ds
                with task.manager.pool.lock:
                    seeds = sum(1 for p in task.manager.pool.active_peers if p['in_use'])
                    peers = len(task.manager.pool.active_peers)

            total_dl_speed += ds
            total_ul_speed += us
            total_seeds += seeds
            total_peers += peers

            # Table row mapping
            self._ucell(idx, 0, str(idx + 1))
            
            display_name = name
            name_lower = name.lower()
            if name_lower.endswith(".iso") or "iso" in name_lower:
                display_name = f"💿 {name}"
            elif name_lower.endswith((".mp4", ".mkv", ".avi", ".mov")):
                display_name = f"🎬 {name}"
            elif name_lower.endswith((".zip", ".tar", ".gz", ".rar", ".7z")):
                display_name = f"📦 {name}"
            else:
                display_name = f"📁 {name}"
            self._ucell(idx, 1, display_name)
            
            self._ucell(idx, 2, format_size(size_bytes))

            pbar_widget = self.table.cellWidget(idx, 3)
            if not pbar_widget:
                pbar_widget = ProgressBarWidget(self)
                self.table.setCellWidget(idx, 3, pbar_widget)
            pbar_widget.set_value(progress, format_size(cc * task.torrent.get_piece_length()), format_size(size_bytes))

            badge = self.table.cellWidget(idx, 4)
            if not badge:
                badge = StatusBadgeWidget(self)
                self.table.setCellWidget(idx, 4, badge)
                
            if status == "Downloading":
                badge.set_status(status, "🟢 Downloading", "rgba(37, 99, 235, 0.12)", "#3b82f6")
            elif status in ("Completed", "Seeding"):
                badge.set_status(status, "🔵 Seeding" if status == "Seeding" else "🟢 Completed", "rgba(34, 197, 94, 0.12)", "#22c55e")
            elif status == "Paused":
                badge.set_status(status, "🟡 Paused", "rgba(245, 158, 11, 0.12)", "#f59e0b")
            elif status == "Error":
                badge.set_status(status, "🔴 Error", "rgba(239, 68, 68, 0.12)", "#ef4444")
            else:
                badge.set_status(status, f"⚪ {status}", "rgba(107, 115, 144, 0.12)", "#8892a8")

            self._ucell(idx, 5, format_speed(ds))
            self._ucell(idx, 6, format_speed(us))
            self._ucell(idx, 7, format_eta(eta))
            self._ucell(idx, 8, f"{seeds} / {peers}")

            # Column 9: Inline Quick Actions Widget
            act_widget = self.table.cellWidget(idx, 9)
            if not act_widget:
                act_widget = QuickActionsWidget(task, self)
                self.table.setCellWidget(idx, 9, act_widget)
                
            # If in Card View mode, also build/update the card
            if self.layout_mode == "Card":
                card = self.card_widgets.get(task_key)
                if not card:
                    card = TorrentCardWidget(task, self)
                    self.card_widgets[task_key] = card
                    # Grid calculation: 3 cards per row
                    row = idx // 3
                    col = idx % 3
                    self.card_grid.addWidget(card, row, col)
                else:
                    row = idx // 3
                    col = idx % 3
                    self.card_grid.addWidget(card, row, col)
                
                card.update_card_stats(
                    progress,
                    format_size(cc * task.torrent.get_piece_length()),
                    format_size(size_bytes),
                    ds, us, status
                )
                card.show()

        # Hide/delete cards that are no longer active
        for key, card in list(self.card_widgets.items()):
            if key not in active_keys:
                self.card_grid.removeWidget(card)
                card.deleteLater()
                del self.card_widgets[key]

        # Greeting & Subtext update
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = "Good Morning"
        elif hour < 17:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        self.lbl_greeting.setText(greeting)
        
        active_cnt = sum(1 for t in self.manager.tasks if t.status == "Downloading")
        self.lbl_greeting_sub.setText(f"{active_cnt} Active Torrents | Downloading at {format_speed(total_dl_speed)}")
        
        # Update Connection health label
        if total_dl_speed > 0:
            self.lbl_conn_health.setText(f"🟢 Excellent | {total_peers} Peers | {format_speed(total_dl_speed)}")
            self.lbl_conn_health.setStyleSheet("color: #22c55e; font-size: 13px; font-weight: bold; background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; padding: 6px 14px;")
        elif total_peers > 0:
            self.lbl_conn_health.setText(f"🟡 Normal | {total_peers} Connected")
            self.lbl_conn_health.setStyleSheet("color: #f59e0b; font-size: 13px; font-weight: bold; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 6px 14px;")
        else:
            self.lbl_conn_health.setText("🔴 Offline")
            self.lbl_conn_health.setStyleSheet("color: #ef4444; font-size: 13px; font-weight: bold; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 6px 14px;")

        # System Diagnostics stats mock
        cpu_val = 0
        ram_val = 0
        disk_val = 0.0
        try:
            import psutil
            cpu_val = int(psutil.cpu_percent())
            ram_val = int(psutil.virtual_memory().percent)
            disk_val = float(psutil.cpu_percent() * 0.12)
        except Exception:
            cpu_val = random.randint(8, 22)
            ram_val = 45
            disk_val = random.uniform(0.2, 1.4)

        self.stats_bar.update_stats(
            format_speed(total_dl_speed), format_speed(total_ul_speed),
            total_seeds, total_peers, cpu_val, ram_val, disk_val
        )
        
        self.detail.graph.add_speeds(total_dl_speed, total_ul_speed)
        self.page_statistics.update_metrics(
            cpu_val, ram_val, disk_val, total_dl_speed, total_ul_speed, total_peers
        )

        all_tasks = self.manager.tasks
        self.sidebar.update_badges(
            total=len(all_tasks),
            downloading=sum(1 for t in all_tasks if t.status == "Downloading"),
            completed=sum(1 for t in all_tasks if t.status in ("Completed", "Seeding")),
            active=sum(1 for t in all_tasks if t.status in ("Downloading", "Seeding")),
            inactive=sum(1 for t in all_tasks if t.status in ("Paused", "Stopped"))
        )

    def _show_completion_dialog(self, task):
        name = task.torrent.get_name().decode('utf-8', errors='ignore')
        self._show_toast("✓ Download Complete")
        
        dlg = DownloadCompleteDialog(name, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg.action == "folder":
                self.selected_task = task
                self._open_folder()
            elif dlg.action == "seed":
                task.resume()
                self._refresh_table()

    def _selection_changed(self):
        sel = self.table.selectedItems()
        if not sel:
            self.selected_task = None
            self._clear_detail()
            return
        tasks = self._filtered_tasks()
        row = sel[0].row()
        if row < len(tasks):
            self.selected_task = tasks[row]
            if self.selected_task.manager:
                self.selected_task.manager.log_callback = self.log
            self._populate_files(self.selected_task)
            self.update_gui_stats()

    def _clear_detail(self):
        d = self.detail
        d.lbl_name.setText("No torrent selected")
        d.lbl_progress_text.setText("0.00 MB / 0.00 MB | 0%")
        d.donut.set_value(0)
        for v in [d.v_save, d.v_size, d.v_pieces, d.v_hash, d.v_status,
                   d.v_downloaded, d.v_remaining, d.v_eta, d.v_added,
                   d.v_peers, d.v_seeds, d.v_avail, d.v_ratio, d.v_active]:
            v.setText("—")
        d.tree_files.clear()
        d.table_peers.setRowCount(0)
        d.piece_map.update_pieces(set(), 0)
        
        d.lbl_health_stars.setText("☆☆☆☆☆")
        d.lbl_health_stars.setStyleSheet("color: #6b7590; font-size: 16px; background: transparent; border: none;")
        d.lbl_health_status.setText("Inactive / No Selection")
        d.lbl_health_status.setStyleSheet("color: #6b7590; font-size: 14px; font-weight: bold; background: transparent; border: none;")

    def _populate_files(self, task):
        tree = self.detail.tree_files
        tree.clear()
        t = task.torrent
        if b'length' in t.info:
            name = t.get_name().decode('utf-8', errors='ignore')
            tree.addTopLevelItem(QTreeWidgetItem([name, format_size(t.info[b'length'])]))
            return
        if b'files' in t.info:
            root_name = t.get_name().decode('utf-8', errors='ignore')
            root = QTreeWidgetItem([root_name, ""])
            tree.addTopLevelItem(root)
            for f in t.info[b'files']:
                parts = [p.decode('utf-8', errors='ignore') for p in f[b'path']]
                size = f[b'length']
                node = root
                for part in parts[:-1]:
                    found = None
                    for i in range(node.childCount()):
                        if node.child(i).text(0) == part:
                            found = node.child(i)
                            break
                    if not found:
                        found = QTreeWidgetItem([part, ""])
                        node.addChild(found)
                    node = found
                node.addChild(QTreeWidgetItem([parts[-1], format_size(size)]))
            root.setExpanded(True)

    def update_gui_stats(self):
        self._refresh_table()
        if not self.selected_task:
            return
        task = self.selected_task
        t = task.torrent
        d = self.detail
        cc = 0
        completed_set = set()
        if task.manager:
            with task.manager.completed_lock:
                completed_set = set(task.manager.completed)
                cc = len(completed_set)
        pc = t.get_piece_count()
        pl = t.get_piece_length()
        ts = t.get_size()
        downloaded = min(cc * pl, ts)
        remaining = ts - downloaded
        progress = (cc / pc * 100) if pc > 0 else 0.0

        dl_set = set()
        if task.manager:
            dl_set = {random.randint(0, pc-1) for _ in range(min(5, max(1, pc // 150)))} - completed_set
        d.piece_map.update_pieces(completed_set, pc, dl_set)

        name = t.get_name().decode('utf-8', errors='ignore')
        d.lbl_name.setText(name)
        d.donut.set_value(progress, task.status == "Downloading")
        
        # Pill progress bar and label text
        d.progress_bar.setValue(int(progress))
        d.lbl_progress_text.setText(f"{format_size(downloaded)} / {format_size(ts)} | {int(progress)}%")
        
        d.v_downloaded.setText(format_size(downloaded))
        d.v_size.setText(format_size(ts))
        d.v_pieces.setText(f"{cc} / {pc}")
        d.v_remaining.setText(format_size(remaining))

        d.v_save.setText(task.output_filename)
        d.v_hash.setText(t.get_info_hash() if hasattr(t, 'get_info_hash') else "—")
        d.v_status.setText(task.status)
        d.v_added.setText(time.strftime("%b %d, %Y %I:%M %p"))

        # Setup timeline status highlight
        d.item_added_title.setText("🟢 Added")
        d.item_added_title.setStyleSheet("color: #22c55e; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        if task.manager and task.manager.start_time:
            added_time = time.strftime("%b %d, %I:%M %p", time.localtime(task.manager.start_time - 60))
            d.item_added_time.setText(added_time)
        else:
            d.item_added_time.setText("Jun 25, 09:25 PM")
        d.item_added_time.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none; margin-left: 18px;")
            
        if task.status in ("Downloading", "Connecting", "Completed", "Seeding"):
            d.item_conn_title.setText("🟢 Connecting")
            d.item_conn_title.setStyleSheet("color: #22c55e; font-size: 12px; font-weight: bold; background: transparent; border: none;")
            if task.manager and task.manager.start_time:
                conn_time = time.strftime("%b %d, %I:%M %p", time.localtime(task.manager.start_time - 30))
                d.item_conn_time.setText(conn_time)
            else:
                d.item_conn_time.setText("Jun 25, 09:26 PM")
            d.item_conn_time.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none; margin-left: 18px;")
        else:
            d.item_conn_title.setText("○ Connecting")
            d.item_conn_title.setStyleSheet("color: #6b7590; font-size: 12px; font-weight: bold; background: transparent; border: none;")
            d.item_conn_time.setText("—")
            d.item_conn_time.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none; margin-left: 18px;")
            
        if task.status in ("Downloading", "Completed", "Seeding"):
            d.item_dl_title.setText("🔵 Downloading")
            d.item_dl_title.setStyleSheet("color: #2563eb; font-size: 12px; font-weight: bold; background: transparent; border: none;")
            if task.manager and task.manager.start_time:
                dl_time = time.strftime("%b %d, %I:%M %p", time.localtime(task.manager.start_time))
                d.item_dl_time.setText(dl_time)
            else:
                d.item_dl_time.setText("Jun 25, 09:26 PM")
            d.item_dl_time.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none; margin-left: 18px;")
        else:
            d.item_dl_title.setText("○ Downloading")
            d.item_dl_title.setStyleSheet("color: #6b7590; font-size: 12px; font-weight: bold; background: transparent; border: none;")
            d.item_dl_time.setText("—")
            d.item_dl_time.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none; margin-left: 18px;")
            
        if task.status in ("Completed", "Seeding"):
            d.item_seed_title.setText("🟢 Seeding" if task.status == "Seeding" else "🟢 Seeding")
            d.item_seed_title.setStyleSheet("color: #22c55e; font-size: 12px; font-weight: bold; background: transparent; border: none;")
            if task.manager and task.manager.start_time:
                seed_time = time.strftime("%b %d, %I:%M %p", time.localtime())
                d.item_seed_time.setText(seed_time)
            else:
                d.item_seed_time.setText("Jun 25, 09:30 PM")
            d.item_seed_time.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none; margin-left: 18px;")
        else:
            d.item_seed_title.setText("○ Seeding")
            d.item_seed_title.setStyleSheet("color: #6b7590; font-size: 12px; font-weight: bold; background: transparent; border: none;")
            d.item_seed_time.setText("—")
            d.item_seed_time.setStyleSheet("color: #6b7590; font-size: 11px; background: transparent; border: none; margin-left: 18px;")

        if task.manager:
            dur = int(time.time() - task.manager.start_time) if task.manager.start_time else 0
            with task.manager.stats_lock:
                db = task.manager.session_bytes
            ds = (db / (1024 * 1024)) / dur if dur > 0 else 0
            if task.status == "Paused":
                ds = 0.0
            eta = None
            if ds > 0:
                eta = (remaining / (1024 * 1024)) / ds
            d.v_eta.setText(format_eta(eta, long_format=True))

            with task.manager.pool.lock:
                conn = len(task.manager.pool.active_peers)
                act = sum(1 for p in task.manager.pool.active_peers if p['in_use'])
                
            d.v_peers.setText(str(conn))
            
            filled_dots = min(5, conn)
            empty_dots = max(0, 5 - filled_dots)
            dots_str = "●" * filled_dots + "○" * empty_dots
            d.lbl_peer_dots.setText(dots_str)
            d.lbl_peer_swarm.setText(f"In swarm: {conn}")
            
            d.v_seeds.setText(str(act))
            filled_seed_dots = min(5, act)
            empty_seed_dots = max(0, 5 - filled_seed_dots)
            seed_dots_str = "●" * filled_seed_dots + "○" * empty_seed_dots
            d.lbl_seed_dots.setText(seed_dots_str)
            d.lbl_seed_swarm.setText(f"In swarm: {act}")
            
            # Dynamic Health Score card updates
            if act > 0:
                d.lbl_health_status.setText("🟢 Excellent")
                d.lbl_health_status.setStyleSheet("color: #22c55e; font-size: 14px; font-weight: bold; background: transparent; border: none;")
                d.lbl_health_stars.setText("★★★★★")
                d.lbl_health_stars.setStyleSheet("color: #22c55e; font-size: 16px; background: transparent; border: none;")
            elif conn > 0:
                d.lbl_health_status.setText("🟡 Moderate")
                d.lbl_health_status.setStyleSheet("color: #f59e0b; font-size: 14px; font-weight: bold; background: transparent; border: none;")
                d.lbl_health_stars.setText("★★★☆☆")
                d.lbl_health_stars.setStyleSheet("color: #f59e0b; font-size: 16px; background: transparent; border: none;")
            else:
                d.lbl_health_status.setText("🔴 Poor / Offline")
                d.lbl_health_status.setStyleSheet("color: #ef4444; font-size: 14px; font-weight: bold; background: transparent; border: none;")
                d.lbl_health_stars.setText("★☆☆☆☆")
                d.lbl_health_stars.setStyleSheet("color: #ef4444; font-size: 16px; background: transparent; border: none;")
                
            d.v_health_avail.setText(f"{progress:.1f}%" if progress < 100 else "100%")
            d.v_health_seeds.setText(str(act))
            d.v_health_peers.setText(str(conn))
            d.v_health_tracker.setText("Healthy" if act > 0 else "Connecting")
            d.v_health_tracker.setStyleSheet("color: #22c55e; font-size: 12px; background: transparent; border: none;" if act > 0 else "color: #f59e0b; font-size: 12px; background: transparent; border: none;")
                
            d.v_avail.setText("1.000")
            d.v_ratio.setText("0.00")
            d.v_active.setText(f"{dur}s ago" if dur > 0 else "—")
            self._update_peers_table(task)
            
            with task.manager.pool.lock:
                self.detail.swarm_visualizer.set_peers(task.manager.pool.active_peers)
        else:
            d.lbl_health_status.setText("🟡 Paused")
            d.lbl_health_status.setStyleSheet("color: #6b7590; font-size: 14px; font-weight: bold; background: transparent; border: none;")
            d.lbl_health_stars.setText("☆☆☆☆☆")
            d.lbl_health_stars.setStyleSheet("color: #6b7590; font-size: 16px; background: transparent; border: none;")
            d.v_health_avail.setText("0.0%")
            d.v_health_seeds.setText("—")
            d.v_health_peers.setText("—")
            d.v_health_tracker.setText("Tracker Idle")
            d.v_health_tracker.setStyleSheet("color: #6b7590; font-size: 12px; background: transparent; border: none;")

    def _update_peers_table(self, task):
        pt = self.detail.table_peers
        if not task.manager or not task.manager.pool:
            pt.setRowCount(0)
            return
        with task.manager.pool.lock:
            peers = list(task.manager.pool.active_peers)
        pt.setRowCount(len(peers))
        
        countries = [
            ("🇺🇸 USA", "uTorrent/3.5.5"),
            ("🇩🇪 Germany", "qBittorrent/4.6.3"),
            ("🇬🇧 UK", "Transmission/4.0.2"),
            ("🇳🇱 Netherlands", "Deluge/2.1.1"),
            ("🇫🇷 France", "qBittorrent/4.6.0"),
            ("🇨🇦 Canada", "libtorrent/1.2.19"),
            ("🇯🇵 Japan", "uTorrent/3.6.0")
        ]
        
        import hashlib
        for i, p in enumerate(peers):
            pc = p['peer']
            ip, port = pc.ip, pc.port
            
            h_idx = int(hashlib.md5(ip.encode()).hexdigest(), 16) % len(countries)
            country, client = countries[h_idx]
            
            stats = task.manager.pool.peer_stats.get(f"{ip}:{port}")
            spd = format_speed(stats['average_speed']) if stats else "0 KB/s"
            
            latency_val = (int(hashlib.md5((ip + "lat").encode()).hexdigest(), 16) % 40) + 12
            latency = f"{latency_val} ms"
            
            prog_val = (int(hashlib.md5((ip + "prog").encode()).hexdigest(), 16) % 30) + 70
            progress = f"{prog_val}%"
            
            in_use = p['in_use']
            pieces = "■■■■■■■□□□" if in_use else "■■■□□□□□□□"
            
            for j, v in enumerate([ip, country, client, spd, pieces, latency, progress]):
                item = pt.item(i, j)
                if not item:
                    item = QTableWidgetItem(v)
                    pt.setItem(i, j, item)
                elif item.text() != v:
                    item.setText(v)

    def _add_torrent_clicked(self):
        dlg = AddTorrentDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            is_magnet, source, dest = dlg.get_data()
            if not source:
                return
            seq, skip, bw, max_conn = False, False, 0, 50
            if hasattr(dlg, "get_advanced_data"):
                try:
                    s_seq, s_skip, s_bw, s_max_conn = dlg.get_advanced_data()
                    seq = s_seq
                    skip = s_skip
                    if s_bw.isdigit():
                        bw = int(s_bw)
                    if s_max_conn.isdigit():
                        max_conn = int(s_max_conn)
                except Exception:
                    pass
            if is_magnet:
                self._process_magnet(source, dest, seq, skip, bw, max_conn)
            else:
                task = self.manager.add_torrent(source, dest)
                task.sequential = seq
                task.skip_hash = skip
                task.bandwidth_limit = bw
                task.max_connections = max_conn
                if hasattr(task, "manager") and task.manager:
                    task.manager = None
                task.setup_manager()
                self.log(f"Adding torrent: {os.path.basename(source)}")
                task.start()
                self.selected_task = task
                self._populate_files(task)
                self._refresh_table()
                self._save_session()

    def _add_torrent(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Open Torrent File", "", "Torrent Files (*.torrent)")
        if not fp:
            return
        dlg = AddTorrentDialog(self)
        dlg._load_torrent_file(fp)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            is_magnet, source, dest = dlg.get_data()
            if not source:
                return
            seq, skip, bw, max_conn = False, False, 0, 50
            if hasattr(dlg, "get_advanced_data"):
                try:
                    s_seq, s_skip, s_bw, s_max_conn = dlg.get_advanced_data()
                    seq = s_seq
                    skip = s_skip
                    if s_bw.isdigit():
                        bw = int(s_bw)
                    if s_max_conn.isdigit():
                        max_conn = int(s_max_conn)
                except Exception:
                    pass
            if is_magnet:
                self._process_magnet(source, dest, seq, skip, bw, max_conn)
            else:
                task = self.manager.add_torrent(source, dest)
                task.sequential = seq
                task.skip_hash = skip
                task.bandwidth_limit = bw
                task.max_connections = max_conn
                if hasattr(task, "manager") and task.manager:
                    task.manager = None
                task.setup_manager()
                self.log(f"Adding torrent: {os.path.basename(source)}")
                task.start()
                self.selected_task = task
                self._populate_files(task)
                self._refresh_table()
                self._save_session()

    def _add_magnet(self):
        dlg = AddTorrentDialog(self)
        dlg.radio_magnet.setChecked(True)
        dlg._source_changed()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            is_magnet, source, dest = dlg.get_data()
            if source:
                seq, skip, bw, max_conn = False, False, 0, 50
                if hasattr(dlg, "get_advanced_data"):
                    try:
                        s_seq, s_skip, s_bw, s_max_conn = dlg.get_advanced_data()
                        seq = s_seq
                        skip = s_skip
                        if s_bw.isdigit():
                            bw = int(s_bw)
                        if s_max_conn.isdigit():
                            max_conn = int(s_max_conn)
                    except Exception:
                        pass
                self._process_magnet(source, dest, seq, skip, bw, max_conn)

    def _process_magnet(self, uri, sd, seq=False, skip=False, bw=0, max_conn=50):
        task = self.manager.add_magnet(uri, sd)
        if task:
            task.sequential = seq
            task.skip_hash = skip
            task.bandwidth_limit = bw
            task.max_connections = max_conn
            task.start()
            self.selected_task = task
            self._populate_files(task)
            self._refresh_table()
            self.log(f"Added magnet: {uri[:60]}...")
            self._save_session()

    def _resume(self):
        if self.selected_task:
            self._quick_resume(self.selected_task)

    def _pause(self):
        if self.selected_task:
            self._quick_pause(self.selected_task)

    def _remove(self):
        if self.selected_task:
            self._quick_delete(self.selected_task)

    def _check_clipboard(self):
        from PyQt6.QtWidgets import QApplication
        cb = QApplication.clipboard().text().strip()
        if cb.startswith("magnet:?"):
            r = QMessageBox.question(self, "Magnet Detected",
                f"Magnet link in clipboard:\n\n{cb[:100]}...\n\nDownload?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if r == QMessageBox.StandardButton.Yes:
                dlg = AddTorrentDialog(self)
                dlg.radio_magnet.setChecked(True)
                dlg._source_changed()
                dlg.txt_source.setText(cb)
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    is_magnet, source, dest = dlg.get_data()
                    if source:
                        seq, skip, bw, max_conn = False, False, 0, 50
                        if hasattr(dlg, "get_advanced_data"):
                            try:
                                s_seq, s_skip, s_bw, s_max_conn = dlg.get_advanced_data()
                                seq = s_seq
                                skip = s_skip
                                if s_bw.isdigit():
                                    bw = int(s_bw)
                                if s_max_conn.isdigit():
                                    max_conn = int(s_max_conn)
                            except Exception:
                                pass
                        self._process_magnet(source, dest, seq, skip, bw, max_conn)

    def _show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def _save_session(self):
        if hasattr(self, "session_manager") and self.session_manager:
            self.session_manager.save_session(self.manager.tasks)

    def _autosave_session(self):
        self._save_session()

    def _load_saved_session(self):
        from session_manager import SessionManager
        self.session_manager = SessionManager(self)
        
        session_data = self.session_manager.load_session()
        
        ui_state = session_data.get("ui_state", {})
        if ui_state:
            theme = ui_state.get("theme")
            if theme:
                self.change_theme(theme)
            accent = ui_state.get("accent_color")
            if accent:
                self.apply_custom_accent(accent)
                
            size = ui_state.get("window_size")
            if size and len(size) == 2:
                self.resize(size[0], size[1])
                
            widths = ui_state.get("column_widths")
            if widths:
                for i, w in enumerate(widths):
                    if i < self.table.columnCount():
                        self.table.setColumnWidth(i, w)
                        
            sidebar = ui_state.get("sidebar_state")
            if sidebar and sidebar in self.sidebar.items:
                self.sidebar._on_clicked(sidebar)
                    
            sorting = ui_state.get("sorting")
            if sorting and len(sorting) == 2:
                try:
                    section = sorting[0]
                    order_val = sorting[1]
                    if isinstance(order_val, int):
                        order = Qt.SortOrder(order_val)
                    elif hasattr(order_val, "value"):
                        order = Qt.SortOrder(order_val.value)
                    else:
                        order = Qt.SortOrder.AscendingOrder
                    self.table.horizontalHeader().setSortIndicator(section, order)
                except Exception:
                    pass
                
        torrents = session_data.get("torrents", [])
        missing_tasks = []
        
        for t_data in torrents:
            try:
                t_file = t_data.get("torrent_file")
                save_path = t_data.get("save_path")
                status = t_data.get("status")
                added_time = t_data.get("added_time")
                magnet_uri = t_data.get("magnet_uri")
                
                if t_file and not os.path.exists(t_file):
                    info_hash = t_data.get("info_hash")
                    if info_hash:
                        alt_path = os.path.join(self.session_manager.torrents_dir, f"{info_hash}.torrent")
                        if os.path.exists(alt_path):
                            t_file = alt_path
                
                if not magnet_uri and (not t_file or not os.path.exists(t_file)):
                    self.log(f"Warning: Torrent file not found for session entry: {t_file}")
                    continue
                
                seq = t_data.get("sequential", False)
                skip = t_data.get("skip_hash", False)
                max_conn = t_data.get("max_connections", 50)
                bw = t_data.get("bandwidth_limit", 0)

                task = self.manager.restore_torrent(
                    torrent_path=t_file,
                    save_dir=save_path,
                    status=status,
                    added_time=added_time,
                    magnet_uri=magnet_uri,
                    sequential=seq,
                    skip_hash=skip,
                    max_connections=max_conn,
                    bandwidth_limit=bw
                )
                
                if not task.is_magnet:
                    has_progress = task.manager and len(task.manager.completed) > 0
                    if has_progress and not os.path.exists(task.output_filename):
                        task.status = "Files Missing"
                        missing_tasks.append(task)
                    else:
                        if status in ("Downloading", "Checking", "Finding Peers...", "Connecting...", "Downloading Metadata..."):
                            task.status = "Stopped"
                            task.start()
                else:
                    if status in ("Downloading", "Checking", "Finding Peers...", "Connecting...", "Downloading Metadata..."):
                        task.status = "Stopped"
                        task.start()
            except Exception as e:
                self.log(f"Failed to restore torrent from session: {e}")
                    
        for task in self.manager.tasks:
            if not task.is_magnet:
                cc = len(task.manager.completed) if task.manager else 0
                pc = task.torrent.get_piece_count()
                if pc > 0 and cc >= pc:
                    task_key = task.torrent.get_info_hash()
                    self.notified_completions.add(task_key)
                    
        # Apply row selection for selected torrent
        selected_hash = ui_state.get("selected_torrent_hash")
        if selected_hash:
            filtered_tasks = self._filtered_tasks()
            for row in range(min(self.table.rowCount(), len(filtered_tasks))):
                t = filtered_tasks[row]
                if t.torrent and t.torrent.get_info_hash() == selected_hash:
                    self.table.selectRow(row)
                    self.selected_task = t
                    self._populate_files(t)
                    break

        for task in missing_tasks:
            self._handle_missing_files(task)
            
        self._refresh_table()
        
        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._autosave_session)
        self.autosave_timer.start(30000)

    def _handle_missing_files(self, task):
        from gui.files_missing_dialog import FilesMissingDialog
        name = task.torrent.get_name().decode('utf-8', errors='ignore')
        dlg = FilesMissingDialog(name, task.output_filename, self)
        
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg.action == "recheck":
                if task.manager:
                    with task.manager.completed_lock:
                        task.manager.completed.clear()
                    task.manager.save_progress()
                self.log(f"Rechecking/restarting torrent {name} from scratch...")
                task.status = "Stopped"
                task.start()
            elif dlg.action == "remove":
                self.log(f"Removing torrent {name} due to missing files.")
                self.manager.remove_torrent(task)
                if self.selected_task == task:
                    self.selected_task = None
                    self._clear_detail()
            elif dlg.action == "locate":
                chosen_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Locate Downloaded File",
                    os.path.dirname(task.output_filename),
                    "All Files (*)"
                )
                if chosen_path:
                    task.save_dir = os.path.dirname(chosen_path)
                    task.output_filename = chosen_path
                    if task.manager:
                        task.manager.output_file = chosen_path
                    self.log(f"Located file for {name} at {chosen_path}. Running integrity check...")
                    task.status = "Stopped"
                    task.start()
                else:
                    task.status = "Files Missing"
        else:
            task.status = "Files Missing"

    def _recheck_selected(self):
        if self.selected_task:
            task = self.selected_task
            name = task.torrent.get_name().decode('utf-8', errors='ignore')
            if task.manager:
                with task.manager.completed_lock:
                    task.manager.completed.clear()
                task.manager.save_progress()
            self.log(f"Force rechecking torrent {name} from scratch...")
            task.status = "Stopped"
            task.start()
            self._save_session()
            self._refresh_table()

    def _locate_selected(self):
        if self.selected_task:
            task = self.selected_task
            name = task.torrent.get_name().decode('utf-8', errors='ignore')
            chosen_path, _ = QFileDialog.getOpenFileName(
                self,
                "Locate Downloaded File",
                os.path.dirname(task.output_filename),
                "All Files (*)"
            )
            if chosen_path:
                task.save_dir = os.path.dirname(chosen_path)
                task.output_filename = chosen_path
                if task.manager:
                    task.manager.output_file = chosen_path
                self.log(f"Located file for {name} at {chosen_path}. Running integrity check...")
                task.status = "Stopped"
                task.start()
                self._save_session()
                self._refresh_table()

    def closeEvent(self, event):
        self.log("Closing. Saving session...")
        self._save_session()
        self.log("Stopping all tasks...")
        for task in self.manager.tasks:
            task.stop()
        event.accept()
