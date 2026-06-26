from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import Qt

class FilesMissingDialog(QDialog):
    def __init__(self, torrent_name, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚠ Files Missing")
        self.setFixedSize(450, 180)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowCloseButtonHint)
        self.setObjectName("filesMissingDialog")
        
        # Apply dark styling matching the theme
        self.setStyleSheet("""
            QDialog#filesMissingDialog {
                background-color: #141828;
                border: 1px solid #ef4444;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #1b2035;
                color: #ffffff;
                border: 1px solid #2e3556;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #252b48;
            }
            QPushButton#btnLocate {
                background-color: #2563eb;
                border: 1px solid #3b82f6;
            }
            QPushButton#btnLocate:hover {
                background-color: #3b82f6;
            }
            QPushButton#btnRemove {
                background-color: #ef4444;
                border: 1px solid #f87171;
            }
            QPushButton#btnRemove:hover {
                background-color: #f87171;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        lbl_msg = QLabel(
            f"<b>Files Missing for:</b> {torrent_name}<br><br>"
            f"The download file was not found at:<br>"
            f"<font color='#ef4444'>{file_path}</font>"
        )
        lbl_msg.setWordWrap(True)
        layout.addWidget(lbl_msg)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.btn_recheck = QPushButton("Recheck")
        self.btn_locate = QPushButton("Locate Files")
        self.btn_locate.setObjectName("btnLocate")
        self.btn_remove = QPushButton("Remove Torrent")
        self.btn_remove.setObjectName("btnRemove")
        
        btn_layout.addWidget(self.btn_recheck)
        btn_layout.addWidget(self.btn_locate)
        btn_layout.addWidget(self.btn_remove)
        
        layout.addLayout(btn_layout)
        
        self.action = None
        
        self.btn_recheck.clicked.connect(self._on_recheck)
        self.btn_locate.clicked.connect(self._on_locate)
        self.btn_remove.clicked.connect(self._on_remove)
        
    def _on_recheck(self):
        self.action = "recheck"
        self.accept()
        
    def _on_locate(self):
        self.action = "locate"
        self.accept()
        
    def _on_remove(self):
        self.action = "remove"
        self.accept()
