import sys
from torrent import Torrent
from peer import generate_peer_id
from tracker_client import UDPTrackerClient
from download_manager import DownloadManager

def run_cli():
    torrent = Torrent("zorin.torrent")
    print("Contacting tracker...")
    tracker_client = UDPTrackerClient("tracker.opentrackr.org", 6969)
    
    connect_response = tracker_client.connect()
    parsed_connect = tracker_client.parse_connect_response(connect_response)
    connection_id = parsed_connect["connection_id"]
    
    announce_packet = tracker_client.build_announce_request(
        connection_id,
        torrent.get_info_hash_bytes(),
        generate_peer_id(),
        torrent.get_size()
    )
    announce_response = tracker_client.announce(announce_packet)
    parsed_announce = tracker_client.parse_announce_response(announce_response)
    peers = parsed_announce["peers"]
    
    print(f"Tracker returned {len(peers)} peers")
    for i, (ip, port) in enumerate(peers[:30]):
        print(f"{i+1}. {ip}:{port}")
        
    output_filename = torrent.get_name().decode('utf-8')
    manager = DownloadManager(
        peers,
        torrent,
        output_filename,
        num_workers=10
    )
    
    success = manager.download(target=None)
    if success:
        print(f"\nSaved to {output_filename}")
    else:
        print("\nDownload incomplete.")

def run_gui():
    try:
        import os
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        from gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setDesktopFileName("vortex")
        
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "logo.png")
        if os.path.exists(logo_path):
            app.setWindowIcon(QIcon(logo_path))
            
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Failed to start GUI: {e}")
        print("Falling back to CLI mode...")
        run_cli()

if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_gui()