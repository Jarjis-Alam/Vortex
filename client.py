import socket

from torrent import Torrent
from peer import generate_peer_id
from handshake import Handshake

torrent = Torrent(
    "zorin.torrent"
)

peer_id = generate_peer_id()

packet = Handshake(
    torrent.get_info_hash_bytes(),
    peer_id
).build()

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client.connect(
    ("127.0.0.1", 5000)
)

client.send(packet)

print(
    "Handshake sent:",
    len(packet)
)

client.close()