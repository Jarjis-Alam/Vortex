import socket
import sys
import builtins

def safe_print(*args, **kwargs):
    try:
        if not sys.is_finalizing():
            builtins.print(*args, **kwargs)
    except Exception:
        pass

print = safe_print

from peer_connection import PeerConnection
from handshake import Handshake
from bitfield import parse_bitfield
from message import interested
from protocol import read_message
from peer import generate_peer_id


def connect_to_peer(
    peers,
    torrent,
    start_index=0
):
    """
    Try connecting to peers starting from
    start_index. Performs handshake and waits
    for unchoke.

    Returns:
        (peer, next_index) on success
        (None, next_index) on failure
    """

    for i in range(
        start_index,
        len(peers)
    ):
        ip, port = peers[i]

        print(
            f"\n[Peer {i + 1}/"
            f"{len(peers)}] "
            f"Trying: {ip}:{port}"
        )

        temp_peer = PeerConnection(
            ip,
            port
        )

        try:

            if not temp_peer.connect():
                continue

            # Handshake
            packet = Handshake(
                torrent.get_info_hash_bytes(),
                generate_peer_id()
            ).build()

            temp_peer.sock.send(packet)

            response = temp_peer.sock.recv(
                68
            )

            if len(response) < 68:
                print("Bad handshake response")
                temp_peer.sock.close()
                continue

            parsed = Handshake.parse(
                response
            )

            print(
                f"Peer: {parsed['peer_id']}"
            )

            # Bitfield
            message = temp_peer.sock.recv(
                4096
            )

            if (
                len(message) < 5
                or message[4] != 5
            ):
                print(
                    "No bitfield received"
                )
                temp_peer.sock.close()
                continue

            bitfield = message[5:]
            pieces = parse_bitfield(
                bitfield
            )

            print(
                f"Pieces: {len(pieces)}"
            )

            # Send interested
            temp_peer.sock.send(
                interested()
            )

            print("Interested sent")

            # Wait for unchoke
            unchoked = False

            for _ in range(50):

                try:
                    msg = read_message(
                        temp_peer.sock
                    )
                except socket.timeout:
                    break
                except Exception:
                    break

                if msg is None:
                    break

                msg_id = msg.get("id", -1)
                msg_name = msg.get(
                    "name", ""
                )

                if msg_name == "keepalive":
                    continue

                if msg_id == 1:
                    unchoked = True
                    print("Unchoked!")
                    break

            if unchoked:
                return temp_peer, pieces, i + 1

            print("No unchoke received")
            temp_peer.sock.close()

        except Exception as e:
            print(f"Failed: {e}")
            try:
                temp_peer.sock.close()
            except Exception:
                pass
            continue

    return None, None, len(peers)
