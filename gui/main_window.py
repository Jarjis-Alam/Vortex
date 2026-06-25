import os
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QProgressBar,
    QFileDialog, QSplitter, QLabel, QHeaderView,
    QAbstractItemView, QPushButton, QMessageBox,
    QMenu, QDialog, QLineEdit, QTextEdit, QTreeWidgetItem
)
from PyQt6.QtCore import QTimer, Qt, QObject, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QPixmap

from gui.sidebar import Sidebar
from gui.stats_bar import StatsBar
from gui.detail_panel import DetailPanel
from gui.theme import VORTEX_THEME
from torrent_manager import TorrentManager


class MagnetDialog(QDialog):
    def __init__(self, parent=None, default_save_dir="."):
        super().__init__(parent)
        self.setWindowTitle("Add Magnet Link")
        self.resize(500, 300)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(QLabel("Magnet URI:"))
        self.txt_magnet = QTextEdit()
        self.txt_magnet.setPlaceholderText("magnet:?xt=urn:btih:...")
        layout.addWidget(self.txt_magnet)
        layout.addWidget(QLabel("Save Path:"))
        self.txt_save = QLineEdit(default_save_dir)
        self.btn_browse = QPushButton("Browse")
        self.btn_browse.clicked.connect(self.browse_save_dir)
        sl = QHBoxLayout()
        sl.addWidget(self.txt_save)
        sl.addWidget(self.btn_browse)
        layout.addLayout(sl)
        bl = QHBoxLayout()
        bc = QPushButton("Cancel")
        bd = QPushButton("Download")
        bc.clicked.connect(self.reject)
        bd.clicked.connect(self.accept)
        bl.addStretch()
        bl.addWidget(bc)
        bl.addWidget(bd)
        layout.addLayout(bl)

    def browse_save_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Save Directory", self.txt_save.text())
        if d:
            self.txt_save.setText(d)

    def get_data(self):
        return self.txt_magnet.toPlainText().strip(), self.txt_save.text().strip()


def format_speed(speed_mb):
    return f"{speed_mb:.2f} MB/s" if speed_mb >= 1.0 else f"{speed_mb * 1024:.1f} KB/s"

def format_size(b):
    for u in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024.0:
            return f"{b:.2f} {u}"
        b /= 1024.0
    return f"{b:.2f} PB"

def format_eta(s):
    if s is None or s < 0 or s == float('inf'):
        return "∞"
    s = int(s)
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    return f"{h}h {m}m"


