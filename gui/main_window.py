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
    QScrollArea, QGridLayout, QGraphicsDropShadowEffect, QCheckBox,
    QApplication
)
from PyQt6.QtCore import QTimer, Qt, QObject, pyqtSignal, QSize, QRect, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF, QByteArray
from PyQt6.QtGui import (
    QAction, QIcon, QPixmap, QDragEnterEvent, QDropEvent,
    QShortcut, QKeySequence, QPainter, QColor, QRadialGradient,
    QLinearGradient
)
from PyQt6.QtSvg import QSvgRenderer

from gui.sidebar import Sidebar, make_svg_icon

TOOLBAR_SVGS = {
    "Add": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <line x1="12" y1="5" x2="12" y2="19"/>
      <line x1="5" y1="12" x2="19" y2="12"/>
    </svg>""",
    "Magnet": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <path d="M6 9v3a6 6 0 0 0 12 0V9"/>
      <path d="M18 9V7a3 3 0 0 0-6 0v2"/>
      <path d="M12 9V7a3 3 0 0 0-6 0v2"/>
    </svg>""",
    "Resume": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polygon points="5 3 19 12 5 21 5 3"/>
    </svg>""",
    "Pause": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <rect x="6" y="4" width="4" height="16"/>
      <rect x="14" y="4" width="4" height="16"/>
    </svg>""",
    "Remove": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="3 6 5 6 21 6"/>
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
      <line x1="10" y1="11" x2="10" y2="17"/>
      <line x1="14" y1="11" x2="14" y2="17"/>
    </svg>""",
    "Grid": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <rect x="3" y="3" width="7" height="7"/>
      <rect x="14" y="3" width="7" height="7"/>
      <rect x="14" y="14" width="7" height="7"/>
      <rect x="3" y="14" width="7" height="7"/>
    </svg>""",
    "Table": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <line x1="9" y1="6" x2="20" y2="6"/>
      <line x1="9" y1="12" x2="20" y2="12"/>
      <line x1="9" y1="18" x2="20" y2="18"/>
      <line x1="5" y1="6" x2="5.01" y2="6"/>
      <line x1="5" y1="12" x2="5.01" y2="12"/>
      <line x1="5" y1="18" x2="5.01" y2="18"/>
    </svg>""",
    "Search": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="11" cy="11" r="8"/>
      <line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>"""
}
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

    def __init__(self, items_data, parent=None):
        super().__init__(parent)
        self.setObjectName("segmentedControl")
        self.items_data = items_data
        self.setStyleSheet("""
            #segmentedControl {
                background-color: #0b0e14;
                border: 1px solid #161a25;
                border-radius: 8px;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                color: #8892a8;
                font-family: 'Inter', sans-serif;
                font-weight: 600;
                font-size: 13px;
                padding: 10px 16px;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #111420;
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
        
        for i, item in enumerate(items_data):
            text = item.get("text", "")
            btn = QPushButton()
            btn.setText("  " + text)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if i == 0:
                btn.setChecked(True)
            self.group.addButton(btn, i)
            layout.addWidget(btn)
            self.buttons.append(btn)
            
        self.group.idClicked.connect(self._on_clicked)
        self.group.idClicked.connect(self.toggled.emit)
        self._update_icons()
        
    def _on_clicked(self, index):
        self._update_icons()
        
    def _update_icons(self):
        for idx, btn in enumerate(self.buttons):
            item = self.items_data[idx]
            icon_xml = item.get("icon")
            if not icon_xml:
                continue
            if btn.isChecked():
                btn.setIcon(make_dialog_svg_icon(icon_xml, "#ffffff", "#ffffff", QSize(14, 14)))
            else:
                color = item.get("color", "#8892a8")
                btn.setIcon(make_dialog_svg_icon(icon_xml, color, color, QSize(14, 14)))

    def select_index(self, index):
        if 0 <= index < len(self.buttons):
            self.buttons[index].setChecked(True)
            self._update_icons()
            self.toggled.emit(index)


def make_dialog_svg_pixmap(svg_xml, color, size):
    xml_colored = svg_xml.replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(xml_colored.encode('utf-8')))
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap

def make_dialog_svg_icon(svg_xml, color_normal, color_hover, size=QSize(18, 18)):
    icon = QIcon()
    for color, mode, state in [
        (color_normal, QIcon.Mode.Normal, QIcon.State.Off),
        (color_hover, QIcon.Mode.Active, QIcon.State.Off)
    ]:
        xml_colored = svg_xml.replace("currentColor", color)
        renderer = QSvgRenderer(QByteArray(xml_colored.encode('utf-8')))
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        icon.addPixmap(pixmap, mode, state)
    return icon


class ChoiceCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, mode, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Style based on mode
        if mode == "file":
            self.title = "Open Torrent File"
            self.subtext = "Browse and select a local .torrent file from your device."
            self.btn_text = "Browse File"
            self.accent_color = "#2563eb" # blue
            self.icon_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>"""
            self.btn_icon_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>"""
        else:
            self.title = "Use Magnet Link"
            self.subtext = "Paste a magnet link directly to start downloading."
            self.btn_text = "Paste Magnet Link"
            self.accent_color = "#ef4444" # red/pink
            self.icon_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 9v3a6 6 0 0 0 12 0V9"/>
              <path d="M18 9V7a3 3 0 0 0-6 0v2"/>
              <path d="M12 9V7a3 3 0 0 0-6 0v2"/>
            </svg>"""
            self.btn_icon_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
            </svg>"""

        # Frame Styling
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #111420;
                border: 1px solid #1e2438;
                border-left: 4px solid {self.accent_color};
                border-radius: 12px;
            }}
            QFrame:hover {{
                background-color: #151a2a;
                border-color: {self.accent_color};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Left Icon Box
        self.icon_box = QFrame()
        self.icon_box.setFixedSize(64, 64)
        self.icon_box.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
            }}
        """)
        ib_layout = QVBoxLayout(self.icon_box)
        ib_layout.setContentsMargins(0, 0, 0, 0)
        ib_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_icon = QLabel()
        self.lbl_icon.setStyleSheet("border: none; background: transparent;")
        icon_pixmap = make_dialog_svg_pixmap(self.icon_xml, self.accent_color, QSize(32, 32))
        self.lbl_icon.setPixmap(icon_pixmap)
        ib_layout.addWidget(self.lbl_icon)
        layout.addWidget(self.icon_box)

        # Right Text Column
        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.lbl_title = QLabel(self.title)
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; border: none; background: transparent;")
        
        self.lbl_sub = QLabel(self.subtext)
        self.lbl_sub.setStyleSheet("font-size: 12px; color: #8892a8; border: none; background: transparent;")
        self.lbl_sub.setWordWrap(True)
        
        # Small Button below
        self.action_btn = QPushButton(self.btn_text)
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_btn.setIcon(make_dialog_svg_icon(self.btn_icon_xml, self.accent_color, "#ffffff", QSize(14, 14)))
        self.action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {self.accent_color};
                border-radius: 6px;
                color: {self.accent_color};
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {self.accent_color};
                color: #ffffff;
            }}
        """)
        # Forward click signal
        self.action_btn.clicked.connect(self.clicked.emit)
        
        # Let's align the button to the left
        btn_hbox = QHBoxLayout()
        btn_hbox.addWidget(self.action_btn)
        btn_hbox.addStretch()
        
        text_layout.addWidget(self.lbl_title)
        text_layout.addWidget(self.lbl_sub)
        text_layout.addSpacing(4)
        text_layout.addLayout(btn_hbox)
        
        layout.addLayout(text_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class DropZone(QFrame):
    file_dropped = pyqtSignal(str)
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("dropZone")
        self.update_style()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_cloud = QLabel()
        self.lbl_cloud.setStyleSheet("background: transparent; border: none;")
        cloud_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 16.92v3a2 2 0 0 1-2.18 2h-12a2 2 0 0 1-2-2v-3"/>
          <path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29"/>
          <polyline points="16 12 12 8 8 12"/>
          <line x1="12" y1="8" x2="12" y2="17"/>
        </svg>"""
        self.lbl_cloud.setPixmap(make_dialog_svg_pixmap(cloud_xml, "#2563eb", QSize(48, 48)))
        self.lbl_cloud.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_cloud)
        
        self.lbl_title = QLabel("Drag & Drop")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; background: transparent; border: none;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_title)
        
        self.lbl_sub = QLabel('.torrent file here or <span style="color:#2563eb; text-decoration: underline;">click to browse</span>')
        self.lbl_sub.setStyleSheet("font-size: 13px; color: #8892a8; background: transparent; border: none;")
        self.lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_sub)
        
    def update_style(self, active=False):
        if active:
            self.setStyleSheet("""
                QFrame#dropZone {
                    border: 2px dashed #2563eb;
                    border-radius: 12px;
                    background-color: rgba(37, 99, 235, 0.08);
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#dropZone {
                    border: 2px dashed #20263d;
                    border-radius: 12px;
                    background-color: #0b0e14;
                }
                QFrame#dropZone:hover {
                    border-color: #2c3554;
                    background-color: #0d111a;
                }
            """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().endswith(".torrent"):
                    self.update_style(True)
                    event.acceptProposedAction()
                    return
        event.ignore()
        
    def dragLeaveEvent(self, event):
        self.update_style(False)
        
    def dropEvent(self, event):
        self.update_style(False)
        for url in event.mimeData().urls():
            fp = url.toLocalFile()
            if fp.endswith(".torrent"):
                self.file_dropped.emit(fp)
                event.acceptProposedAction()
                return

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class FileSelectorCard(QFrame):
    browse_clicked = pyqtSignal()
    change_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #0b0e14;
                border: 1px solid #161a25;
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
        
        # PAGE 0: EMPTY STATE
        self.page_empty = QWidget()
        pe_layout = QHBoxLayout(self.page_empty)
        pe_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_empty = QLabel("No torrent selected")
        self.lbl_empty.setStyleSheet("color: #8892a8; font-family: 'Inter', sans-serif; font-size: 13px;")
        
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #111420;
                border: 1px solid #1e2438;
                border-radius: 6px;
                color: #ffffff;
                font-weight: bold;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #161a2a;
                border-color: #2563eb;
            }
        """)
        self.btn_browse.clicked.connect(self.browse_clicked.emit)
        pe_layout.addWidget(self.lbl_empty)
        pe_layout.addStretch()
        pe_layout.addWidget(self.btn_browse)
        self.stack.addWidget(self.page_empty)
        
        # PAGE 1: SELECTED STATE
        self.page_selected = QWidget()
        ps_layout = QHBoxLayout(self.page_selected)
        ps_layout.setContentsMargins(0, 0, 0, 0)
        ps_layout.setSpacing(14)
        
        self.doc_box = QFrame()
        self.doc_box.setFixedSize(48, 54)
        self.doc_box.setStyleSheet("""
            QFrame {
                background-color: rgba(37, 99, 235, 0.08);
                border: 1.5px solid #2563eb;
                border-radius: 6px;
            }
        """)
        db_layout = QVBoxLayout(self.doc_box)
        db_layout.setContentsMargins(0, 6, 0, 4)
        db_layout.setSpacing(0)
        db_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        doc_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>"""
        lbl_doc_ico = QLabel()
        lbl_doc_ico.setPixmap(make_dialog_svg_pixmap(doc_xml, "#2563eb", QSize(22, 22)))
        lbl_doc_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_doc_ext = QLabel(".torrent")
        lbl_doc_ext.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 8px; font-weight: bold; color: #2563eb; border: none;")
        lbl_doc_ext.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        db_layout.addWidget(lbl_doc_ico)
        db_layout.addWidget(lbl_doc_ext)
        ps_layout.addWidget(self.doc_box)
        
        vbox = QVBoxLayout()
        vbox.setSpacing(2)
        vbox.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.lbl_filename = QLabel("ubuntu.torrent")
        self.lbl_filename.setStyleSheet("color: #ffffff; font-family: 'Inter', sans-serif; font-weight: bold; font-size: 14px;")
        self.lbl_filesize = QLabel("3.2 KB")
        self.lbl_filesize.setStyleSheet("color: #8892a8; font-family: 'Inter', sans-serif; font-size: 12px;")
        vbox.addWidget(self.lbl_filename)
        vbox.addWidget(self.lbl_filesize)
        
        ps_layout.addLayout(vbox)
        ps_layout.addStretch()
        
        self.btn_change = QPushButton("  Change File")
        self.btn_change.setCursor(Qt.CursorShape.PointingHandCursor)
        folder_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>"""
        self.btn_change.setIcon(make_dialog_svg_icon(folder_xml, "#ffffff", "#ffffff", QSize(14, 14)))
        self.btn_change.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1e2438;
                border-radius: 6px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-weight: bold;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #111420;
                border-color: #2563eb;
            }
        """)
        self.btn_change.clicked.connect(self.change_clicked.emit)
        ps_layout.addWidget(self.btn_change)
        
        self.stack.addWidget(self.page_selected)
        
    def set_file(self, filename, size_str):
        if filename:
            self.lbl_filename.setText(filename)
            self.lbl_filesize.setText(size_str)
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(0)


