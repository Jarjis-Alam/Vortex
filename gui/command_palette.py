from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent

class CommandPalette(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(520, 360)
        
        if parent:
            geo = parent.geometry()
            self.move(int(geo.center().x() - 260), int(geo.top() + 80))
            
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.bg_frame = QFrame()
        self.bg_frame.setObjectName("paletteBg")
        self.bg_frame.setStyleSheet("""
            QFrame#paletteBg {
                background-color: #0f1220;
                border: 1.5px solid #2563eb;
                border-radius: 12px;
            }
        """)
        
        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(14, 14, 14, 14)
        bg_layout.setSpacing(12)
        
        self.search = QLineEdit()
        self.search.setPlaceholderText("Type a command to run...")
        self.search.setStyleSheet("""
            QLineEdit {
                background-color: #141828;
                border: 1px solid #1e2438;
                border-radius: 999px;
                padding: 12px 16px;
                color: #ffffff;
                font-size: 15px;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        self.search.textChanged.connect(self._filter_items)
        bg_layout.addWidget(self.search)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                padding: 10px 14px;
                color: #c8d0e0;
                font-size: 14px;
                border-radius: 12px;
            }
            QListWidget::item:selected {
                background-color: rgba(37, 99, 235, 0.15);
                color: #ffffff;
                font-weight: bold;
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.04);
            }
        """)
        
        self.commands = [
            ("▶ Resume All Torrents", "resume_all"),
            ("⏸ Pause All Torrents", "pause_all"),
            ("📂 Open Downloads Folder", "open_downloads"),
            ("🔗 Add Magnet Link", "add_magnet"),
            ("➕ Add Torrent File", "add_torrent"),
            ("⚙ Open Settings / Preferences", "settings"),
            ("ℹ Open About Vortex", "about"),
            ("🧹 Clean Finished Torrents", "clean_finished")
        ]
        
        for text, cmd_id in self.commands:
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, cmd_id)
            self.list_widget.addItem(item)
            
        self.list_widget.setCurrentRow(0)
        bg_layout.addWidget(self.list_widget)
        
        layout.addWidget(self.bg_frame)
        self.selected_command = None
        self.list_widget.itemActivated.connect(self._execute_selected)
        
    def _filter_items(self, text):
        text = text.strip().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text not in item.text().lower())
            
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if not item.isHidden():
                self.list_widget.setCurrentRow(i)
                break

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Down:
            curr = self.list_widget.currentRow()
            for i in range(curr + 1, self.list_widget.count()):
                if not self.list_widget.item(i).isHidden():
                    self.list_widget.setCurrentRow(i)
                    break
        elif event.key() == Qt.Key.Key_Up:
            curr = self.list_widget.currentRow()
            for i in range(curr - 1, -1, -1):
                if not self.list_widget.item(i).isHidden():
                    self.list_widget.setCurrentRow(i)
                    break
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self._execute_selected(self.list_widget.currentItem())
        else:
            super().keyPressEvent(event)

    def _execute_selected(self, item):
        if item:
            self.selected_command = item.data(Qt.ItemDataRole.UserRole)
            self.accept()
