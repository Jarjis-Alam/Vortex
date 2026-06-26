import queue
import threading
import time
import socket
import sys
import builtins
from peer_connector import connect_to_peer

def safe_print(*args, **kwargs):
    try:
        if not sys.is_finalizing():
            builtins.print(*args, **kwargs)
    except Exception:
        pass

print = safe_print

class PeerPool:
    def __init__(self, peers, torrent, pool_size=15):
        self.peers = peers
        self.torrent = torrent
        self.pool_size = pool_size
        
        self.active_peers = []  # list of dicts: {'peer': PeerConnection, 'pieces': list, 'in_use': bool, 'last_used': float}
        self.failed_peers = set()  # set of (ip, port)
        self.connecting = set()  # set of (ip, port)
        self.peer_stats = {}  # dictionary: ip:port -> statistics dict
        self.reconnect_count = 0
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self.running = True
        self.next_try_index = 0
        
        # Start supervisor thread
        self.supervisor_thread = threading.Thread(target=self._supervisor_loop, daemon=True)
        self.supervisor_thread.start()

    def _supervisor_loop(self):
        last_reset_time = 0
        while self.running:
            with self.lock:
                needed = self.pool_size - (len(self.active_peers) + len(self.connecting))
                
                now = time.time()
                if needed > 0 and self.peers and (now - last_reset_time > 15):
                    tries = 0
                    started_any = False
                    while tries < len(self.peers) and needed > 0:
                        ip, port = self.peers[self.next_try_index]
                        peer_idx = self.next_try_index
                        self.next_try_index = (self.next_try_index + 1) % len(self.peers)
                        
                        is_active = any(p['peer'].ip == ip and p['peer'].port == port for p in self.active_peers)
                        peer_tuple = (ip, port)
                        
                        if peer_tuple not in self.failed_peers and peer_tuple not in self.connecting and not is_active:
                            self.connecting.add(peer_tuple)
                            t = threading.Thread(target=self._connect_worker, args=(peer_tuple, peer_idx), daemon=True)
                            t.start()
                            needed -= 1
                            started_any = True
                        tries += 1
                        
                    if not started_any and len(self.active_peers) == 0 and len(self.connecting) == 0:
                        print("[PeerPool] All peers failed. Backing off 15 seconds before retrying.")
                        self.failed_peers.clear()
                        last_reset_time = now
            time.sleep(1)

    def _connect_worker(self, peer_tuple, peer_idx):
        try:
            peer, pieces, _ = connect_to_peer([peer_tuple], self.torrent, 0)
            with self.lock:
                if peer_tuple in self.connecting:
                    self.connecting.remove(peer_tuple)
                if peer is not None:
                    # Double check not already active
                    is_active = any(p['peer'].ip == peer.ip and p['peer'].port == peer.port for p in self.active_peers)
                    if not is_active:
                        self.active_peers.append({
                            'peer': peer,
                            'pieces': pieces,
                            'in_use': False,
                            'last_used': time.time()
                        })
                        self.reconnect_count += 1
                        print(f"[PeerPool] Connected to {peer.ip}:{peer.port}. Pool size: {len(self.active_peers)}")
                        self.cond.notify_all()
                    else:
                        try:
                            peer.sock.close()
                        except:
                            pass
                else:
                    self.failed_peers.add(peer_tuple)
        except Exception as e:
            print(f"[PeerPool] Error connecting to {peer_tuple}: {e}")
            with self.lock:
                if peer_tuple in self.connecting:
                    self.connecting.remove(peer_tuple)
                self.failed_peers.add(peer_tuple)

    def get_peer(self, piece_index, timeout=30):
        """
        Get an unused peer from the pool that has the specified piece_index.
        Blocks up to `timeout` seconds.
        """
        end_time = time.time() + timeout
        with self.lock:
            while self.running:
                # 1. Search for a peer that has the piece and is not in use
                best_peer_idx = -1
                for idx, p in enumerate(self.active_peers):
                    if not p['in_use']:
                        has_piece = p['pieces'] is None or (piece_index < len(p['pieces']) and p['pieces'][piece_index])
                        if has_piece:
                            best_peer_idx = idx
                            break
                
                # 2. Fallback: If no peer has it specifically, but we have unused peers, take any unused peer
                if best_peer_idx == -1:
                    for idx, p in enumerate(self.active_peers):
                        if not p['in_use']:
                            best_peer_idx = idx
                            break
                
                if best_peer_idx != -1:
                    self.active_peers[best_peer_idx]['in_use'] = True
                    return self.active_peers[best_peer_idx]['peer']
                
                remaining = end_time - time.time()
                if remaining <= 0:
                    return None
                
                self.cond.wait(remaining)
        return None

    def return_peer(self, peer):
        """Return a working peer to the pool."""
        with self.lock:
            for p in self.active_peers:
                if p['peer'] == peer:
                    p['in_use'] = False
                    p['last_used'] = time.time()
                    self.cond.notify_all()
                    break

    def report_dead(self, peer):
        """Remove a dead peer from the pool so background loop can replace it."""
        self.report_failure(peer, is_timeout=True)
        with self.lock:
            for idx, p in enumerate(self.active_peers):
                if p['peer'] == peer:
                    ip, port = peer.ip, peer.port
                    self.failed_peers.add((ip, port))
                    self.active_peers.pop(idx)
                    print(f"[PeerPool] Removed dead peer {ip}:{port}. Pool size: {len(self.active_peers)}")
                    try:
                        peer.sock.close()
                    except:
                        pass
                    self.cond.notify_all()
                    break

    def peer_has_piece(self, peer, piece_index):
        """Check if a peer has a specific piece index."""
        with self.lock:
            for p in self.active_peers:
                if p['peer'] == peer:
                    return p['pieces'] is None or (piece_index < len(p['pieces']) and p['pieces'][piece_index])
        return True

    def count_peers_with_piece(self, piece_index):
        """Count how many active peers have a specific piece index."""
        count = 0
        with self.lock:
            for p in self.active_peers:
                if p['pieces'] is None or (piece_index < len(p['pieces']) and p['pieces'][piece_index]):
                    count += 1
        return count

    def report_speed(self, peer, speed_mb, bytes_count):
        """Record performance statistics for a peer."""
        with self.lock:
            key = f"{peer.ip}:{peer.port}"
            if key not in self.peer_stats:
                self.peer_stats[key] = {
                    'downloaded_pieces': 0,
                    'total_bytes': 0,
                    'speeds': [],
                    'average_speed': 0.0,
                    'successes': 0,
                    'failures': 0,
                    'timeouts': 0
                }
            stats = self.peer_stats[key]
            stats['downloaded_pieces'] += 1
            stats['total_bytes'] += bytes_count
            stats['speeds'].append(speed_mb)
            if len(stats['speeds']) > 5:
                stats['speeds'].pop(0)
            stats['average_speed'] = sum(stats['speeds']) / len(stats['speeds'])
            stats['successes'] += 1

    def report_failure(self, peer, is_timeout=False):
        """Record a failure/timeout and prune poor performers from the pool."""
        with self.lock:
            key = f"{peer.ip}:{peer.port}"
            if key not in self.peer_stats:
                self.peer_stats[key] = {
                    'downloaded_pieces': 0,
                    'total_bytes': 0,
                    'speeds': [],
                    'average_speed': 0.0,
                    'successes': 0,
                    'failures': 0,
                    'timeouts': 0
                }
            stats = self.peer_stats[key]
            stats['failures'] += 1
            if is_timeout:
                stats['timeouts'] += 1

            # Prune peer if failures or timeouts become too high
            # (e.g. failures > 3 or timeout_count > 2 without any successes)
            if stats['failures'] > 3 or (stats['timeouts'] > 2 and stats['successes'] == 0):
                for idx, p in enumerate(self.active_peers):
                    if p['peer'] == peer:
                        ip, port = peer.ip, peer.port
                        self.failed_peers.add((ip, port))
                        self.active_peers.pop(idx)
                        print(f"[PeerPool] Pruned poor peer {ip}:{port} (Success: {stats['successes']}, Failures: {stats['failures']}, Timeouts: {stats['timeouts']}). Active pool: {len(self.active_peers)}")
                        try:
                            peer.sock.close()
                        except:
                            pass
                        self.cond.notify_all()
                        break

    def report_slow(self, peer):
        """Worker reported that this peer is too slow. Drop it immediately from the pool."""
        self.report_failure(peer, is_timeout=False)
        with self.lock:
            for idx, p in enumerate(self.active_peers):
                if p['peer'] == peer:
                    ip, port = peer.ip, peer.port
                    self.failed_peers.add((ip, port))
                    self.active_peers.pop(idx)
                    print(f"[PeerPool] Dropped slow peer {ip}:{port} on worker report. Active pool: {len(self.active_peers)}")
                    try:
                        peer.sock.close()
                    except:
                        pass
                    self.cond.notify_all()
                    break

    def get_peer_stats(self, peer):
        """Get stats dict for a given peer."""
        with self.lock:
            key = f"{peer.ip}:{peer.port}"
            return self.peer_stats.get(key)

    def stop(self):
        self.running = False
        with self.lock:
            for p in self.active_peers:
                try:
                    p['peer'].sock.close()
                except:
                    pass
            self.active_peers.clear()
            self.cond.notify_all()
