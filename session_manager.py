import os
import sys
import json
import shutil
import datetime

def get_vortex_dir():
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA")
        if not base:
            base = os.path.expanduser("~")
        return os.path.join(base, "Vortex")
    elif sys.platform.startswith("darwin"):
        return os.path.expanduser("~/Library/Application Support/Vortex")
    else:
        return os.path.expanduser("~/.vortex")

class SessionManager:
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.vortex_dir = get_vortex_dir()
        self.torrents_dir = os.path.join(self.vortex_dir, "torrents")
        self.progress_dir = os.path.join(self.vortex_dir, "progress")
        self.fastresume_dir = os.path.join(self.vortex_dir, "fastresume")
        self.cache_dir = os.path.join(self.vortex_dir, "cache")
        self.logs_dir = os.path.join(self.vortex_dir, "logs")
        
        # Ensure directories exist
        for d in [self.torrents_dir, self.progress_dir, self.fastresume_dir, self.cache_dir, self.logs_dir]:
            os.makedirs(d, exist_ok=True)
            
        self.session_file = os.path.join(self.vortex_dir, "session.json")

    def save_session(self, tasks, active_task=None):
        torrents_data = []
        for task in tasks:
            status = task.status
            torrent_file = task.torrent_path
            
            # Auto-copy original torrent file if not in vortex directory
            if torrent_file and os.path.exists(torrent_file) and not torrent_file.startswith(self.torrents_dir):
                torrent_file = self.copy_torrent_file(torrent_file, task.torrent.get_info_hash())
                task.torrent_path = torrent_file
            
            info_hash = task.torrent.get_info_hash()
            progress_file = os.path.join(self.progress_dir, f"{info_hash}.json")
            
            torrents_data.append({
                "torrent_file": torrent_file,
                "save_path": task.save_dir,
                "status": status,
                "progress_file": progress_file,
                "added_time": getattr(task, "added_time", datetime.datetime.now().isoformat()),
                "magnet_uri": task.magnet_uri,
                "info_hash": info_hash
            })
            
        ui_state = {}
        if self.main_window:
            ui_state = {
                "window_size": [self.main_window.width(), self.main_window.height()],
                "sidebar_state": self.main_window._current_filter,
                "selected_torrent_hash": self.main_window.selected_task.torrent.get_info_hash() if (self.main_window.selected_task and self.main_window.selected_task.torrent) else None,
            }
            table_widget = None
            if hasattr(self.main_window, "table"):
                table_widget = self.main_window.table
            elif hasattr(self.main_window, "torrent_table"):
                table_widget = self.main_window.torrent_table
                
            if table_widget is not None:
                order = table_widget.horizontalHeader().sortIndicatorOrder()
                order_val = order.value if hasattr(order, "value") else int(order)
                ui_state["sorting"] = [
                    table_widget.horizontalHeader().sortIndicatorSection(),
                    order_val
                ]
                ui_state["column_widths"] = [
                    table_widget.columnWidth(i)
                    for i in range(table_widget.columnCount())
                ]
            if hasattr(self.main_window, "page_settings") and hasattr(self.main_window.page_settings, "saved_settings"):
                ui_state["theme"] = self.main_window.page_settings.saved_settings.get("theme")
                ui_state["accent_color"] = self.main_window.page_settings.saved_settings.get("accent_color")
                
        session_data = {
            "torrents": torrents_data,
            "ui_state": ui_state
        }
        
        try:
            with open(self.session_file, "w") as f:
                json.dump(session_data, f, indent=4)
        except Exception as e:
            print(f"Error saving session: {e}")

    def load_session(self):
        if not os.path.exists(self.session_file):
            return {"torrents": [], "ui_state": {}}
        try:
            with open(self.session_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
            return {"torrents": [], "ui_state": {}}

    def copy_torrent_file(self, original_path, info_hash):
        if not original_path or not os.path.exists(original_path):
            return original_path
        dest_path = os.path.join(self.torrents_dir, f"{info_hash}.torrent")
        if os.path.abspath(original_path) != os.path.abspath(dest_path):
            try:
                shutil.copy2(original_path, dest_path)
            except Exception as e:
                print(f"Failed to copy torrent file: {e}")
        return dest_path