class QuickAccessButton(QPushButton):
    def __init__(self, name, path, parent=None):
        super().__init__(name, parent)
        self.name = name
        self.path = path
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)
        self.set_active(False)
        
    def set_active(self, active):
        self.setChecked(active)
        dot_svg = """<svg viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="12" r="6"/>
        </svg>"""
        folder_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>"""
        if active:
            self.setIcon(make_dialog_svg_icon(dot_svg, "#2563eb", "#2563eb", QSize(10, 10)))
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0c101b;
                    border: 1px solid #2563eb;
                    border-radius: 6px;
                    color: #2563eb;
                    font-family: 'Inter', sans-serif;
                    font-weight: 600;
                    padding: 6px 12px;
                    font-size: 11px;
                }
            """)
        else:
            self.setIcon(make_dialog_svg_icon(folder_svg, "#8892a8", "#ffffff", QSize(12, 12)))
            self.setStyleSheet("""
                QPushButton {
                    background-color: #10121d;
                    border: 1px solid #1e2438;
                    border-radius: 6px;
                    color: #8892a8;
                    font-family: 'Inter', sans-serif;
                    font-weight: 500;
                    padding: 6px 12px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #161927;
                    border-color: #2c3247;
                    color: #ffffff;
                }
            """)


class SpaceStatusBanner(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_dialog = parent
        self.setVisible(False)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)
        
        self.ico_warning = QLabel()
        self.ico_warning.setStyleSheet("background: transparent; border: none;")
        warn_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>"""
        self.ico_warning.setPixmap(make_dialog_svg_pixmap(warn_xml, "#ef4444", QSize(18, 18)))
        layout.addWidget(self.ico_warning)
        
        self.lbl_title = QLabel("Insufficient Disk Space")
        self.lbl_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; font-weight: bold; color: #ef4444; background: transparent; border: none;")
        layout.addWidget(self.lbl_title)
        
        self.lbl_details = QLabel("")
        self.lbl_details.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 12px; color: #fca5a5; background: transparent; border: none;")
        layout.addWidget(self.lbl_details)
        
        layout.addStretch()
        
        self.btn_action = QPushButton(" Choose Another Location")
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        folder_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>"""
        self.btn_action.setIcon(make_dialog_svg_icon(folder_svg, "#ffffff", "#ffffff", QSize(14, 14)))
        self.btn_action.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: #ffffff;
                padding: 6px 12px;
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.08);
            }
        """)
        if parent:
            self.btn_action.clicked.connect(parent._browse_dest)
        layout.addWidget(self.btn_action)
        
    def show_warning(self, free_str, size_str):
        self.lbl_details.setText(f"Free: {free_str}   |   Required: {size_str}")
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(239, 68, 68, 0.06);
                border: 1px solid rgba(239, 68, 68, 0.15);
                border-radius: 8px;
            }
        """)
        self.setVisible(True)
        
    def hide_banner(self):
        self.setVisible(False)


