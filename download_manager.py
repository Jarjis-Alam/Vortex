import hashlib
import os
import time
import json
import socket
import threading
import queue
import sys
import builtins

def safe_print(*args, **kwargs):
    try:
        if not sys.is_finalizing():
            builtins.print(*args, **kwargs)
    except Exception:
        pass

print = safe_print

from piece_downloader import download_piece
from peer_pool import PeerPool


def verify_piece(piece, expected_hash):
    """Verify a piece matches its SHA1 hash."""
    piece_hash = hashlib.sha1(piece).digest()
    return piece_hash == expected_hash


class DownloadManager:
    """
    Multi-peer parallel download manager.
    Uses worker threads to download different
    pieces from different peers simultaneously.
    """

    def __init__(
        self,
        peers,
        torrent,
        output_file,
        num_workers=5
    ):

        self.peers = peers
        self.torrent = torrent
        self.output_file = output_file
        self.num_workers = num_workers

        self.piece_count = (
            torrent.get_piece_count()
        )
        self.piece_length = (
            torrent.get_piece_length()
        )
        self.total_size = (
            torrent.get_size()
        )
        self.progress_file = "progress.json"

        # Dynamic Rarest-First Scheduler state
        self.remaining_pieces = set()
        self.remaining_lock = threading.Lock()

        # Completed pieces (thread-safe set)
        self.completed = set()
        self.completed_lock = threading.Lock()

        # File write lock
        self.file_lock = threading.Lock()
        self.output_fd = None

        # Stats
        self.session_bytes = 0
        self.hash_failures = 0
        self.stats_lock = threading.Lock()
        self.start_time = None
        self.shutdown_event = threading.Event()

        # Print lock
        self.print_lock = threading.Lock()

        # Pause state
        self.is_paused = False
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.log_callback = None

        # Initialize Peer Pool
        pool_size = max(15, self.num_workers + 5)
        self.pool = PeerPool(self.peers, self.torrent, pool_size=pool_size)

    def log(self, msg):
        """Thread-safe print."""
        with self.print_lock:
            print(msg)
            if self.log_callback:
                try:
                    self.log_callback(msg)
                except:
                    pass

    def pause(self):
        """Pause the download process."""
        self.is_paused = True
        self.pause_event.clear()
        self.log("Download PAUSED")

    def resume(self):
        """Resume the download process."""
        self.is_paused = False
        self.pause_event.set()
        self.log("Download RESUMED")

    def load_progress(self):
        """Load completed pieces from file."""

        if (
            os.path.exists(self.progress_file)
            and os.path.exists(
                self.output_file
            )
        ):
            with open(
                self.progress_file, "r"
            ) as f:
                progress = json.load(f)

            completed = progress.get(
                "completed", []
            )

            # Support old format
            if not completed:
                last = progress.get(
                    "last_piece", -1
                )
                completed = list(
                    range(last + 1)
                )

            self.completed = set(completed)

            self.log(
                f"Resuming: "
                f"{len(self.completed)} "
                f"pieces already done"
            )

    def save_progress(self):
        """Save completed pieces to file."""
        with self.completed_lock:
            completed = sorted(
                self.completed
            )

        with open(
            self.progress_file, "w"
        ) as f:
            json.dump(
                {
                    "completed": completed,
                    "last_piece": (
                        max(completed)
                        if completed
                        else -1
                    )
                },
                f
            )

    def verify_existing_pieces(self):
        """Verify hashes of already downloaded pieces on startup."""
        if not self.completed or not os.path.exists(self.output_file):
            return
        
        self.log("Performing startup integrity check on completed pieces...")
        verified = set()
        
        try:
            with open(self.output_file, "rb") as f:
                for piece_index in sorted(self.completed):
                    offset = piece_index * self.piece_length
                    f.seek(offset)
                    piece_data = f.read(self.torrent.get_piece_size(piece_index))
                    
                    expected_hash = self.torrent.get_piece_hash(piece_index)
                    if verify_piece(piece_data, expected_hash):
                        verified.add(piece_index)
                    else:
                        self.log(f"Piece {piece_index} failed startup verification. Will redownload.")
        except Exception as e:
            self.log(f"Error during startup integrity check: {e}")
            verified = set()
                    
        self.completed = verified
        self.save_progress()
        self.log(f"Integrity check complete. {len(self.completed)} verified pieces.")

    def get_next_piece(self, peer):
        """Select the rarest uncompleted piece that this peer has."""
        with self.remaining_lock:
            candidates = []
            for p_idx in self.remaining_pieces:
                if self.pool.peer_has_piece(peer, p_idx):
                    candidates.append(p_idx)
            
            if not candidates:
                return None
            
            # Count how many active peers have each candidate piece index
            rarity_scores = {}
            for p_idx in candidates:
                rarity_scores[p_idx] = self.pool.count_peers_with_piece(p_idx)
            
            # Sort by rarity (ascending score, rarer first)
            candidates.sort(key=lambda x: rarity_scores[x])
            
            selected = candidates[0]
            self.remaining_pieces.remove(selected)
            return selected

    def requeue_piece(self, piece_index):
        """Put a failed piece back into the scheduler's remaining list."""
        with self.remaining_lock:
            self.remaining_pieces.add(piece_index)

    def worker(self, worker_id):
        """
        Worker thread: gets peer from PeerPool
        and downloads pieces from the scheduler.
        """
        self.log(f"W{worker_id}: Worker started")
        peer = None
        consecutive_failures = 0

        while not self.shutdown_event.is_set():
            # If paused, wait here until resume
            self.pause_event.wait()
            if self.shutdown_event.is_set():
                break

            # Check if target is already reached globally
            with self.completed_lock:
                if len(self.completed) >= self.target_pieces:
                    break

            # 1. Get a peer if we don't have one
            if peer is None:
                peer = self.pool.get_peer(-1, timeout=5)
                if self.shutdown_event.is_set():
                    break
                if peer is None:
                    # No peer available yet, sleep and retry
                    time.sleep(1)
                    continue

            # 2. Select the next piece for this peer
            piece_index = self.get_next_piece(peer)
            if piece_index is None:
                # Peer has no pieces that we need. Return peer and look for another one.
                self.pool.return_peer(peer)
                peer = None
                
                with self.remaining_lock:
                    if not self.remaining_pieces:
                        break
                
                time.sleep(1)
                continue

            piece_size = self.torrent.get_piece_size(piece_index)

            # Adaptive Pipelining based on peer speed stats
            peer_stats = self.pool.get_peer_stats(peer)
            if peer_stats:
                avg_speed = peer_stats['average_speed']  # in MB/s
                if avg_speed < 0.05:     # < 50 KB/s
                    pipeline_size = 8
                elif avg_speed > 2.0:    # > 2 MB/s
                    pipeline_size = 128
                elif avg_speed > 0.5:    # > 500 KB/s
                    pipeline_size = 64
                else:
                    pipeline_size = 32
            else:
                pipeline_size = 32

            # Try downloading
            piece = None
            t0 = time.time()
            try:
                piece = download_piece(
                    peer,
                    piece_index,
                    piece_size,
                    pipeline_size=pipeline_size
                )
            except (
                socket.timeout,
                socket.error,
                ConnectionError,
                OSError
            ) as e:
                self.log(
                    f"W{worker_id}: "
                    f"Error on piece "
                    f"{piece_index}: {e}"
                )

            if piece is None:
                self.log(f"W{worker_id}: Failed to download piece {piece_index}. Reporting dead peer.")
                self.pool.report_dead(peer)
                peer = None

                self.requeue_piece(piece_index)

                consecutive_failures += 1
                if consecutive_failures >= 5:
                    self.log(f"W{worker_id}: Too many failures, exiting worker.")
                    break
                continue

            consecutive_failures = 0
            download_elapsed = time.time() - t0

            # Verify hash
            t_verify_start = time.time()
            expected_hash = self.torrent.get_piece_hash(piece_index)
            verified = verify_piece(piece, expected_hash)
            verify_elapsed = time.time() - t_verify_start

            if not verified:
                self.log(f"W{worker_id}: ✗ Piece {piece_index} hash mismatch. Reporting dead peer.")
                with self.stats_lock:
                    self.hash_failures += 1
                self.pool.report_dead(peer)
                peer = None

                self.requeue_piece(piece_index)
                continue

            # Write to file at correct offset
            offset = piece_index * self.piece_length

            t_write_start = time.time()
            with self.file_lock:
                self.output_fd.seek(offset)
                self.output_fd.write(piece)
                self.output_fd.flush()
            write_elapsed = time.time() - t_write_start

            with self.completed_lock:
                self.completed.add(piece_index)
                count = len(self.completed)

            with self.stats_lock:
                self.session_bytes += len(piece)
                session_bytes = self.session_bytes

            # Slow peer detection: if average speed for this piece is < 50 KB/s
            speed_mb = (len(piece) / (1024 * 1024)) / download_elapsed if download_elapsed > 0 else 0
            self.pool.report_speed(peer, speed_mb, len(piece))
            if speed_mb < 0.05 and piece_size > 65536:
                self.log(f"W{worker_id}: Peer {peer.ip} slow ({speed_mb*1024:.1f} KB/s). Dropping.")
                self.pool.report_slow(peer)
                peer = None

            # Progress output
            total_elapsed = time.time() - self.start_time
            mb = session_bytes / (1024 * 1024)
            avg_speed = mb / total_elapsed if total_elapsed > 0 else 0
            percent = count * 100 / self.piece_count

            # Timing and metrics logging
            piece_mb = piece_size / (1024 * 1024)
            self.log(
                f"Piece {piece_index}: {piece_mb:.2f} MB in {download_elapsed:.2f}s "
                f"({piece_mb/download_elapsed if download_elapsed > 0 else 0:.2f} MB/s) | "
                f"Pipeline: {pipeline_size} | "
                f"Verify: {verify_elapsed:.4f}s | "
                f"Write: {write_elapsed:.4f}s | "
                f"Progress: {count}/{self.piece_count} ({percent:.1f}%) | "
                f"Avg Speed: {avg_speed:.2f} MB/s"
            )

            # Save progress every 25 pieces
            if count % 25 == 0:
                self.save_progress()

        # Clean up this worker's peer
        if peer is not None:
            self.pool.return_peer(peer)

    def stats_printer_loop(self):
        """Periodically print client performance and pool health benchmarks."""
        while not self.shutdown_event.is_set():
            for _ in range(50):
                if self.shutdown_event.is_set():
                    return
                time.sleep(0.1)

            with self.completed_lock:
                completed_count = len(self.completed)
            with self.pool.lock:
                peers_connected = len(self.pool.active_peers)
                peers_active = sum(1 for p in self.pool.active_peers if p['in_use'])
                reconnects = self.pool.reconnect_count

            total_elapsed = time.time() - self.start_time
            with self.stats_lock:
                downloaded_mb = self.session_bytes / (1024 * 1024)
                hash_failures = self.hash_failures

            if self.is_paused:
                speed = 0.0
                status_str = " (Paused)"
            else:
                speed = downloaded_mb / total_elapsed if total_elapsed > 0 else 0
                status_str = ""

            self.log(
                f"\n[STATS] Peers: {peers_connected} | Active: {peers_active} | "
                f"Downloaded: {downloaded_mb:.2f} MB | Speed: {speed:.2f} MB/s{status_str} | "
                f"Verified: {completed_count}/{self.piece_count} | "
                f"Hash Failures: {hash_failures} | Reconnects: {reconnects}"
            )

    def download(self, target=None):
        """
        Download pieces using multiple peers.

        Args:
            target: Number of pieces to
                download (None = all)

        Returns:
            True if successful
        """

        if target is None:
            target = self.piece_count

        self.target_pieces = target

        self.load_progress()
        self.verify_existing_pieces()

        # Populate remaining pieces for the scheduler
        for i in range(target):
            if i not in self.completed:
                self.remaining_pieces.add(i)

        enqueued = len(self.remaining_pieces)

        if enqueued == 0:
            self.log(
                "All pieces already "
                "downloaded!"
            )
            self.pool.stop()
            return True

        self.log(
            f"Target: {target} pieces, "
            f"{enqueued} remaining"
        )
        self.log(
            f"Workers: {self.num_workers}"
        )

        # Pre-allocate output file
        if not os.path.exists(
            self.output_file
        ):
            self.log(
                "Pre-allocating file..."
            )
            with open(
                self.output_file, "wb"
            ) as f:
                f.seek(self.total_size - 1)
                f.write(b'\0')

        self.output_fd = open(
            self.output_file, "r+b"
        )
        self.start_time = time.time()
        self.shutdown_event.clear()

        # Launch stats printer thread
        stats_thread = threading.Thread(
            target=self.stats_printer_loop,
            daemon=True
        )
        stats_thread.start()

        # Launch worker threads
        threads = []

        for i in range(self.num_workers):

            t = threading.Thread(
                target=self.worker,
                args=(i,),
                daemon=True
            )
            threads.append(t)
            t.start()

        # Wait for all workers
        for t in threads:
            t.join()

        # Stop stats thread and peer pool
        self.shutdown_event.set()
        self.pool.stop()

        self.output_fd.close()
        self.save_progress()

        # Final stats
        with self.completed_lock:
            count = len(self.completed)

        elapsed = (
            time.time() - self.start_time
        )
        mb = (
            self.session_bytes
            / (1024 * 1024)
        )
        speed = (
            mb / elapsed
            if elapsed > 0
            else 0
        )

        self.log(f"\n{'=' * 40}")
        self.log(
            f"Downloaded: {count}/{target}"
        )
        self.log(
            f"Size: {mb:.1f} MB "
            f"in {elapsed:.1f}s"
        )
        self.log(
            f"Speed: {speed:.2f} MB/s"
        )

        if count >= target:
            if target == self.piece_count:
                if os.path.exists(
                    self.progress_file
                ):
                    os.remove(
                        self.progress_file
                    )
            self.log(
                "✓ Download complete!"
            )
            return True

        return False
