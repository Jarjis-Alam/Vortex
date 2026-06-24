from handshake import Handshake
import socket

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server.bind(("127.0.0.1", 5000))

server.listen(1)

print("Waiting for peer...")

client, address = server.accept()

print("Peer connected:", address)

handshake = client.recv(68)

print("Handshake length:",
      len(handshake))

parsed = Handshake.parse(
    handshake
)

print(
    parsed["protocol"]
)

print(
    parsed["peer_id"]
)

client.close()
server.close()