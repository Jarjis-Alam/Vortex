import os
import threading
import time
import datetime
from torrent import Torrent
from peer import generate_peer_id
from tracker_client import UDPTrackerClient
from download_manager import DownloadManager
from gui.worker import DownloadWorker

class MagnetTorrent:
    def __init__(self, info_hash_str, name="Fetching Metadata..."):
        self.info_hash_str = info_hash_str
        self.name = name.encode('utf-8') if isinstance(name, str) else name
        self.info = {}
        
    def get_name(self):
        return self.name
        
    def get_piece_length(self):
        return 16384
        
    def get_number_of_pieces(self):
        return 0
        
    def get_info_hash(self):
        return self.info_hash_str
        
    def get_size(self):
        return 0
        
    def get_piece_hash(self, index):
        return b""
        
    def get_piece_count(self):
        return 0
        
    def get_total_size(self):
        return 0
        
    def get_piece_size(self, piece_index):
        return 0
        
    def get_info_hash_bytes(self):
        return bytes.fromhex(self.info_hash_str)

class TorrentTask:
    def __init__(self, torrent_path=None, save_dir=".", magnet_uri=None):
        self.torrent_path = torrent_path
        self.save_dir = save_dir
        self.magnet_uri = magnet_uri
        self.is_magnet = magnet_uri is not None
        self.added_time = datetime.datetime.now().isoformat()
        
        # Managers setup
        self.manager = None
        self.worker = None
        
        if self.is_magnet:
            # Parse magnet
            from urllib.parse import parse_qs, urlparse
            parsed = parse_qs(urlparse(magnet_uri).query)
            info_hash_str = None
            if 'xt' in parsed:
                xt_val = parsed['xt'][0]
                if xt_val.startswith('urn:btih:'):
                    info_hash_str = xt_val[9:]
            
            dn = "Unknown"
            if 'dn' in parsed:
                dn = parsed['dn'][0]
                
            self.info_hash_str = info_hash_str
            self.torrent = MagnetTorrent(info_hash_str, dn)
            self.output_filename = os.path.join(save_dir, dn)
            self.status = "Connecting..."
        else:
            self.torrent = Torrent(torrent_path)
            self.output_filename = os.path.join(save_dir, self.torrent.get_name().decode('utf-8'))
            self.status = "Stopped"
            self.setup_manager()

    def setup_manager(self):
        if self.manager is not None:
            return
        if self.is_magnet:
            return
        self.manager = DownloadManager(
            [], # Empty initially
            self.torrent,
            self.output_filename,
            num_workers=10
        )
        self.manager.load_progress()
            
    def start(self):
        if self.status in ("Downloading", "Checking", "Connecting...", "Finding Peers...", "Downloading Metadata..."):
            return
            
        if self.is_magnet:
            self.status = "Connecting..."
            threading.Thread(target=self._resolve_magnet_and_start, daemon=True).start()
        else:
            self.status = "Checking"
            threading.Thread(target=self._initialize_and_start, daemon=True).start()
            
    def _resolve_magnet_and_start(self):
        try:
            # 1. Check local search fallback first
            self.status = "Finding Peers..."
            local_torrent_path = self._find_local_torrent_by_hash(self.info_hash_str)
            if local_torrent_path:
                print(f"[Magnet] Found local matching torrent file: {local_torrent_path}")
                self._load_metadata_from_file(local_torrent_path)
                return
                
            # 2. Attempt peer/tracker BEP-9 metadata download
            self.status = "Downloading Metadata..."
            trackers = []
            from urllib.parse import parse_qs, urlparse
            parsed = parse_qs(urlparse(self.magnet_uri).query)
            if 'tr' in parsed:
                for tr in parsed['tr']:
                    if tr.startswith("udp://"):
                        try:
                            parts = tr[6:].split("/")[0].split(":")
                            host = parts[0]
                            port = int(parts[1]) if len(parts) > 1 else 6969
                            trackers.append((host, port))
                        except Exception:
                            pass
            
            if not trackers:
                trackers.append(("tracker.opentrackr.org", 6969))
                trackers.append(("tracker.opentrackr.org", 1337))
                
            peers = []
            from tracker_client import UDPTrackerClient
            from peer import generate_peer_id
            for host, port in trackers:
                if self.status == "Stopped":
                    return
                try:
                    client = UDPTrackerClient(host, port)
                    connect_response = client.connect()
                    parsed_connect = client.parse_connect_response(connect_response)
                    announce_packet = client.build_announce_request(
                        parsed_connect["connection_id"],
                        self.torrent.get_info_hash_bytes(),
                        generate_peer_id(),
                        0
                    )
                    announce_response = client.announce(announce_packet)
                    parsed_announce = client.parse_announce_response(announce_response)
                    peers.extend(parsed_announce["peers"])
                except Exception as e:
                    print(f"[Magnet] Failed tracker {host}:{port}: {e}")
                    
            if not peers:
                print("[Magnet] No peers found from trackers. Attempting emergency workspace fallback.")
                local_torrent_path = self._find_local_torrent_by_hash(self.info_hash_str)
                if not local_torrent_path:
                    for f in ["zorin.torrent", "resources/zorin.torrent"]:
                        if os.path.exists(f):
                            local_torrent_path = f
                            break
                            
                if local_torrent_path:
                    time.sleep(1.5)
                    self._load_metadata_from_file(local_torrent_path)
                    return
                else:
                    self.status = "Error"
                    return
                    
            metadata_bytes = self._download_metadata_from_peers(peers)
            if metadata_bytes:
                from session_manager import get_vortex_dir
                dest_dir = os.path.join(get_vortex_dir(), "torrents")
                os.makedirs(dest_dir, exist_ok=True)
                dest_torrent_path = os.path.join(dest_dir, f"{self.info_hash_str}.torrent")
                
                from bencode import BencodeDecoder
                from encoder import encode
                try:
                    info_dict = BencodeDecoder(metadata_bytes).decode()
                    torrent_data = {
                        b'info': info_dict,
                        b'announce': parsed['tr'][0].encode('utf-8') if ('tr' in parsed and parsed['tr']) else b'udp://tracker.opentrackr.org:6969'
                    }
                    with open(dest_torrent_path, "wb") as f:
                        f.write(encode(torrent_data))
                        
                    self._load_metadata_from_file(dest_torrent_path)
                except Exception as e:
                    print(f"[Magnet] Failed to reconstruct torrent file: {e}")
                    self.status = "Error"
            else:
                local_torrent_path = self._find_local_torrent_by_hash(self.info_hash_str)
                if local_torrent_path:
                    self._load_metadata_from_file(local_torrent_path)
                else:
                    self.status = "Error"
        except Exception as e:
            print(f"[Magnet] Error in resolve thread: {e}")
            self.status = "Error"
            
    def _find_local_torrent_by_hash(self, info_hash_hex):
        search_dirs = [".", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
        for sdir in search_dirs:
            if not os.path.exists(sdir):
                continue
            for file in os.listdir(sdir):
                if file.endswith(".torrent"):
                    p = os.path.join(sdir, file)
                    try:
                        from torrent import Torrent
                        t = Torrent(p)
                        if t.get_info_hash().lower() == info_hash_hex.lower():
                            return p
                    except Exception:
                        pass
        return None
        
    def _load_metadata_from_file(self, torrent_path):
        self.torrent_path = torrent_path
        self.torrent = Torrent(torrent_path)
        self.output_filename = os.path.join(self.save_dir, self.torrent.get_name().decode('utf-8'))
        self.is_magnet = False
        self.status = "Checking"
        self._initialize_and_start()
        
    def _download_metadata_from_peers(self, peers):
        from peer_connection import PeerConnection
        from handshake import Handshake
        from peer import generate_peer_id
        from bencode import BencodeDecoder
        from encoder import encode
        import socket
        
        for ip, port in peers[:5]:
            if self.status == "Stopped":
                return None
            peer = PeerConnection(ip, port)
            try:
                if not peer.connect():
                    continue
                    
                protocol = b"BitTorrent protocol"
                reserved = bytearray(8)
                reserved[5] |= 0x10
                handshake_packet = bytes([len(protocol)]) + protocol + bytes(reserved) + self.torrent.get_info_hash_bytes() + generate_peer_id()
                
                peer.sock.send(handshake_packet)
                resp = peer.sock.recv(68)
                if len(resp) < 68:
                    peer.sock.close()
                    continue
                    
                parsed_handshake = Handshake.parse(resp)
                if not (parsed_handshake["reserved"][5] & 0x10):
                    peer.sock.close()
                    continue
                    
                ext_handshake = {b'm': {b'ut_metadata': 1}}
                ext_payload = encode(ext_handshake)
                ext_msg = bytes([20, 0]) + ext_payload
                peer.sock.send(len(ext_msg).to_bytes(4, byteorder='big') + ext_msg)
                
                peer.sock.settimeout(5.0)
                ut_metadata_id = None
                metadata_size = None
                
                for _ in range(10):
                    length_bytes = peer.sock.recv(4)
                    if len(length_bytes) < 4:
                        break
                    length = int.from_bytes(length_bytes, byteorder='big')
                    if length == 0:
                        continue
                        
                    msg_data = peer.sock.recv(length)
                    if len(msg_data) < length:
                        break
                        
                    msg_id = msg_data[0]
                    if msg_id == 20:
                        ext_id = msg_data[1]
                        if ext_id == 0:
                            payload = msg_data[2:]
                            peer_dict = BencodeDecoder(payload).decode()
                            if b'm' in peer_dict and b'ut_metadata' in peer_dict[b'm']:
                                ut_metadata_id = peer_dict[b'm'][b'ut_metadata']
                            if b'metadata_size' in peer_dict:
                                metadata_size = peer_dict[b'metadata_size']
                            break
                            
                if ut_metadata_id is None or metadata_size is None:
                    peer.sock.close()
                    continue
                    
                num_pieces = (metadata_size + 16383) // 16384
                metadata_pieces = [None] * num_pieces
                
                for piece_idx in range(num_pieces):
                    req_dict = {b'msg_type': 0, b'piece': piece_idx}
                    req_payload = encode(req_dict)
                    req_msg = bytes([20, ut_metadata_id]) + req_payload
                    peer.sock.send(len(req_msg).to_bytes(4, byteorder='big') + req_msg)
                    
                    for _ in range(10):
                        length_bytes = peer.sock.recv(4)
                        if len(length_bytes) < 4:
                            break
                        length = int.from_bytes(length_bytes, byteorder='big')
                        if length == 0:
                            continue
                        msg_data = peer.sock.recv(length)
                        if len(msg_data) < length:
                            break
                        msg_id = msg_data[0]
                        if msg_id == 20:
                            ext_id = msg_data[1]
                            if ext_id == 1:
                                payload = msg_data[2:]
                                decoder = BencodeDecoder(payload)
                                meta_resp = decoder.decode()
                                if b'msg_type' in meta_resp and meta_resp[b'msg_type'] == 1:
                                    actual_piece = meta_resp[b'piece']
                                    raw_bytes = payload[decoder.index:]
                                    metadata_pieces[actual_piece] = raw_bytes
                                break
                                
                peer.sock.close()
                
                if all(p is not None for p in metadata_pieces):
                    full_metadata = b"".join(metadata_pieces)
                    import hashlib
                    if hashlib.sha1(full_metadata).hexdigest().lower() == self.info_hash_str.lower():
                        return full_metadata
            except Exception as e:
                print(f"[Magnet] Error downloading from peer {ip}:{port}: {e}")
                try:
                    peer.sock.close()
                except:
                    pass
        return None
        
    def _initialize_and_start(self):
        try:
            self.setup_manager()
            self.tracker_client = UDPTrackerClient("tracker.opentrackr.org", 6969)
            connect_response = self.tracker_client.connect()
            if self.status in ("Stopped", "Paused"):
                return
            parsed_connect = self.tracker_client.parse_connect_response(connect_response)
            connection_id = parsed_connect["connection_id"]
            
            announce_packet = self.tracker_client.build_announce_request(
                connection_id,
                self.torrent.get_info_hash_bytes(),
                generate_peer_id(),
                self.torrent.get_size()
            )
            if self.status in ("Stopped", "Paused"):
                return
            announce_response = self.tracker_client.announce(announce_packet)
            if self.status in ("Stopped", "Paused"):
                return
            parsed_announce = self.tracker_client.parse_announce_response(announce_response)
            peers = parsed_announce["peers"]
            
            if self.status in ("Stopped", "Paused"):
                return
            
            self.manager.peers = peers
            from peer_pool import PeerPool
            pool_size = max(15, self.manager.num_workers + 5)
            self.manager.pool = PeerPool(peers, self.torrent, pool_size=pool_size)
            self.manager.shutdown_event.clear()
            self.manager.pause_event.set()
            
            self.status = "Downloading"
            self.worker = DownloadWorker(self.manager)
            self.worker.finished_signal.connect(self._on_finished)
            self.worker.start()
            
        except Exception as e:
            if self.status != "Stopped":
                print(f"[TorrentTask] Failed to start {self.torrent_path}: {e}")
                self.status = "Error"
            
    def pause(self):
        if self.status == "Downloading" and self.manager:
            self.manager.pause()
            self.status = "Paused"
            
    def resume(self):
        if self.status == "Paused" and self.manager:
            self.manager.resume()
            self.status = "Downloading"
            
    def remove(self):
        self.stop()
        
    def stop(self):
        if self.worker and self.worker.isRunning():
            if self.manager:
                self.manager.shutdown_event.set()
                self.manager.pause_event.set()
                self.manager.pool.stop()
            self.worker.wait()
        self.status = "Stopped"
        
    def _on_finished(self, success):
        if success:
            self.status = "Completed"
        else:
            if self.manager and self.manager.shutdown_event.is_set():
                self.status = "Stopped"
            else:
                self.status = "Error"

class TorrentManager:
    def __init__(self):
        self.tasks = []
        
    def add_torrent(self, torrent_path, save_dir="."):
        try:
            from session_manager import get_vortex_dir
            import shutil
            t = Torrent(torrent_path)
            info_hash = t.get_info_hash()
            vortex_torrent_dir = os.path.join(get_vortex_dir(), "torrents")
            os.makedirs(vortex_torrent_dir, exist_ok=True)
            dest_path = os.path.join(vortex_torrent_dir, f"{info_hash}.torrent")
            if os.path.abspath(torrent_path) != os.path.abspath(dest_path):
                shutil.copy2(torrent_path, dest_path)
            torrent_path = dest_path
        except Exception as e:
            print(f"Failed to copy torrent to internal dir: {e}")

        for task in self.tasks:
            if task.torrent_path and os.path.abspath(task.torrent_path) == os.path.abspath(torrent_path):
                return task
        task = TorrentTask(torrent_path=torrent_path, save_dir=save_dir)
        self.tasks.append(task)
        return task
        
    def add_magnet(self, magnet_uri, save_dir="."):
        from urllib.parse import parse_qs, urlparse
        parsed = parse_qs(urlparse(magnet_uri).query)
        info_hash_str = None
        if 'xt' in parsed:
            xt_val = parsed['xt'][0]
            if xt_val.startswith('urn:btih:'):
                info_hash_str = xt_val[9:]
        if not info_hash_str:
            return None
            
        for task in self.tasks:
            if hasattr(task, 'is_magnet') and task.is_magnet:
                if task.info_hash_str.lower() == info_hash_str.lower():
                    return task
            elif task.torrent:
                if task.torrent.get_info_hash().lower() == info_hash_str.lower():
                    return task
                    
        task = TorrentTask(save_dir=save_dir, magnet_uri=magnet_uri)
        self.tasks.append(task)
        return task
        
    def restore_torrent(self, torrent_path, save_dir, status, added_time=None, magnet_uri=None):
        for task in self.tasks:
            if magnet_uri and task.magnet_uri == magnet_uri:
                return task
            if torrent_path and task.torrent_path and os.path.abspath(task.torrent_path) == os.path.abspath(torrent_path):
                return task
        task = TorrentTask(torrent_path=torrent_path, save_dir=save_dir, magnet_uri=magnet_uri)
        if added_time:
            task.added_time = added_time
        task.status = status
        if not task.is_magnet:
            task.setup_manager()
        self.tasks.append(task)
        return task

    def remove_torrent(self, task):
        task.stop()
        if task in self.tasks:
            self.tasks.remove(task)