class LogSignaler(QObject):
    log_signal = pyqtSignal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vortex")
        self.resize(1400, 850)
        self._setup_icons()
        self.manager = TorrentManager()
        self.selected_task = None
        self.log_signaler = LogSignaler()
        self.log_signaler.log_signal.connect(self._append_log)
        self._current_filter = "Torrents"
        self._init_ui()
        self.setStyleSheet(VORTEX_THEME)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gui_stats)
        self.timer.start(1000)
        self.log("Vortex GUI initialized.")
        QTimer.singleShot(1000, self._check_clipboard)

    def _setup_icons(self):
        import shutil
        base = "/home/jarjis/.gemini/antigravity/brain/7d114df7-267c-421e-9513-46238f4a6f8a"
        src_map = {
            "resume": f"{base}/media__1782303921094.png",
            "pause": f"{base}/media__1782304036316.png",
            "remove": f"{base}/media__1782304486047.png",
            "about": f"{base}/media__1782304173487.png",
            "logo": f"{base}/media__1782304275212.png",
            "add": f"{base}/media__1782304581869.png",
            "magnet": f"{base}/media__1782305106390.png",
        }
        dest_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")
        os.makedirs(dest_dir, exist_ok=True)

        def make_white(src, dst):
            if not os.path.exists(src):
                return
            try:
                from PyQt6.QtGui import QImage, QColor as QC
                img = QImage(src).convertToFormat(QImage.Format.Format_ARGB32)
                for y in range(img.height()):
                    for x in range(img.width()):
                        c = QC.fromRgba(img.pixel(x, y))
                        if c.alpha() > 0:
                            img.setPixel(x, y, QC(255, 255, 255, c.alpha()).rgba())
                img.save(dst)
            except Exception:
                pass

        for name, src in src_map.items():
            dst = os.path.join(dest_dir, f"{name}.png")
            if name == "logo":
                if os.path.exists(src) and not os.path.exists(dst):
                    shutil.copy(src, dst)
            else:
                if not os.path.exists(dst):
                    make_white(src, dst)

        logo = os.path.join(dest_dir, "logo.png")
        if os.path.exists(logo):
            self.setWindowIcon(QIcon(logo))

    def _icon(self, name):
        p = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", f"{name}.png")
        return QIcon(p) if os.path.exists(p) else QIcon()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.filter_changed.connect(self._on_filter)
        self.sidebar.items["About"].clicked.connect(self._show_about)
        root.addWidget(self.sidebar)

        # Right content
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        # Toolbar
        tb = QWidget()
        tb.setObjectName("toolbarWidget")
        tb.setFixedHeight(64)
        tbl = QHBoxLayout(tb)
        tbl.setContentsMargins(20, 10, 20, 10)
        tbl.setSpacing(12)

        btn_add = QPushButton("  Add Torrent")
        btn_add.setObjectName("tbtn_add")
        btn_add.setIcon(self._icon("add"))
        btn_add.setIconSize(QSize(18, 18))
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        add_menu = QMenu(self)
        add_menu.addAction("Add Torrent File").triggered.connect(self._add_torrent)
        add_menu.addAction("Add Magnet Link").triggered.connect(self._add_magnet)
        add_menu.addAction("Paste from Clipboard").triggered.connect(self._add_paste)
        btn_add.setMenu(add_menu)
        tbl.addWidget(btn_add)

        for name, icon, slot in [
            ("Magnet Link", "magnet", self._add_magnet),
            ("Resume", "resume", self._resume),
            ("Pause", "pause", self._pause),
            ("Remove", "remove", self._remove),
        ]:
            b = QPushButton(f"  {name}")
            b.setObjectName("tbtn_action_" + name.lower().replace(" ", ""))
            b.setIcon(self._icon(icon))
            b.setIconSize(QSize(18, 18))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(slot)
            tbl.addWidget(b)

        tbl.addStretch()

        self.search = QLineEdit()
        self.search.setObjectName("searchBox")
        self.search.setPlaceholderText("🔍 Search torrents...")
        self.search.textChanged.connect(self._on_search)
        tbl.addWidget(self.search)

        right.addWidget(tb)

        # Stats bar
        self.stats_bar = StatsBar()
        right.addWidget(self.stats_bar)

        # Splitter: table + detail
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Torrent table
        self.table = QTableWidget()
        self.table.setObjectName("torrentTable")
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "#", "Name", "Size", "Progress", "Status", "Down Speed", "Up Speed", "ETA", "Peers"
        ])
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hdr.resizeSection(0, 50)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        hdr.resizeSection(1, 320)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        splitter.addWidget(self.table)

        # Detail panel
        self.detail = DetailPanel()
        splitter.addWidget(self.detail)
        splitter.setSizes([400, 320])

        right.addWidget(splitter, 1)
        root.addLayout(right, 1)

    def _on_filter(self, name):
        self._current_filter = name
        self._refresh_table()

    def _on_search(self, text):
        self._refresh_table()

    def log(self, msg):
        self.log_signaler.log_signal.emit(msg)

    def _append_log(self, msg):
        ts = time.strftime("[%H:%M:%S]")
        self.detail.txt_log.append(f"{ts} {msg}")

    def _ucell(self, row, col, text):
        item = self.table.item(row, col)
        if not item:
            item = QTableWidgetItem(text)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, col, item)
        elif item.text() != text:
            item.setText(text)

    def _status_color(self, status):
        m = {"Downloading": "#3b82f6", "Completed": "#22c55e", "Seeding": "#22c55e",
             "Paused": "#ef4444", "Queued": "#f59e0b", "Error": "#ef4444",
             "Checking": "#f59e0b", "Stopped": "#6b7280"}
        return m.get(status, "#8892a8")

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
            elif f == "Inactive" and t.status in ("Paused", "Stopped", "Queued"):
                tasks.append(t)
            elif f not in ("Torrents", "Downloading", "Completed", "Active", "Inactive"):
                tasks.append(t)
        return tasks

    def _refresh_table(self):
        tasks = self._filtered_tasks()
        self.table.setRowCount(len(tasks))
        total_dl_speed = 0.0
        total_ul_speed = 0.0
        total_downloaded = 0
        active_count = 0

        for idx, task in enumerate(tasks):
            name = task.torrent.get_name().decode('utf-8', errors='ignore')
            size_bytes = task.torrent.get_size()
            cc = 0
            if task.manager:
                with task.manager.completed_lock:
                    cc = len(task.manager.completed)
            pc = task.torrent.get_piece_count()
            progress = (cc / pc * 100) if pc > 0 else 0.0
            status = task.status
            ds = us = 0.0
            eta = None
            peers = 0

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
                    peers = len([p for p in task.manager.pool.active_peers if p['in_use']])
                total_downloaded += db

            if status == "Downloading":
                active_count += 1
            total_dl_speed += ds
            total_ul_speed += us

            self._ucell(idx, 0, str(idx + 1))
            self._ucell(idx, 1, name)
            self._ucell(idx, 2, format_size(size_bytes))

            pbar = self.table.cellWidget(idx, 3)
            if not pbar:
                pbar = QProgressBar()
                pbar.setTextVisible(False)
                pbar.setFixedHeight(10)
                self.table.setCellWidget(idx, 3, pbar)
            pbar.setValue(int(progress))
            if progress >= 100:
                pbar.setStyleSheet("QProgressBar::chunk { background: #22c55e; border-radius: 4px; }")

            # Status with color
            self._ucell(idx, 4, status)
            si = self.table.item(idx, 4)
            if si:
                from PyQt6.QtGui import QColor
                si.setForeground(QColor(self._status_color(status)))

            self._ucell(idx, 5, format_speed(ds))
            self._ucell(idx, 6, format_speed(us))
            self._ucell(idx, 7, format_eta(eta))
            self._ucell(idx, 8, str(peers))

        # Update stats bar
        self.stats_bar.update_stats(
            format_speed(total_dl_speed), format_speed(total_ul_speed),
            active_count, format_size(total_downloaded)
        )

        # Update sidebar badges
        all_tasks = self.manager.tasks
        self.sidebar.update_badges(
            total=len(all_tasks),
            downloading=sum(1 for t in all_tasks if t.status == "Downloading"),
            completed=sum(1 for t in all_tasks if t.status in ("Completed", "Seeding")),
            active=sum(1 for t in all_tasks if t.status in ("Downloading", "Seeding")),
            inactive=sum(1 for t in all_tasks if t.status in ("Paused", "Stopped"))
        )

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
        d.donut.set_value(0)
        for v in [d.v_save, d.v_size, d.v_pieces, d.v_hash, d.v_status,
                   d.v_downloaded, d.v_remaining, d.v_eta, d.v_added,
                   d.v_peers, d.v_seeds, d.v_avail, d.v_ratio, d.v_active]:
            v.setText("—")
        d.tree_files.clear()
        d.table_peers.setRowCount(0)

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
        if task.manager:
            with task.manager.completed_lock:
                cc = len(task.manager.completed)
        pc = t.get_piece_count()
        pl = t.get_piece_length()
        ts = t.get_size()
        downloaded = min(cc * pl, ts)
        remaining = ts - downloaded
        progress = (cc / pc * 100) if pc > 0 else 0.0

        name = t.get_name().decode('utf-8', errors='ignore')
        d.lbl_name.setText(name)
        d.donut.set_value(progress)
        d.v_save.setText(task.output_filename)
        d.v_size.setText(format_size(ts))
        d.v_pieces.setText(f"{cc} / {pc}")
        d.v_hash.setText(t.get_info_hash()[:12] + "..." if hasattr(t, 'get_info_hash') else "—")
        d.v_status.setText(task.status)
        d.v_status.setStyleSheet(f"color: {self._status_color(task.status)}; font-weight: bold;")
        d.v_downloaded.setText(format_size(downloaded))
        d.v_remaining.setText(format_size(remaining))

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
            d.v_eta.setText(format_eta(eta))

            with task.manager.pool.lock:
                conn = len(task.manager.pool.active_peers)
                act = sum(1 for p in task.manager.pool.active_peers if p['in_use'])
            d.v_peers.setText(str(conn))
            d.v_seeds.setText(str(act))
            d.v_avail.setText("—")
            d.v_ratio.setText("0.00")
            d.v_active.setText(f"{dur}s ago" if dur > 0 else "—")
            d.v_added.setText(time.strftime("%b %d, %Y %I:%M %p"))
            self._update_peers_table(task)

    def _update_peers_table(self, task):
        pt = self.detail.table_peers
        if not task.manager or not task.manager.pool:
            pt.setRowCount(0)
            return
        with task.manager.pool.lock:
            peers = list(task.manager.pool.active_peers)
        pt.setRowCount(len(peers))
        for i, p in enumerate(peers):
            pc = p['peer']
            ip, port = pc.ip, pc.port
            in_use = "Yes" if p['in_use'] else "No"
            stats = task.manager.pool.peer_stats.get(f"{ip}:{port}")
            spd = format_speed(stats['average_speed']) if stats else "0.00 KB/s"
            suc = str(stats['successes']) if stats else "0"
            fail = str(stats['failures'] + stats['timeouts']) if stats else "0"
            for j, v in enumerate([ip, str(port), in_use, spd, suc, fail]):
                item = pt.item(i, j)
                if not item:
                    item = QTableWidgetItem(v)
                    pt.setItem(i, j, item)
                elif item.text() != v:
                    item.setText(v)

    # ── Actions ──
    def _add_torrent(self):
        fp, _ = QFileDialog.getOpenFileName(self, "Open Torrent File", "", "Torrent Files (*.torrent)")
        if not fp:
            return
        task = self.manager.add_torrent(fp)
        self.log(f"Adding torrent: {os.path.basename(fp)}")
        task.start()
        self.selected_task = task
        self._populate_files(task)
        self._refresh_table()

    def _add_magnet(self):
        dlg = MagnetDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            uri, sd = dlg.get_data()
            if uri:
                self._process_magnet(uri, sd)

    def _add_paste(self):
        from PyQt6.QtWidgets import QApplication
        cb = QApplication.clipboard().text().strip()
        if cb.startswith("magnet:?"):
            dlg = MagnetDialog(self)
            dlg.txt_magnet.setPlainText(cb)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                uri, sd = dlg.get_data()
                if uri:
                    self._process_magnet(uri, sd)
        else:
            QMessageBox.information(self, "Paste", "No valid magnet link in clipboard.")

    def _process_magnet(self, uri, sd):
        task = self.manager.add_magnet(uri, sd)
        if task:
            task.start()
            self.selected_task = task
            self._populate_files(task)
            self._refresh_table()
            self.log(f"Added magnet: {uri[:60]}...")

    def _resume(self):
        if self.selected_task:
            self.selected_task.resume()
            self.log(f"Resumed: {self.selected_task.torrent.get_name().decode('utf-8', errors='ignore')}")
            self._refresh_table()

    def _pause(self):
        if self.selected_task:
            self.selected_task.pause()
            self.log(f"Paused: {self.selected_task.torrent.get_name().decode('utf-8', errors='ignore')}")
            self._refresh_table()

    def _remove(self):
        if self.selected_task:
            name = self.selected_task.torrent.get_name().decode('utf-8', errors='ignore')
            self.log(f"Removing: {name}")
            self.manager.remove_torrent(self.selected_task)
            self.selected_task = None
            self._clear_detail()
            self._refresh_table()

    def _check_clipboard(self):
        from PyQt6.QtWidgets import QApplication
        cb = QApplication.clipboard().text().strip()
        if cb.startswith("magnet:?"):
            r = QMessageBox.question(self, "Magnet Detected",
                f"Magnet link in clipboard:\n\n{cb[:100]}...\n\nDownload?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if r == QMessageBox.StandardButton.Yes:
                dlg = MagnetDialog(self)
                dlg.txt_magnet.setPlainText(cb)
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    uri, sd = dlg.get_data()
                    if uri:
                        self._process_magnet(uri, sd)

    def _show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About Vortex")
        logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "logo.png")
        if os.path.exists(logo):
            msg.setIconPixmap(QPixmap(logo).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText("""
        <div style='color: #e2e8f0;'>
            <h2 style='color: #3b82f6;'>Vortex</h2>
            <p>A powerful BitTorrent client.</p>
            <p><b>Version:</b> 1.0.0</p>
            <hr style='border-top: 1px solid #1e2438;'/>
            <p><b>Developer:</b> Munshi Jarjis Alam</p>
            <p><a href="https://github.com/Jarjis-Alam" style="color: #3b82f6;">GitHub</a> •
            <a href="https://linkedin.com/in/jarjisalam/" style="color: #3b82f6;">LinkedIn</a> •
            <a href="https://instagram.com/jarvis._exe_" style="color: #3b82f6;">Instagram</a></p>
        </div>""")
        msg.exec()

    def closeEvent(self, event):
        self.log("Closing. Stopping all tasks...")
        for task in self.manager.tasks:
            task.stop()
        event.accept()
