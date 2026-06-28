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
        from PyQt6.QtNetwork import QLocalServer, QLocalSocket
        from gui.main_window import MainWindow
        from gui.splash_screen import SplashScreen
        
        # Determine if a torrent file or magnet link is passed as an argument
        torrent_file = None
        for arg in sys.argv[1:]:
            if not arg.startswith("-"):
                if os.path.exists(arg):
                    torrent_file = os.path.abspath(arg)
                else:
                    torrent_file = arg
                break

        # Check for another running instance
        socket_name = "vortex_single_instance"
        socket = QLocalSocket()
        socket.connectToServer(socket_name)
        if socket.waitForConnected(500):
            if torrent_file:
                socket.write(torrent_file.encode('utf-8'))
                socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
            sys.exit(0)

        # Start local server to listen for subsequent instances
        server = QLocalServer()
        QLocalServer.removeServer(socket_name)
        if not server.listen(socket_name):
            print(f"Failed to start local single-instance server: {server.errorString()}")

        received_queue = []
        main_window_instance = None

        def handle_new_connection():
            client_socket = server.nextPendingConnection()
            if client_socket:
                if client_socket.waitForReadyRead(1000):
                    data = client_socket.readAll().data().decode('utf-8')
                    if data:
                        if os.path.exists(data):
                            data = os.path.abspath(data)
                        nonlocal main_window_instance
                        if main_window_instance is not None:
                            main_window_instance.handle_torrent_file(data)
                        else:
                            received_queue.append(data)
                client_socket.disconnectFromServer()

        server.newConnection.connect(handle_new_connection)

        app = QApplication(sys.argv)
        app.setDesktopFileName("vortex")
        
        # Set AppUserModelID on Windows to ensure correct taskbar icon grouping
        if sys.platform == "win32":
            import ctypes
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("JarjisAlam.Vortex.BitTorrentClient")
            except Exception:
                pass
        
        # Attach the server to the QApplication to prevent garbage collection
        app._single_instance_server = server
        
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "vortex_logo_v2.png")
        if os.path.exists(logo_path):
            app.setWindowIcon(QIcon(logo_path))
            
        # Display splash loading screen
        splash = SplashScreen()
        if splash.exec() == SplashScreen.DialogCode.Accepted:
            window = MainWindow()
            main_window_instance = window
            window.show()
            
            # Process arguments passed to this initial instance
            if torrent_file:
                window.handle_torrent_file(torrent_file)
                
            # Process any torrent files received via socket during startup
            for pending in received_queue:
                window.handle_torrent_file(pending)
            received_queue.clear()
            
            sys.exit(app.exec())
        else:
            sys.exit(0)
    except Exception as e:
        print(f"Failed to start GUI: {e}")
        print("Falling back to CLI mode...")
        run_cli()

if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_gui()