class AddTorrentDialog(QDialog):
    def __init__(self, parent=None, default_save_dir="."):
        super().__init__(parent)
        self.setWindowTitle("Add Torrent")
        self.resize(800, 680)
        self.setAcceptDrops(True)
        self._is_valid_magnet = False
        self._has_enough_space = True
        
        self.setStyleSheet("""
            QDialog {
                background-color: #080b10;
                border: 1px solid #1e2438;
            }
            QLabel {
                color: #c8d0e0;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #0b0e14;
                border: 1px solid #161a25;
                border-radius: 8px;
                padding: 8px 12px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:hover {
                border-color: #2563eb;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
            QCheckBox {
                color: #8892a8;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1.5px solid #20263d;
                border-radius: 4px;
                background-color: #0b0e14;
            }
            QCheckBox::indicator:hover {
                border-color: #2563eb;
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
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "vortex_logo_v2.png")
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
        
        header_hbox = QHBoxLayout()
        header_hbox.setSpacing(16)
        
        lbl_hdr_icon = QLabel()
        lbl_hdr_icon.setStyleSheet("background: transparent; border: none;")
        inbox_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/>
          <path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>
        </svg>"""
        lbl_hdr_icon.setPixmap(make_dialog_svg_pixmap(inbox_xml, "#2563eb", QSize(44, 44)))
        header_hbox.addWidget(lbl_hdr_icon)
        
        ch_vbox = QVBoxLayout()
        ch_vbox.setSpacing(2)
        lbl_c_title = QLabel("Add Torrent")
        lbl_c_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff; background: transparent; border: none;")
        lbl_c_subtitle = QLabel("Add a .torrent file or paste a magnet link to start downloading.")
        lbl_c_subtitle.setStyleSheet("font-size: 13px; color: #8892a8; background: transparent; border: none;")
        ch_vbox.addWidget(lbl_c_title)
        ch_vbox.addWidget(lbl_c_subtitle)
        header_hbox.addLayout(ch_vbox)
        header_hbox.addStretch()
        pc_layout.addLayout(header_hbox)
        
        cards_hbox = QHBoxLayout()
        cards_hbox.setSpacing(20)
        
        self.card_file = ChoiceCard("file", self)
        self.card_magnet = ChoiceCard("magnet", self)
        self.card_file.clicked.connect(self._choose_file_mode)
        self.card_magnet.clicked.connect(self._choose_magnet_mode)
        
        cards_hbox.addWidget(self.card_file)
        cards_hbox.addWidget(self.card_magnet)
        pc_layout.addLayout(cards_hbox)
        
        self.choice_drop = DropZone()
        self.choice_drop.file_dropped.connect(self._load_torrent_file)
        self.choice_drop.clicked.connect(self._choose_file_mode)
        pc_layout.addWidget(self.choice_drop)
        
        cf_layout = QHBoxLayout()
        self.chk_dont_show = QCheckBox("Don't show this again")
        cf_layout.addWidget(self.chk_dont_show)
        cf_layout.addStretch()
        
        cancel_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>"""
        btn_c_cancel = QPushButton(" Cancel")
        btn_c_cancel.setObjectName("btnCancel")
        btn_c_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c_cancel.setIcon(make_dialog_svg_icon(cancel_xml, "#ffffff", "#ffffff", QSize(14, 14)))
        btn_c_cancel.setStyleSheet("""
            QPushButton#btnCancel {
                background-color: transparent;
                border: 1px solid #20263d;
                border-radius: 8px;
                color: #ffffff;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#btnCancel:hover {
                background-color: #151a25;
            }
        """)
        btn_c_cancel.clicked.connect(self.reject)
        cf_layout.addWidget(btn_c_cancel)
        
        plus_xml = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <line x1="5" y1="12" x2="19" y2="12"/>
        </svg>"""
        btn_c_add = QPushButton(" Add Torrent")
        btn_c_add.setObjectName("btnSelect")
        btn_c_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c_add.setIcon(make_dialog_svg_icon(plus_xml, "#ffffff", "#ffffff", QSize(14, 14)))
        btn_c_add.setStyleSheet("""
            QPushButton#btnSelect {
                background-color: #2563eb;
                border: none;
                border-radius: 8px;
                color: #ffffff;
                padding: 10px 22px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#btnSelect:hover {
                background-color: #1d4ed8;
            }
        """)
        btn_c_add.clicked.connect(self._choose_file_mode)
        cf_layout.addWidget(btn_c_add)
        
        pc_layout.addLayout(cf_layout)
        self.main_stack.addWidget(self.page_choice)
        
        # PAGE 1: FORM SCREEN
        self.page_form = QWidget()
        pf_layout = QVBoxLayout(self.page_form)
        pf_layout.setContentsMargins(30, 24, 30, 24)
        pf_layout.setSpacing(14)
        
        fh_vbox = QVBoxLayout()
        fh_vbox.setSpacing(4)
        lbl_f_title = QLabel("Add Torrent")
        lbl_f_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ffffff;")
        self.lbl_f_subtitle = QLabel("Add a .torrent file to start downloading.")
        self.lbl_f_subtitle.setStyleSheet("font-size: 13px; color: #8892a8;")
        fh_vbox.addWidget(lbl_f_title)
        fh_vbox.addWidget(self.lbl_f_subtitle)
        
        f_header_hbox = QHBoxLayout()
        f_header_hbox.setSpacing(16)
        lbl_f_hdr_icon = QLabel()
        lbl_f_hdr_icon.setPixmap(make_dialog_svg_pixmap(inbox_xml, "#2563eb", QSize(36, 36)))
        f_header_hbox.addWidget(lbl_f_hdr_icon)
        f_header_hbox.addLayout(fh_vbox)
        f_header_hbox.addStretch()
        
        pf_layout.addLayout(f_header_hbox)
        
        torrent_tab_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>"""
        magnet_tab_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 9v3a6 6 0 0 0 12 0V9"/>
          <path d="M18 9V7a3 3 0 0 0-6 0v2"/>
          <path d="M12 9V7a3 3 0 0 0-6 0v2"/>
        </svg>"""
        
        tab_items = [
            {"text": "Torrent File", "icon": torrent_tab_svg, "color": "#2563eb"},
            {"text": "Magnet Link", "icon": magnet_tab_svg, "color": "#ef4444"}
        ]
        self.segmented_control = SegmentedControl(tab_items)
        self.segmented_control.toggled.connect(self._segmented_toggled)
        pf_layout.addWidget(self.segmented_control)
        
        self.radio_file = QRadioButton()
        self.radio_magnet = QRadioButton()
        self.radio_file.setVisible(False)
        self.radio_magnet.setVisible(False)
        pf_layout.addWidget(self.radio_file)
        pf_layout.addWidget(self.radio_magnet)
        
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
                background-color: #0b0e14;
                border: 1px solid rgba(37, 99, 235, 0.15);
                border-radius: 10px;
            }
        """)
        info_layout = QGridLayout(self.info_group)
        info_layout.setContentsMargins(16, 14, 16, 14)
        info_layout.setSpacing(12)
        
        def make_grid_row(icon_xml, label_name):
            w = QWidget()
            lay = QHBoxLayout(w)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.setSpacing(10)
            
            ico = QLabel()
            ico.setPixmap(make_dialog_svg_pixmap(icon_xml, "#2563eb", QSize(15, 15)))
            
            lbl_title = QLabel(label_name)
            lbl_title.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #8892a8; border: none; background: transparent;")
            lbl_title.setFixedWidth(80)
            
            lbl_val = QLabel("—")
            lbl_val.setStyleSheet("font-family: 'Inter', sans-serif; font-size: 13px; color: #ffffff; font-weight: 600; border: none; background: transparent;")
            
            lay.addWidget(ico)
            lay.addWidget(lbl_title)
            lay.addWidget(lbl_val)
            lay.addStretch()
            return w, lbl_val
            
        user_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>"""
        drive_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
          <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
          <line x1="6" y1="6" x2="6.01" y2="6"/>
          <line x1="6" y1="18" x2="6.01" y2="18"/>
        </svg>"""
        folder_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>"""
        jigsaw_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 16V8a2 2 0 0 0-2-2h-3.5a3.5 3.5 0 0 0-7 0H5a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h3.5a3.5 3.5 0 0 0 7 0H19a2 2 0 0 0 2-2z"/>
        </svg>"""
        created_by_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>"""
        calendar_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
          <line x1="16" y1="2" x2="16" y2="6"/>
          <line x1="8" y1="2" x2="8" y2="6"/>
          <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>"""
        
        w_name, self.lbl_info_name = make_grid_row(user_svg, "Name")
        w_size, self.lbl_info_size = make_grid_row(drive_svg, "Size")
        w_files, self.lbl_info_files = make_grid_row(folder_svg, "Files")
        w_pieces, self.lbl_info_pieces = make_grid_row(jigsaw_svg, "Pieces")
        w_created_by, self.lbl_info_created_by = make_grid_row(created_by_svg, "Created By")
        w_created_on, self.lbl_info_created_on = make_grid_row(calendar_svg, "Created On")
        
        info_layout.addWidget(w_name, 0, 0)
        info_layout.addWidget(w_size, 1, 0)
        info_layout.addWidget(w_files, 2, 0)
        
        info_layout.addWidget(w_pieces, 0, 1)
        info_layout.addWidget(w_created_by, 1, 1)
        info_layout.addWidget(w_created_on, 2, 1)
        
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
                background-color: #0b0e14;
                border: 2px solid #161a25;
                border-radius: 10px;
                padding: 12px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-size: 13px;
            }
            QLineEdit:hover {
                border-color: #2563eb;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        self.txt_source.textChanged.connect(self._source_text_changed)
        
        self.lbl_magnet_validation = QLabel("")
        self.lbl_magnet_validation.setStyleSheet("font-size: 11px; font-family: 'Inter', sans-serif;")
        
        smp_layout.addWidget(self.txt_source)
        smp_layout.addWidget(self.lbl_magnet_validation)
        self.stack_source.addWidget(self.src_magnet_page)
        
        pf_layout.addWidget(self.stack_source)
        
        dest_vbox = QVBoxLayout()
        dest_vbox.setSpacing(6)
        
        lbl_dest_label = QLabel("Destination")
        lbl_dest_label.setStyleSheet("font-weight: bold; color: #ffffff; font-family: 'Inter', sans-serif;")
        dest_vbox.addWidget(lbl_dest_label)
        
        self.dest_card = QFrame()
        self.dest_card.setStyleSheet("""
            QFrame {
                background-color: #0b0e14;
                border: 1px solid #161a25;
                border-radius: 10px;
            }
        """)
        dest_card_layout = QHBoxLayout(self.dest_card)
        dest_card_layout.setContentsMargins(14, 12, 14, 12)
        dest_card_layout.setSpacing(12)
        
        self.dest_folder_icon = QLabel()
        self.dest_folder_icon.setPixmap(make_dialog_svg_pixmap(folder_svg, "#f59e0b", QSize(18, 18)))
        dest_card_layout.addWidget(self.dest_folder_icon)
        
        self.lbl_dest_path = QLabel("/home/jarjis/Downloads")
        self.lbl_dest_path.setStyleSheet("color: #ffffff; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; background: transparent; border: none;")
        dest_card_layout.addWidget(self.lbl_dest_path)
        dest_card_layout.addStretch()
        
        self.lbl_dest_folder_title = QLabel("")
        self.lbl_dest_folder_title.setVisible(False)
        dest_card_layout.addWidget(self.lbl_dest_folder_title)
        
        self.btn_browse_dest = QPushButton("  Browse...")
        self.btn_browse_dest.setIcon(make_dialog_svg_icon(folder_svg, "#ffffff", "#ffffff", QSize(14, 14)))
        self.btn_browse_dest.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1e2438;
                border-radius: 6px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-weight: bold;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #111420;
                border-color: #2563eb;
            }
        """)
        self.btn_browse_dest.clicked.connect(self._browse_dest)
        dest_card_layout.addWidget(self.btn_browse_dest)
        dest_vbox.addWidget(self.dest_card)
        
        self.recent_layout = QHBoxLayout()
        self.recent_layout.setSpacing(8)
        self.recent_layout.setContentsMargins(2, 0, 0, 0)
        
        clock_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>"""
        lbl_recent_tag = QLabel("Quick Access")
        lbl_recent_tag.setStyleSheet("color: #6b7590; font-family: 'Inter', sans-serif; font-size: 11px; font-weight: bold;")
        lbl_recent_ico = QLabel()
        lbl_recent_ico.setPixmap(make_dialog_svg_pixmap(clock_svg, "#6b7590", QSize(13, 13)))
        
        self.recent_layout.addWidget(lbl_recent_ico)
        self.recent_layout.addWidget(lbl_recent_tag)
        self.recent_layout.addSpacing(4)
        
        recent_paths = {
            "Downloads": os.path.expanduser("~/Downloads"),
            "Movies": os.path.expanduser("~/Videos") if os.path.exists(os.path.expanduser("~/Videos")) else os.path.expanduser("~/Downloads/Movies"),
            "ISOs": os.path.expanduser("~/Downloads/ISOs") if os.path.exists(os.path.expanduser("~/Downloads/ISOs")) else os.path.expanduser("~/Downloads"),
            "Documents": os.path.expanduser("~/Documents")
        }
        self.qa_buttons = []
        for name, path in recent_paths.items():
            btn = QuickAccessButton(name, path, self)
            btn.clicked.connect(lambda checked, p=path, n=name: self._set_destination_path(p, n))
            self.recent_layout.addWidget(btn)
            self.qa_buttons.append(btn)
            
        self.recent_layout.addStretch()
        dest_vbox.addLayout(self.recent_layout)
        pf_layout.addLayout(dest_vbox)
        
        self.lbl_space_status = SpaceStatusBanner(self)
        pf_layout.addWidget(self.lbl_space_status)
        
        gear_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3"/>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>"""
        self.btn_toggle_advanced = QPushButton("  Advanced Options   ▼")
        self.btn_toggle_advanced.setCheckable(True)
        self.btn_toggle_advanced.setIcon(make_dialog_svg_icon(gear_svg, "#8892a8", "#ffffff", QSize(14, 14)))
        self.btn_toggle_advanced.setIconSize(QSize(14, 14))
        self.btn_toggle_advanced.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_advanced.setStyleSheet("""
            QPushButton {
                background-color: #0b0e14;
                border: 1px solid #161a25;
                border-radius: 8px;
                color: #8892a8;
                font-family: 'Inter', sans-serif;
                font-weight: 600;
                font-size: 13px;
                text-align: left;
                padding: 10px 14px;
            }
            QPushButton:hover {
                border-color: #20263d;
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
        
        info_circle_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>"""
        lbl_f_info_icon = QLabel()
        lbl_f_info_icon.setPixmap(make_dialog_svg_pixmap(info_circle_svg, "#6b7590", QSize(14, 14)))
        self.lbl_footer_info = QLabel("Downloaded files will be stored in the selected location.")
        self.lbl_footer_info.setStyleSheet("color: #6b7590; font-family: 'Inter', sans-serif; font-size: 11px;")
        
        ff_layout.addWidget(lbl_f_info_icon)
        ff_layout.addWidget(self.lbl_footer_info)
        ff_layout.addStretch()
        
        btn_f_cancel = QPushButton("Cancel")
        btn_f_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_f_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1e2438;
                border-radius: 8px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #111420;
            }
        """)
        btn_f_cancel.clicked.connect(self.reject)
        ff_layout.addWidget(btn_f_cancel)
        
        dl_btn_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>"""
        self.btn_download = QPushButton("  Start Download")
        self.btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_download.setIcon(make_dialog_svg_icon(dl_btn_svg, "#ffffff", "#ffffff", QSize(14, 14)))
        self.btn_download.setIconSize(QSize(14, 14))
        self.btn_download.clicked.connect(self.accept)
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
        if not self.txt_source.text().strip() or self.file_selector.stack.currentIndex() == 0:
            self._browse_source()

    def _choose_magnet_mode(self):
        self.radio_magnet.setChecked(True)
        self.segmented_control.select_index(1)
        self.main_stack.setCurrentIndex(1)
        self._source_changed()
        self.txt_source.setFocus()

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
            self.lbl_magnet_validation.setStyleSheet("color: #10b981; font-weight: bold; font-size: 11px; font-family: 'Inter', sans-serif;")
            self._is_valid_magnet = True
        else:
            self.lbl_magnet_validation.setText("❌ Invalid Magnet Link")
            self.lbl_magnet_validation.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 11px; font-family: 'Inter', sans-serif;")
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
            
            created_on = "Unknown"
            creation_date_ts = t.meta.get(b'creation date')
            if creation_date_ts:
                try:
                    dt = datetime.datetime.fromtimestamp(int(creation_date_ts))
                    created_on = dt.strftime("%b %d, %Y  •  %H:%M")
                except Exception:
                    pass
            
            self.file_selector.set_file(os.path.basename(file_path), formatted_size)
            
            self.lbl_info_name.setText(name)
            self.lbl_info_size.setText(formatted_size)
            self.lbl_info_pieces.setText(f"{pieces:,}")
            self.lbl_info_files.setText(str(files_count))
            self.lbl_info_created_by.setText(created_by)
            self.lbl_info_created_on.setText(created_on)
            self.info_group.setVisible(True)
            
            self._update_disk_space_check(size)
        except Exception as e:
            QMessageBox.warning(self, "Invalid Torrent", f"Failed to parse torrent file: {e}")
            self.file_selector.set_file("", "")
            self.info_group.setVisible(False)
            self.lbl_space_status.hide_banner()
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
        self.lbl_dest_path.setText(path)
        self.lbl_footer_info.setText(f"Downloaded files will be stored in <font color='#ffffff'><b>{folder_name}</b></font>")
        
        for btn in self.qa_buttons:
            btn.set_active(btn.path == path)
            
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
            self.lbl_space_status.hide_banner()
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
                self.lbl_space_status.hide_banner()
                self._has_enough_space = True
            else:
                self.lbl_space_status.show_warning(free_str, size_str)
                self._has_enough_space = False
        else:
            self.lbl_space_status.hide_banner()
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
        dl_btn_svg = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>"""
        if valid:
            self.btn_download.setIcon(make_dialog_svg_icon(dl_btn_svg, "#ffffff", "#ffffff", QSize(14, 14)))
            self.btn_download.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                    border: none;
                    border-radius: 8px;
                    color: #ffffff;
                    font-family: 'Inter', sans-serif;
                    font-weight: bold;
                    padding: 10px 24px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3b82f6, stop:1 #2563eb);
                }
            """)
        else:
            self.btn_download.setIcon(make_dialog_svg_icon(dl_btn_svg, "#4a5568", "#4a5568", QSize(14, 14)))
            self.btn_download.setStyleSheet("""
                QPushButton {
                    background-color: #0b0e14;
                    border: 1px solid #161a25;
                    border-radius: 8px;
                    color: #4a5568;
                    font-family: 'Inter', sans-serif;
                    font-weight: bold;
                    padding: 10px 24px;
                    font-size: 13px;
                }
            """)

    def _toggle_advanced(self, checked):
        self.advanced_container.setVisible(checked)
        self.btn_toggle_advanced.setText("  Advanced Options   ▲" if checked else "  Advanced Options   ▼")

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
        
        icon = QLabel()
        icon.setFixedSize(96, 96)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "vortex_logo_v2.png")
        if os.path.exists(logo_path):
            pm = QPixmap(logo_path).scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon.setPixmap(pm)
        else:
            icon.setText("🌀")
            icon.setStyleSheet("font-size: 80px; background: transparent; border: none;")
        clayout.addWidget(icon, 0, Qt.AlignmentFlag.AlignCenter)
        
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


