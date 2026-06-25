VORTEX_THEME = """
QMainWindow {
    background-color: #0b0e18;
}
QWidget {
    color: #c8d0e0;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 15px;
}

/* ── Sidebar ── */
QWidget#sidebar {
    background-color: #0f1220;
    border-right: 1px solid #1a1f30;
}
QLabel#logoText {
    font-size: 22px;
    font-weight: bold;
    color: #ffffff;
}
QPushButton[objectName^="nav_"] {
    background: transparent;
    border: none;
    border-radius: 10px;
    text-align: left;
    padding: 9px 14px;
    color: #8892a8;
    font-weight: 500;
    font-size: 15px;
}
QPushButton[objectName^="nav_"]:checked {
    background-color: rgba(45, 121, 243, 0.12);
    color: #4d9eff;
    font-weight: bold;
}
QPushButton[objectName^="nav_"]:hover {
    background-color: rgba(255,255,255,0.04);
    color: #c8d0e0;
}
QFrame#sidebarSep {
    background-color: #1a1f30;
    max-height: 1px;
    margin: 10px 6px;
}
QFrame#proFrame {
    background-color: #141828;
    border: 1px solid #1e2438;
    border-radius: 14px;
}
QLabel#proTitle {
    font-weight: bold;
    color: #ffffff;
    font-size: 16px;
}
QLabel#proClose {
    color: #556;
    font-size: 18px;
}
QLabel#proDesc {
    color: #6b7590;
    font-size: 13px;
}
QPushButton#goProBtn {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2563eb, stop:1 #06b6d4);
    border: none;
    border-radius: 12px;
    color: #ffffff;
    font-weight: bold;
    font-size: 15px;
}
QPushButton#goProBtn:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3b82f6, stop:1 #22d3ee);
}

/* ── Toolbar area ── */
QWidget#toolbarWidget {
    background-color: #0f1220;
    border-bottom: 1px solid #1a1f30;
}
QPushButton#tbtn_add {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
    border: none;
    border-radius: 10px;
    color: #ffffff;
    font-weight: bold;
    padding: 10px 22px;
    font-size: 15px;
}
QPushButton#tbtn_add:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #3b82f6, stop:1 #2563eb);
}
QPushButton[objectName^="tbtn_action"] {
    background: transparent;
    border: 1px solid #1e2438;
    border-radius: 10px;
    color: #c8d0e0;
    padding: 10px 20px;
    font-size: 15px;
}
QPushButton[objectName^="tbtn_action"]:hover {
    background-color: rgba(255,255,255,0.06);
    border-color: #2d3650;
    color: #ffffff;
}
QLineEdit#searchBox {
    background-color: #141828;
    border: 1px solid #1e2438;
    border-radius: 10px;
    padding: 9px 16px 9px 36px;
    color: #8892a8;
    font-size: 15px;
    min-width: 220px;
}
QLineEdit#searchBox:focus {
    border-color: #2563eb;
    color: #ffffff;
}

/* ── Stats bar ── */
QWidget#statsBar {
    background-color: #0f1220;
    border-bottom: 1px solid #1a1f30;
}
QLabel#statValue {
    font-size: 16px;
    font-weight: bold;
}
QLabel#statLabel {
    font-size: 13px;
    color: #5a6580;
}

/* ── Torrent Table ── */
QTableWidget#torrentTable {
    background-color: #0f1220;
    border: none;
    gridline-color: #161b2c;
    selection-background-color: rgba(37, 99, 235, 0.10);
    outline: none;
    font-size: 14px;
}
QTableWidget#torrentTable::item {
    padding: 12px 14px;
    border-bottom: 1px solid #161b2c;
}
QTableWidget#torrentTable::item:selected {
    background-color: rgba(37, 99, 235, 0.10);
    color: #ffffff;
}
QHeaderView::section {
    background-color: #0f1220;
    color: #5a6580;
    padding: 10px 14px;
    border: none;
    border-bottom: 1px solid #1a1f30;
    font-weight: 600;
    font-size: 13px;
}
QHeaderView::section:hover {
    color: #8892a8;
}

/* ── Progress Bar ── */
QProgressBar {
    border: none;
    border-radius: 5px;
    text-align: center;
    background-color: #1a1f30;
    color: transparent;
    max-height: 10px;
    min-height: 10px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2563eb, stop:1 #06b6d4);
    border-radius: 5px;
}

/* ── Bottom Tabs ── */
QTabWidget#detailTabs::pane {
    border: none;
    border-top: 1px solid #1a1f30;
    background-color: #0f1220;
}
QTabBar::tab {
    background: transparent;
    border: none;
    padding: 12px 24px;
    color: #5a6580;
    font-weight: 500;
    font-size: 15px;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #ffffff;
    border-bottom: 2px solid #2563eb;
}
QTabBar::tab:hover {
    color: #8892a8;
}

/* ── Detail panel widgets ── */
QWidget#detailPanel {
    background-color: #0f1220;
}
QLabel#detailName {
    font-size: 18px;
    font-weight: bold;
    color: #ffffff;
}
QLabel#detailKey {
    color: #5a6580;
    font-size: 14px;
}
QLabel#detailVal {
    color: #c8d0e0;
    font-size: 14px;
    font-weight: 500;
}
QLabel#statusDownloading {
    color: #3b82f6;
    font-weight: bold;
}
QLabel#statusSeeding {
    color: #22c55e;
    font-weight: bold;
}
QLabel#statusPaused {
    color: #ef4444;
    font-weight: bold;
}
QLabel#statusQueued {
    color: #f59e0b;
    font-weight: bold;
}

/* ── Peer / File Tables ── */
QTableWidget#peerTable, QTreeWidget#fileTree {
    background-color: #0f1220;
    border: none;
    gridline-color: #161b2c;
    color: #c8d0e0;
    font-size: 14px;
}
QTreeWidget#fileTree::item {
    padding: 6px 10px;
}

/* ── Log Console ── */
QTextEdit#logConsole {
    background-color: #0a0d16;
    border: none;
    color: #06b6d4;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 14px;
    padding: 12px;
}

/* ── Scrollbars ── */
QScrollBar:vertical {
    background: #0f1220;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #1e2438;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #2d3650;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #0f1220;
    height: 10px;
    border: none;
}
QScrollBar::handle:horizontal {
    background: #1e2438;
    border-radius: 5px;
}

/* ── Splitter ── */
QSplitter::handle {
    background-color: #1a1f30;
    height: 2px;
}

/* ── Dialogs ── */
QDialog {
    background-color: #0f1220;
}
QMessageBox {
    background-color: #0f1220;
}
QMenu {
    background-color: #141828;
    border: 1px solid #1e2438;
    border-radius: 10px;
    padding: 6px;
}
QMenu::item {
    padding: 10px 24px;
    border-radius: 6px;
    font-size: 14px;
}
QMenu::item:selected {
    background-color: rgba(37, 99, 235, 0.15);
    color: #ffffff;
}
"""
