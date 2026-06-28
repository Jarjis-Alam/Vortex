presets = {
    "Vortex Glass": {
        "bg_main": "#060713", "bg_panel": "rgba(10, 14, 28, 0.45)", "bg_card": "rgba(20, 26, 46, 0.40)",
        "border": "rgba(255, 255, 255, 0.08)", "border_alt": "rgba(255, 255, 255, 0.05)", "text": "#ffffff",
        "text_muted": "#8b9bb4", "accent": "#2563eb", "accent_hover": "#3b82f6",
        "success": "#22c55e", "warning": "#f59e0b", "error": "#ef4444",
        "bg_card_alpha": "rgba(20, 24, 40, 0.4)", "border_glow": "rgba(37, 99, 235, 0.25)",
        "header_sec": "#8b9bb4", "grid_line": "rgba(255, 255, 255, 0.03)"
    },
    "Midnight Blue": {
        "bg_main": "#0b0e18", "bg_panel": "#0f1220", "bg_card": "#141828",
        "border": "#1e2438", "border_alt": "#1a1f30", "text": "#c8d0e0",
        "text_muted": "#5a6580", "accent": "#2563eb", "accent_hover": "#3b82f6",
        "success": "#22c55e", "warning": "#f59e0b", "error": "#ef4444",
        "bg_card_alpha": "rgba(20, 24, 40, 0.65)", "border_glow": "rgba(37, 99, 235, 0.25)",
        "header_sec": "#5a6580", "grid_line": "#161b2c"
    },
    "Dracula": {
        "bg_main": "#1e1f29", "bg_panel": "#282a36", "bg_card": "#343746",
        "border": "#44475a", "border_alt": "#3d4054", "text": "#f8f8f2",
        "text_muted": "#6272a4", "accent": "#bd93f9", "accent_hover": "#caa9fa",
        "success": "#50fa7b", "warning": "#ffb86c", "error": "#ff5555",
        "bg_card_alpha": "rgba(52, 55, 70, 0.65)", "border_glow": "rgba(189, 147, 249, 0.25)",
        "header_sec": "#6272a4", "grid_line": "#21222c"
    },
    "AMOLED": {
        "bg_main": "#000000", "bg_panel": "#050505", "bg_card": "#111111",
        "border": "#222222", "border_alt": "#1c1c1c", "text": "#ffffff",
        "text_muted": "#666666", "accent": "#007acc", "accent_hover": "#1f9eff",
        "success": "#22c55e", "warning": "#f59e0b", "error": "#ef4444",
        "bg_card_alpha": "rgba(17, 17, 17, 0.65)", "border_glow": "rgba(0, 122, 204, 0.25)",
        "header_sec": "#888888", "grid_line": "#1a1a1a"
    },
    "Nord": {
        "bg_main": "#2e3440", "bg_panel": "#3b4252", "bg_card": "#434c5e",
        "border": "#4c566a", "border_alt": "#434c5e", "text": "#d8dee9",
        "text_muted": "#7b88a1", "accent": "#88c0d0", "accent_hover": "#8fbcbb",
        "success": "#a3be8c", "warning": "#ebcb8b", "error": "#bf616a",
        "bg_card_alpha": "rgba(67, 76, 94, 0.65)", "border_glow": "rgba(136, 192, 208, 0.25)",
        "header_sec": "#7b88a1", "grid_line": "#3b4252"
    },
    "Catppuccin": {
        "bg_main": "#1e1e2e", "bg_panel": "#181825", "bg_card": "#313244",
        "border": "#45475a", "border_alt": "#313244", "text": "#cdd6f4",
        "text_muted": "#7f849c", "accent": "#cba6f7", "accent_hover": "#f5c2e7",
        "success": "#a6e3a1", "warning": "#f9e2af", "error": "#f38ba8",
        "bg_card_alpha": "rgba(49, 50, 68, 0.65)", "border_glow": "rgba(203, 166, 247, 0.25)",
        "header_sec": "#7f849c", "grid_line": "#1e1e2f"
    },
    "Light": {
        "bg_main": "#f0f2f5", "bg_panel": "#ffffff", "bg_card": "#f8f9fa",
        "border": "#cbd5e1", "border_alt": "#cbd5e1", "text": "#1e293b",
        "text_muted": "#64748b", "accent": "#2563eb", "accent_hover": "#3b82f6",
        "success": "#16a34a", "warning": "#ea580c", "error": "#dc2626",
        "bg_card_alpha": "rgba(248, 249, 250, 0.8)", "border_glow": "rgba(37, 99, 235, 0.15)",
        "header_sec": "#64748b", "grid_line": "#e2e8f0"
    }
}