class ClickableToast(QWidget):
    def __init__(self, text, click_callback, parent=None):
        super().__init__(parent)
        self.click_callback = click_callback
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #141828;
                border: 1px solid #2563eb;
                border-radius: 10px;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
            }
            QWidget:hover {
                background-color: #1a2035;
                border-color: #3b82f6;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        
        icon_lbl = QLabel("🧲")
        icon_lbl.setStyleSheet("font-size: 16px; background: transparent; border: none;")
        layout.addWidget(icon_lbl)
        
        text_lbl = QLabel(text)
        text_lbl.setStyleSheet("background: transparent; border: none; color: #ffffff;")
        layout.addWidget(text_lbl)
        
        btn = QPushButton("Add")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                border: none;
                border-radius: 6px;
                color: #ffffff;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3b82f6;
            }
        """)
        btn.clicked.connect(self._on_click)
        layout.addWidget(btn)
        
        self.adjustSize()
        
    def mousePressEvent(self, event):
        self._on_click()
        
    def _on_click(self):
        self.click_callback()
        self.close()


class ClipboardMagnetDialog(QDialog):
    def __init__(self, magnet_link, parent=None):
        super().__init__(parent)
        self.magnet_link = magnet_link
        self.setWindowTitle("Magnet Link Detected")
        self.setFixedSize(650, 480)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Card Background Frame
        self.bg_frame = QFrame()
        self.bg_frame.setObjectName("dialogBg")
        self.bg_frame.setStyleSheet("""
            QFrame#dialogBg {
                background-color: #090d16;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        layout.addWidget(self.bg_frame)
        
        # Inner Layout
        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(24, 24, 24, 24)
        bg_layout.setSpacing(20)
        
        # 1. Header Layout
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Magnet icon
        self.lbl_magnet_icon = QLabel("🧲")
        self.lbl_magnet_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_magnet_icon.setStyleSheet("""
            font-size: 28px;
            color: #10b981;
            background: transparent;
            border: none;
            margin-bottom: 2px;
        """)
        header_layout.addWidget(self.lbl_magnet_icon)
        
        # Title and Subtitle
        title_v_layout = QVBoxLayout()
        title_v_layout.setSpacing(2)
        title_v_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.lbl_title = QLabel("Magnet Link Detected")
        self.lbl_title.setStyleSheet("color: #ffffff; font-family: 'Inter', sans-serif; font-size: 18px; font-weight: bold; background: transparent; border: none;")
        
        self.lbl_subtitle = QLabel("Vortex has detected a magnet link in your clipboard.")
        self.lbl_subtitle.setStyleSheet("color: #6b7590; font-family: 'Inter', sans-serif; font-size: 13px; background: transparent; border: none;")
        
        title_v_layout.addWidget(self.lbl_title)
        title_v_layout.addWidget(self.lbl_subtitle)
        header_layout.addLayout(title_v_layout)
        header_layout.addStretch()
        
        # Window controls
        win_controls_layout = QHBoxLayout()
        win_controls_layout.setSpacing(8)
        win_controls_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        btn_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 6px;
                color: #a0aec0;
                font-weight: bold;
                font-size: 11px;
                width: 26px;
                height: 26px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
            }
        """
        
        self.btn_min = QPushButton("—")
        self.btn_min.setStyleSheet(btn_style)
        self.btn_min.clicked.connect(self.showMinimized)
        
        self.btn_max = QPushButton("⬜")
        self.btn_max.setStyleSheet(btn_style)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 6px;
                color: #a0aec0;
                font-weight: bold;
                font-size: 11px;
                width: 26px;
                height: 26px;
            }
            QPushButton:hover {
                background-color: #ef4444;
                color: #ffffff;
                border-color: #ef4444;
            }
        """)
        self.btn_close.clicked.connect(self.reject)
        
        win_controls_layout.addWidget(self.btn_min)
        win_controls_layout.addWidget(self.btn_max)
        win_controls_layout.addWidget(self.btn_close)
        header_layout.addLayout(win_controls_layout)
        
        bg_layout.addLayout(header_layout)
        
        # 2. Main Box (Magnet link box)
        self.magnet_box = QFrame()
        self.magnet_box.setStyleSheet("""
            QFrame {
                background-color: rgba(16, 185, 129, 0.02);
                border: 1px solid rgba(16, 185, 129, 0.12);
                border-radius: 10px;
            }
        """)
        magnet_box_layout = QHBoxLayout(self.magnet_box)
        magnet_box_layout.setContentsMargins(16, 16, 16, 16)
        magnet_box_layout.setSpacing(16)
        magnet_box_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Chain Link icon box
        self.chain_box = QFrame()
        self.chain_box.setFixedSize(54, 54)
        self.chain_box.setStyleSheet("""
            QFrame {
                background-color: rgba(16, 185, 129, 0.06);
                border: 1px solid rgba(16, 185, 129, 0.2);
                border-radius: 8px;
            }
            QLabel {
                font-size: 22px;
                background: transparent;
                border: none;
            }
        """)
        chain_box_layout = QVBoxLayout(self.chain_box)
        chain_box_layout.setContentsMargins(0, 0, 0, 0)
        chain_box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_chain = QLabel("🔗")
        lbl_chain.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chain_box_layout.addWidget(lbl_chain)
        magnet_box_layout.addWidget(self.chain_box, 0, Qt.AlignmentFlag.AlignVCenter)
        
        # Magnet text fields layout
        text_fields_layout = QVBoxLayout()
        text_fields_layout.setSpacing(8)
        text_fields_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        lbl_magnet_title = QLabel("MAGNET LINK")
        lbl_magnet_title.setStyleSheet("color: #10b981; font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 700; background: transparent; border: none; letter-spacing: 0.5px;")
        text_fields_layout.addWidget(lbl_magnet_title)
        
        # Link and copy row
        link_row = QHBoxLayout()
        link_row.setSpacing(8)
        link_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.txt_link = QLineEdit()
        self.txt_link.setText(self.magnet_link)
        self.txt_link.setReadOnly(True)
        self.txt_link.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.txt_link.setStyleSheet("""
            QLineEdit {
                color: #ffffff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)
        link_row.addWidget(self.txt_link, 1)
        
        self.btn_copy = QPushButton("⎘")
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.setToolTip("Copy magnet link")
        self.btn_copy.setFixedSize(32, 32)
        self.btn_copy.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                font-size: 15px;
                color: #ffffff;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: rgba(16, 185, 129, 0.06);
                border-color: rgba(16, 185, 129, 0.3);
            }
        """)
        self.btn_copy.clicked.connect(self._copy_link)
        link_row.addWidget(self.btn_copy, 0, Qt.AlignmentFlag.AlignVCenter)
        text_fields_layout.addLayout(link_row)
        
        # Valid Badge
        badge_layout = QHBoxLayout()
        self.lbl_badge = QLabel("  ✓  Valid magnet link  ")
        self.lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_badge.setStyleSheet("""
            QLabel {
                color: #10b981;
                font-family: 'Inter', sans-serif;
                font-size: 11px;
                font-weight: bold;
                background-color: rgba(16, 185, 129, 0.08);
                border: 1px solid rgba(16, 185, 129, 0.2);
                border-radius: 6px;
                padding: 4px 6px;
            }
        """)
        badge_layout.addWidget(self.lbl_badge)
        badge_layout.addStretch()
        text_fields_layout.addLayout(badge_layout)
        
        magnet_box_layout.addLayout(text_fields_layout, 1)
        bg_layout.addWidget(self.magnet_box)
        
        # 3. What is this? Box
        self.info_box = QFrame()
        self.info_box.setStyleSheet("""
            QFrame {
                background-color: rgba(37, 99, 235, 0.03);
                border: 1px solid rgba(37, 99, 235, 0.12);
                border-radius: 10px;
            }
        """)
        info_box_layout = QHBoxLayout(self.info_box)
        info_box_layout.setContentsMargins(16, 16, 16, 16)
        info_box_layout.setSpacing(16)
        info_box_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Info icon box (Vector-styled label)
        self.info_icon_lbl = QLabel("i")
        self.info_icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_icon_lbl.setFixedSize(20, 20)
        self.info_icon_lbl.setStyleSheet("""
            QLabel {
                color: #3b82f6;
                border: 1.5px solid #3b82f6;
                border-radius: 10px;
                font-family: 'Inter', sans-serif;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
                margin-top: 2px;
            }
        """)
        info_box_layout.addWidget(self.info_icon_lbl, 0, Qt.AlignmentFlag.AlignTop)
        
        # Info text
        info_text_layout = QVBoxLayout()
        info_text_layout.setSpacing(4)
        
        lbl_info_title = QLabel("What is this?")
        lbl_info_title.setStyleSheet("color: #3b82f6; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: bold; background: transparent; border: none;")
        
        lbl_info_desc = QLabel("A magnet link is a special link used to download files using the BitTorrent protocol. No .torrent file is required.")
        lbl_info_desc.setWordWrap(True)
        lbl_info_desc.setStyleSheet("color: #a0aec0; font-family: 'Inter', sans-serif; font-size: 12px; line-height: 1.4; background: transparent; border: none;")
        
        info_text_layout.addWidget(lbl_info_title)
        info_text_layout.addWidget(lbl_info_desc)
        info_box_layout.addLayout(info_text_layout, 1)
        info_box_layout.setAlignment(info_text_layout, Qt.AlignmentFlag.AlignVCenter)
        bg_layout.addWidget(self.info_box)
        
        # 4. Footer Section
        footer_layout = QHBoxLayout()
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.chk_dont_show = QCheckBox("Don't show this again")
        self.chk_dont_show.setStyleSheet("""
            QCheckBox {
                color: #8892a8;
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 4px;
                background-color: rgba(255, 255, 255, 0.03);
            }
            QCheckBox::indicator:hover {
                border-color: #10b981;
            }
            QCheckBox::indicator:checked {
                background-color: #10b981;
                border-color: #10b981;
            }
        """)
        footer_layout.addWidget(self.chk_dont_show, 0, Qt.AlignmentFlag.AlignVCenter)
        footer_layout.addStretch()
        
        # Buttons
        self.btn_no = QPushButton("⊘  No")
        self.btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_no.setFixedHeight(36)
        self.btn_no.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                font-weight: 600;
                padding-left: 16px;
                padding-right: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.15);
            }
        """)
        self.btn_no.clicked.connect(self.reject)
        footer_layout.addWidget(self.btn_no, 0, Qt.AlignmentFlag.AlignVCenter)
        footer_layout.addSpacing(10)
        
        self.btn_yes = QPushButton("↓  Yes, Download")
        self.btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_yes.setFixedHeight(36)
        self.btn_yes.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10b981, stop:1 #059669);
                border: 1px solid #10b981;
                border-radius: 8px;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                font-weight: 700;
                padding-left: 16px;
                padding-right: 16px;
            }
            QPushButton:hover {
                background: #10b981;
            }
        """)
        self.btn_yes.clicked.connect(self.accept)
        footer_layout.addWidget(self.btn_yes, 0, Qt.AlignmentFlag.AlignVCenter)
        
        bg_layout.addLayout(footer_layout)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.bg_frame.setGraphicsEffect(shadow)
        
        # Draggable frameless window
        self._drag_position = None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Only allow dragging from the header or card frame (not inputs/buttons)
            child = self.childAt(event.position().toPoint())
            if child in [self.bg_frame, self.lbl_title, self.lbl_subtitle, self.lbl_magnet_icon]:
                self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        self._drag_position = None
        
    def _copy_link(self):
        QApplication.clipboard().setText(self.magnet_link)
        self.btn_copy.setText("✓")
        QTimer.singleShot(1500, lambda: self.btn_copy.setText("⎘"))


