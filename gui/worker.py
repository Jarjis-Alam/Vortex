from PyQt6.QtCore import QThread, pyqtSignal

class DownloadWorker(QThread):
    finished_signal = pyqtSignal(bool)
    
    def __init__(self, manager, target=None):
        super().__init__()
        self.manager = manager
        self.target = target
        
    def run(self):
        try:
            success = self.manager.download(target=self.target)
            self.finished_signal.emit(success)
        except Exception as e:
            print(f"[Worker] Error during download execution: {e}")
            self.finished_signal.emit(False)