def hex_to_rgba(hex_str, alpha=0.12):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = "".join([c*2 for c in hex_str])
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"

def get_theme_qss(theme_name):
    colors = presets.get(theme_name, presets["Midnight Blue"])
    accent_rgba = hex_to_rgba(colors["accent"], 0.12)
    
    return f"""
    QMainWindow {{
        background-color: {colors["bg_main"]};
    }}
    QWidget {{
        color: {colors["text"]};
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 15px;
    }}

    /* ── Sidebar ── */
    QWidget#sidebar {{
        background-color: {colors["bg_panel"]};
        border-right: 1px solid {colors["border"]};
    }}
    QLabel#logoText {{
        font-size: 22px;
        font-weight: bold;
        color: {colors["text"]};
    }}
    QPushButton[objectName^="nav_"] {{
        background: transparent;
        border: none;
        border-left: 3px solid transparent;
        border-radius: 10px;
        text-align: left;
        padding: 9px 16px 9px 13px;
        color: {colors["text_muted"]};
        font-weight: 500;
        font-size: 15px;
        spacing: 12px;
    }}
    QPushButton[objectName^="nav_"]:checked {{
        background-color: {accent_rgba};
        border-left: 3px solid {colors["accent"]};
        color: {colors["accent"]};
        font-weight: bold;
    }}
    QPushButton[objectName^="nav_"]:hover {{
        background-color: rgba(255,255,255,0.04);
        color: {colors["text"]};
    }}
    QFrame#sidebarSep {{
        background-color: {colors["border"]};
        max-height: 1px;
        margin: 10px 6px;
    }}
    QFrame#proFrame {{
        background-color: {colors["bg_card"]};
        border: 1px solid {colors["border"]};
        border-radius: 12px;
    }}
    QLabel#proTitle {{
        font-weight: bold;
        color: {colors["text"]};
        font-size: 16px;
    }}
    QLabel#proClose {{
        color: {colors["text_muted"]};
        font-size: 18px;
    }}
    QLabel#proDesc {{
        color: {colors["text_muted"]};
        font-size: 13px;
    }}
    QPushButton#goProBtn {{
        background: {colors["accent"]};
        border: none;
        border-radius: 999px;
        color: #ffffff;
        font-weight: bold;
        font-size: 15px;
    }}
    QPushButton#goProBtn:hover {{
        background: {colors["accent_hover"]};
    }}

    /* ── Toolbar area ── */
    QWidget#toolbarWidget {{
        background-color: {colors["bg_panel"]};
        border-bottom: 1px solid {colors["border"]};
    }}
    QPushButton#tbtn_add {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {colors["accent"]}, stop:1 {colors["accent_hover"]});
        border: none;
        border-radius: 999px;
        color: #ffffff;
        font-weight: bold;
        padding: 10px 22px;
        font-size: 15px;
    }}
    QPushButton#tbtn_add:hover {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {colors["accent_hover"]}, stop:1 {colors["accent"]});
    }}
    QPushButton[objectName^="tbtn_action"] {{
        background: transparent;
        border: 1px solid {colors["border"]};
        border-radius: 999px;
        color: {colors["text"]};
        padding: 10px 20px;
        font-size: 15px;
    }}
    QPushButton[objectName^="tbtn_action"]:hover {{
        background-color: rgba(255,255,255,0.06);
        border-color: {colors["accent"]};
        color: {colors["text"]};
    }}
    QLineEdit#searchBox {{
        background-color: {colors["bg_card"]};
        border: 1px solid {colors["border"]};
        border-radius: 999px;
        padding: 9px 16px 9px 36px;
        color: {colors["text_muted"]};
        font-size: 15px;
        min-width: 220px;
    }}
    QLineEdit#searchBox:focus {{
        border-color: {colors["accent"]};
        color: {colors["text"]};
    }}

    /* ── Stats bar ── */
    QWidget#statsBar {{
        background-color: {colors["bg_panel"]};
        border-bottom: 1px solid {colors["border"]};
    }}
    QLabel#statValue {{
        font-size: 16px;
        font-weight: bold;
    }}
    QLabel#statLabel {{
        font-size: 13px;
        color: {colors["text_muted"]};
    }}

    /* ── Torrent Table ── */
    QTableWidget#torrentTable {{
        background-color: {colors["bg_panel"]};
        border: none;
        gridline-color: {colors["grid_line"]};
        selection-background-color: rgba(37, 99, 235, 0.10);
        outline: none;
        font-size: 14px;
    }}
    QTableWidget#torrentTable::item {{
        padding: 12px 14px;
        border-bottom: 1px solid {colors["grid_line"]};
    }}
    QTableWidget#torrentTable::item:selected {{
        background-color: rgba(37, 99, 235, 0.10);
        color: {colors["text"]};
    }}
    QTableWidget#torrentTable::item:hover {{
        background-color: rgba(255, 255, 255, 0.03);
    }}
    QHeaderView::section {{
        background-color: {colors["bg_panel"]};
        color: {colors["text_muted"]};
        padding: 10px 14px;
        border: none;
        border-bottom: 1px solid {colors["border"]};
        font-weight: 600;
        font-size: 13px;
    }}
    QHeaderView::section:hover {{
        color: {colors["text"]};
    }}

    /* ── Progress Bar ── */
    QProgressBar {{
        border: none;
        border-radius: 999px;
        text-align: center;
        background-color: {colors["border"]};
        color: transparent;
        max-height: 10px;
        min-height: 10px;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2F7CF6, stop:1 #47B2FF);
        border-radius: 999px;
    }}

    /* ── Bottom Tabs ── */
    QTabWidget#detailTabs::pane {{
        border: none;
        border-top: 1px solid {colors["border"]};
        background-color: {colors["bg_panel"]};
    }}
    QTabBar::tab {{
        background: transparent;
        border: none;
        padding: 12px 24px;
        color: {colors["text_muted"]};
        font-weight: 500;
        font-size: 15px;
        border-bottom: 2px solid transparent;
    }}
    QTabBar::tab:selected {{
        color: {colors["text"]};
        border-bottom: 2px solid {colors["accent"]};
    }}
    QTabBar::tab:hover {{
        color: {colors["text"]};
    }}

    /* ── Detail panel widgets ── */
    QWidget#detailPanel {{
        background-color: {colors["bg_panel"]};
    }}
    QLabel#detailName {{
        font-size: 18px;
        font-weight: bold;
        color: {colors["text"]};
    }}
    QLabel#detailKey {{
        color: {colors["text_muted"]};
        font-size: 14px;
    }}
    QLabel#detailVal {{
        color: {colors["text"]};
        font-size: 14px;
        font-weight: 500;
    }}

    /* ── Peer / File Tables ── */
    QTableWidget#peerTable, QTreeWidget#fileTree {{
        background-color: {colors["bg_panel"]};
        border: none;
        gridline-color: {colors["grid_line"]};
        color: {colors["text"]};
        font-size: 14px;
    }}
    QTreeWidget#fileTree::item {{
        padding: 6px 10px;
    }}

    /* ── Log Console ── */
    QTextEdit#logConsole {{
        background-color: {colors["bg_main"]};
        border: none;
        color: {colors["accent"]};
        font-family: 'JetBrains Mono', 'Consolas', monospace;
        font-size: 14px;
        padding: 12px;
    }}

    /* ── Scrollbars ── */
    QScrollBar:vertical {{
        background: {colors["bg_panel"]};
        width: 10px;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {colors["border"]};
        border-radius: 999px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {colors["border_alt"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {colors["bg_panel"]};
        height: 10px;
        border: none;
    }}
    QScrollBar::handle:horizontal {{
        background: {colors["border"]};
        border-radius: 999px;
    }}

    /* ── Splitter ── */
    QSplitter::handle {{
        background-color: {colors["border"]};
        height: 2px;
    }}

    /* ── Dialogs ── */
    QDialog {{
        background-color: {colors["bg_panel"]};
    }}
    QMessageBox {{
        background-color: {colors["bg_panel"]};
    }}
    QMenu {{
        background-color: {colors["bg_card"]};
        border: 1px solid {colors["border"]};
        border-radius: 12px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 10px 24px;
        border-radius: 999px;
        font-size: 14px;
    }}
    QMenu::item:selected {{
        background-color: rgba(37, 99, 235, 0.15);
        color: {colors["text"]};
    }}

    /* ── Card Grid Transparent Backgrounds ── */
    QScrollArea#cardScrollArea {{
        background-color: transparent;
        border: none;
    }}
    QWidget#cardContainer {{
        background-color: transparent;
    }}
    """
