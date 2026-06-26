import hashlib
import os
import time
import json
import socket
import sys

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

from piece_downloader import download_piece
from peer_connector import connect_to_peer


def verify_piece(piece, expected_hash):
    """Verify a piece matches its SHA1 hash."""
    piece_hash = hashlib.sha1(piece).digest()
    return piece_hash == expected_hash


def download_all_pieces(
    peers,
    torrent,
    output_file
):
    """
    Download all pieces and write to output
    file. Handles resume, retry, reconnection,
    and speed tracking.

    Args:
        peers: List of (ip, port) tuples
        torrent: Torrent metadata object
        output_file: Path to write content

    Returns:
        True if successful, False otherwise
    """

    piece_count = torrent.get_piece_count()
    piece_length = torrent.get_piece_length()
    info_hash = torrent.get_info_hash()
    progress_file = os.path.join(get_vortex_dir(), "progress", f"{info_hash}.json")

    # Resume support
    start_piece = 0

    if (
        os.path.exists(progress_file)
        and os.path.exists(output_file)
    ):
        with open(progress_file, "r") as pf:
            progress = json.load(pf)
            start_piece = (
                progress["last_piece"] + 1
            )
        print(
            f"Resuming from piece "
            f"{start_piece}"
        )

    remaining = piece_count - start_piece

    print(
        f"Downloading {piece_count} pieces "
        f"({remaining} remaining)..."
    )

    # Connect to first peer
    peer, _, peer_index = connect_to_peer(
        peers,
        torrent,
        0
    )

    if peer is None:
        print("No peers available")
        return False

    # Open file for writing or resuming
    if start_piece > 0:
        f = open(output_file, "r+b")
        f.seek(start_piece * piece_length)
    else:
        f = open(output_file, "wb")

    start_time = time.time()
    session_bytes = 0

    try:

        for piece_index in range(
            start_piece,
            500  # TEST: change to piece_count
        ):

            piece_size = (
                torrent.get_piece_size(
                    piece_index
                )
            )

            percent = (
                (piece_index + 1)
                * 100
                / piece_count
            )

            elapsed = (
                time.time() - start_time
            )

            mb_downloaded = (
                session_bytes
                / (1024 * 1024)
            )

            speed = (
                mb_downloaded / elapsed
                if elapsed > 0
                else 0
            )

            print(
                f"\n[{piece_index + 1}/"
                f"{piece_count}] "
                f"{percent:.2f}% - "
                f"{speed:.2f} MB/s"
            )

            # Retry with reconnection
            piece = None

            for attempt in range(3):

                try:
                    piece = download_piece(
                        peer,
                        piece_index,
                        piece_size
                    )

                    if piece is not None:
                        break

                except (
                    socket.timeout,
                    socket.error,
                    ConnectionError,
                    OSError
                ) as e:
                    print(
                        f"Connection error: "
                        f"{e}"
                    )

                # Reconnect to next peer
                print(
                    f"Attempt "
                    f"{attempt + 1}/3 "
                    f"failed, reconnecting..."
                )

                try:
                    peer.sock.close()
                except Exception:
                    pass

                peer, _, peer_index = (
                    connect_to_peer(
                        peers,
                        torrent,
                        peer_index
                    )
                )

                if peer is None:
                    # Wrap around to start
                    peer, _, peer_index = (
                        connect_to_peer(
                            peers,
                            torrent,
                            0
                        )
                    )

                if peer is None:
                    print(
                        "No peers available"
                    )
                    return False

            if piece is None:
                print(
                    f"Failed piece "
                    f"{piece_index} after "
                    f"3 attempts"
                )
                return False

            expected_hash = (
                torrent.get_piece_hash(
                    piece_index
                )
            )

            if verify_piece(
                piece, expected_hash
            ):
                print(
                    f"✓ Piece {piece_index} "
                    f"verified"
                )

                f.write(piece)
                f.flush()
                os.fsync(f.fileno())
                session_bytes += len(piece)

                # Save progress
                with open(
                    progress_file, "w"
                ) as pf:
                    json.dump(
                        {
                            "last_piece":
                                piece_index
                        },
                        pf
                    )

            else:
                piece_hash = hashlib.sha1(
                    piece
                ).digest()
                print(
                    f"✗ Piece {piece_index} "
                    f"hash mismatch!"
                )
                print(
                    f"  Got:      "
                    f"{piece_hash.hex()}"
                )
                print(
                    f"  Expected: "
                    f"{expected_hash.hex()}"
                )
                return False

    finally:
        f.close()
        try:
            peer.sock.close()
        except Exception:
            pass

    # Clean up on completion
    if os.path.exists(progress_file):
        os.remove(progress_file)

    elapsed = time.time() - start_time
    mb_total = (
        session_bytes / (1024 * 1024)
    )
    avg_speed = (
        mb_total / elapsed
        if elapsed > 0
        else 0
    )

    print(
        f"\n✓ All {piece_count} pieces "
        f"downloaded!"
    )
    print(
        f"  Total: {mb_total:.1f} MB "
        f"in {elapsed:.1f}s"
    )
    print(
        f"  Average: {avg_speed:.2f} MB/s"
    )
    return True