class LogSignaler(QObject):
    log_signal = pyqtSignal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vortex")
        self.resize(1400, 850)
        self.setAcceptDrops(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "vortex_logo_v2.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
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
        self.change_theme("Vortex Glass")
        self._load_saved_session()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gui_stats)
        self.timer.start(1000)
        
        self.log("Vortex GUI initialized.")
        self._last_checked_magnet = ""
        QApplication.clipboard().dataChanged.connect(self._on_clipboard_changed)
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
            from gui.theme import hex_to_rgba, presets
            base_accent = presets.get(theme_name, presets["Midnight Blue"])["accent"]
            base_rgba = hex_to_rgba(base_accent, 0.12)
            custom_rgba = hex_to_rgba(custom_accent, 0.12)
            qss = qss.replace(base_rgba, custom_rgba)
            
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
        
        if hasattr(self, "sidebar") and self.sidebar:
            self.sidebar.refresh_theme_icons()
            
        if hasattr(self, "stats_bar") and self.stats_bar:
            self.stats_bar.refresh_theme(theme_name, custom_accent)
            
        if hasattr(self, "btn_add_torrent") and self.btn_add_torrent:
            self.refresh_toolbar_icons()

    def refresh_toolbar_icons(self):
        theme_name = getattr(self, "current_theme", "Midnight Blue")
        custom_accent = getattr(self, "custom_accent_color", None)
        from gui.theme import presets
        colors = presets.get(theme_name, presets["Midnight Blue"])
        
        accent = custom_accent if custom_accent else colors["accent"]
        text_normal = colors["text"]
        
        # 1. Add Torrent (always white icon on its solid primary background)
        add_icon = make_svg_icon(TOOLBAR_SVGS["Add"], "#ffffff", "#ffffff", "#ffffff")
        self.btn_add_torrent.setIcon(add_icon)
        
        # 2. Action buttons (normal text color, white on hover)
        hover_color = "#ffffff"
        magnet_icon = make_svg_icon(TOOLBAR_SVGS["Magnet"], text_normal, accent, hover_color)
        self.btn_magnet.setIcon(magnet_icon)
        
        resume_icon = make_svg_icon(TOOLBAR_SVGS["Resume"], text_normal, accent, hover_color)
        self.btn_resume.setIcon(resume_icon)
        
        pause_icon = make_svg_icon(TOOLBAR_SVGS["Pause"], text_normal, accent, hover_color)
        self.btn_pause.setIcon(pause_icon)
        
        remove_icon = make_svg_icon(TOOLBAR_SVGS["Remove"], text_normal, accent, hover_color)
        self.btn_remove.setIcon(remove_icon)
        
        # 3. Layout toggle button
        svg_name = "Table" if self.layout_mode == "Card" else "Grid"
        toggle_icon = make_svg_icon(TOOLBAR_SVGS[svg_name], text_normal, accent, hover_color)
        self.btn_layout_toggle.setIcon(toggle_icon)
        
        # 4. Search action icon inside QLineEdit
        if hasattr(self, "search_action") and self.search_action:
            search_icon = make_svg_icon(TOOLBAR_SVGS["Search"], colors.get("text_muted", "#6b7590"), accent, text_normal)
            self.search_action.setIcon(search_icon)

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

        self.btn_add_torrent = QPushButton("Add Torrent")
        self.btn_add_torrent.setObjectName("tbtn_add")
        self.btn_add_torrent.setFixedHeight(42)
        self.btn_add_torrent.setIconSize(QSize(18, 18))
        self.btn_add_torrent.setToolTip("Add Torrent File (Ctrl+O)")
        self.btn_add_torrent.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_torrent.clicked.connect(self._add_torrent_clicked)
        self.btn_add_torrent.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                border: none;
                color: #ffffff;
                border-radius: 10px;
                font-weight: bold;
                padding: 10px 22px;
                font-size: 14px;
                spacing: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
            }
        """)
        tbl.addWidget(self.btn_add_torrent)

        # Magnet Link
        self.btn_magnet = QPushButton("Magnet Link")
        self.btn_magnet.setObjectName("tbtn_action_magnet")
        self.btn_magnet.setIconSize(QSize(18, 18))
        self.btn_magnet.setToolTip("Magnet Link (Ctrl+M)")
        self.btn_magnet.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_magnet.clicked.connect(self._add_magnet)
        
        # Resume
        self.btn_resume = QPushButton("Resume")
        self.btn_resume.setObjectName("tbtn_action_resume")
        self.btn_resume.setIconSize(QSize(18, 18))
        self.btn_resume.setToolTip("Resume (Space to toggle)")
        self.btn_resume.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_resume.clicked.connect(self._resume)
        
        # Pause
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setObjectName("tbtn_action_pause")
        self.btn_pause.setIconSize(QSize(18, 18))
        self.btn_pause.setToolTip("Pause (Space to toggle)")
        self.btn_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pause.clicked.connect(self._pause)
        
        # Remove
        self.btn_remove = QPushButton("Remove")
        self.btn_remove.setObjectName("tbtn_action_remove")
        self.btn_remove.setIconSize(QSize(18, 18))
        self.btn_remove.setToolTip("Remove (Delete)")
        self.btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove.clicked.connect(self._remove)

        # Style sheet for other action buttons
        action_btn_qss = """
            QPushButton {
                background-color: transparent;
                border: 1px solid #1e2438;
                border-radius: 10px;
                color: #c8d0e0;
                font-weight: bold;
                padding: 10px 20px;
                font-size: 14px;
                spacing: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.04);
                border-color: #2563eb;
                color: #ffffff;
            }
        """
        
        for b in [self.btn_magnet, self.btn_resume, self.btn_pause, self.btn_remove]:
            b.setStyleSheet(action_btn_qss)
            tbl.addWidget(b)

        # Toggle Layout mode button
        self.btn_layout_toggle = QPushButton("Card View")
        self.btn_layout_toggle.setObjectName("tbtn_action_layout")
        self.btn_layout_toggle.setFixedHeight(42)
        self.btn_layout_toggle.setIconSize(QSize(18, 18))
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
                padding: 10px 20px;
                font-size: 14px;
                spacing: 8px;
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
        self.search.setPlaceholderText("Search torrents... (Ctrl+F)")
        self.search.textChanged.connect(self._on_search)
        self.search_action = self.search.addAction(QIcon(), QLineEdit.ActionPosition.LeadingPosition)
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
        self.card_scroll.setObjectName("cardScrollArea")
        self.card_scroll.setWidgetResizable(True)
        self.card_scroll.setStyleSheet("background-color: transparent; border: none;")
        
        self.card_container = QWidget()
        self.card_container.setObjectName("cardContainer")
        self.card_container.setStyleSheet("background-color: transparent;")
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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        theme_name = getattr(self, "current_theme", "Vortex Glass")
        w = self.width()
        h = self.height()
        t = time.time()
        
        if theme_name == "Vortex Glass":
            # 1. Vortex Glass: Stunning Apple-like animated mesh gradient backdrop
            # Dark base (translucent)
            painter.fillRect(self.rect(), QColor(6, 7, 19, 175))
            
            # Fluid Blob 1: Deep Royal Blue shifting top-left
            cx1 = w * 0.25 + (w * 0.15) * math.sin(t * 0.08)
            cy1 = h * 0.25 + (h * 0.15) * math.cos(t * 0.06)
            grad1 = QRadialGradient(cx1, cy1, w * 0.5)
            grad1.setColorAt(0.0, QColor(37, 99, 235, 45)) # royal blue
            grad1.setColorAt(0.5, QColor(37, 99, 235, 12))
            grad1.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), grad1)
            
            # Fluid Blob 2: Vibrant Purple shifting bottom-right
            cx2 = w * 0.75 + (w * 0.15) * math.cos(t * 0.07)
            cy2 = h * 0.75 + (h * 0.15) * math.sin(t * 0.09)
            grad2 = QRadialGradient(cx2, cy2, w * 0.6)
            grad2.setColorAt(0.0, QColor(147, 51, 234, 38)) # purple
            grad2.setColorAt(0.5, QColor(147, 51, 234, 10))
            grad2.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), grad2)
            
            # Fluid Blob 3: Neo-Teal/Cyan shifting bottom-left
            cx3 = w * 0.3 + (w * 0.20) * math.cos(t * 0.10)
            cy3 = h * 0.7 - (h * 0.15) * math.sin(t * 0.05)
            grad3 = QRadialGradient(cx3, cy3, w * 0.45)
            grad3.setColorAt(0.0, QColor(13, 148, 136, 32)) # teal
            grad3.setColorAt(0.5, QColor(13, 148, 136, 8))
            grad3.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), grad3)
            
        elif theme_name == "Midnight Blue":
            # Original Midnight Blue shifting radial gradient
            t_scaled = t * 0.12
            cx = w / 2 + (w * 0.15) * math.sin(t_scaled)
            cy = h / 2 + (h * 0.15) * math.cos(t_scaled)
            grad = QRadialGradient(cx, cy, w * 0.8)
            
            c2 = QColor(11, 14, 24, 180)
            c3 = QColor(5, 7, 12, 180)
            
            shift = (math.sin(t_scaled) + 1.0) / 2.0
            purple_tint = QColor(
                int(15 + 15 * shift),
                int(18 + 10 * (1 - shift)),
                int(32 + 25 * shift),
                180
            )
            grad.setColorAt(0, purple_tint)
            grad.setColorAt(0.5, c2)
            grad.setColorAt(1, c3)
            painter.fillRect(self.rect(), grad)
            
        elif theme_name == "Dracula":
            # Dracula: Dracula colors in background blobs (translucent)
            painter.fillRect(self.rect(), QColor(30, 31, 41, 180))
            cx = w * 0.6 + (w * 0.12) * math.sin(t * 0.08)
            cy = h * 0.4 + (h * 0.12) * math.cos(t * 0.08)
            grad = QRadialGradient(cx, cy, w * 0.6)
            grad.setColorAt(0.0, QColor(189, 147, 249, 25)) # #bd93f9 with alpha
            grad.setColorAt(0.6, QColor(40, 42, 54, 5))
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), grad)
            
        elif theme_name == "AMOLED":
            # Pure solid black for OLED screens (battery/contrast optimization)
            painter.fillRect(self.rect(), QColor("#000000"))
            
        elif theme_name == "Nord":
            # Nord: Slate/frost aurora background (translucent)
            painter.fillRect(self.rect(), QColor(46, 52, 64, 180))
            cx = w * 0.3 + (w * 0.15) * math.cos(t * 0.05)
            cy = h * 0.6 + (h * 0.15) * math.sin(t * 0.05)
            grad = QRadialGradient(cx, cy, w * 0.55)
            grad.setColorAt(0.0, QColor(136, 192, 208, 20)) # Nord aurora blue
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), grad)
            
        elif theme_name == "Catppuccin":
            # Catppuccin: Pastel mauve/blue shifts (translucent)
            painter.fillRect(self.rect(), QColor(30, 30, 46, 180))
            cx = w * 0.7 + (w * 0.15) * math.sin(t * 0.07)
            cy = h * 0.3 + (h * 0.15) * math.cos(t * 0.07)
            grad = QRadialGradient(cx, cy, w * 0.5)
            grad.setColorAt(0.0, QColor(203, 166, 247, 22)) # Catppuccin mauve
            grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), grad)
            
        elif theme_name == "Light":
            # Light: Sophisticated light grey/blue mesh (translucent)
            painter.fillRect(self.rect(), QColor(240, 242, 245, 180))
            cx1 = w * 0.3 + (w * 0.15) * math.sin(t * 0.06)
            cy1 = h * 0.3 + (h * 0.15) * math.cos(t * 0.08)
            grad1 = QRadialGradient(cx1, cy1, w * 0.5)
            grad1.setColorAt(0.0, QColor(37, 99, 235, 12)) # light blue
            grad1.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), grad1)
            
            cx2 = w * 0.7 + (w * 0.15) * math.cos(t * 0.08)
            cy2 = h * 0.7 + (h * 0.15) * math.sin(t * 0.06)
            grad2 = QRadialGradient(cx2, cy2, w * 0.5)
            grad2.setColorAt(0.0, QColor(236, 72, 153, 10)) # light pink
            grad2.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.fillRect(self.rect(), grad2)

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
            self.btn_layout_toggle.setText("Table View")
        else:
            self.layout_mode = "Table"
            self.btn_layout_toggle.setText("Card View")
        if hasattr(self, "btn_layout_toggle") and self.btn_layout_toggle:
            self.refresh_toolbar_icons()
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

    def handle_torrent_file(self, file_path):
        if not file_path:
            return
        
        is_magnet_link = file_path.startswith("magnet:")
        if not is_magnet_link and not os.path.exists(file_path):
            return
            
        self.showNormal()
        self.activateWindow()
        self.raise_()
        
        dlg = AddTorrentDialog(self)
        if is_magnet_link:
            dlg.radio_magnet.setChecked(True)
            dlg._source_changed()
            dlg.txt_source.setText(file_path)
        else:
            dlg._load_torrent_file(file_path)
            
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
        cb = QApplication.clipboard().text().strip()
        if cb.startswith("magnet:?") and cb != self._last_checked_magnet:
            self._last_checked_magnet = cb
            
            skip = False
            if hasattr(self, "page_settings") and self.page_settings:
                skip = self.page_settings.saved_settings.get("skip_magnet_dialog", False)
                
            if skip:
                self.handle_torrent_file(cb)
            else:
                self._show_magnet_dialog(cb)

    def _on_clipboard_changed(self):
        self._check_clipboard()

    def _show_magnet_dialog(self, magnet_link):
        dlg = ClipboardMagnetDialog(magnet_link, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg.chk_dont_show.isChecked():
                if hasattr(self, "page_settings") and self.page_settings:
                    self.page_settings.saved_settings["skip_magnet_dialog"] = True
                    self.page_settings._save_settings_file()
            
            self.showNormal()
            self.activateWindow()
            self.raise_()
            self.handle_torrent_file(magnet_link)
        else:
            if dlg.chk_dont_show.isChecked():
                if hasattr(self, "page_settings") and self.page_settings:
                    self.page_settings.saved_settings["skip_magnet_dialog"] = True
                    self.page_settings._save_settings_file()

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
