import socket
import struct
import random


class UDPTrackerClient:

    def __init__(
        self,
        host,
        port
    ):

        self.host = host
        self.port = port

    def connect(self):

        self.sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

        self.sock.settimeout(15)

        protocol_id = 0x41727101980

        action = 0

        transaction_id = random.randint(
            0,
            2147483647
        )

        packet = struct.pack(
            "!QII",
            protocol_id,
            action,
            transaction_id
        )

        print(
            "Sending connect request..."
        )
        print("Packet Length:", len(packet))
        print(packet.hex())
        self.sock.sendto(
            packet,
            (self.host, self.port)
        )

        response, addr = self.sock.recvfrom(
            2048
        )

        print(
            "Received",
            len(response),
            "bytes"
        )

        return response
    def parse_connect_response(
        self,
        response
    ):

        action = int.from_bytes(
            response[0:4],
            "big"
        )

        transaction_id = int.from_bytes(
            response[4:8],
            "big"
        )

        connection_id = int.from_bytes(
            response[8:16],
            "big"
        )

        return {
            "action": action,
            "transaction_id": transaction_id,
            "connection_id": connection_id
        }
    def build_announce_request(
        self,
        connection_id,
        info_hash,
        peer_id,
        left
    ):

        action = 1

        transaction_id = random.randint(
            0,
            2147483647
        )

        downloaded = 0
        uploaded = 0

        event = 0
        ip = 0
        key = random.randint(
            0,
            2147483647
        )

        num_want = -1
        port = 6881

        packet = struct.pack(
            "!QII20s20sQQQIIIiH",
            connection_id,
            action,
            transaction_id,
            info_hash,
            peer_id,
            downloaded,
            left,
            uploaded,
            event,
            ip,
            key,
            num_want,
            port
        )

        return packet
    def announce(
        self,
        packet
    ):

        print(
            "Sending announce request..."
        )

        print(
            "Announce Length:",
            len(packet)
        )

        self.sock.sendto(
            packet,
            (self.host, self.port)
        )

        response, addr = (
            self.sock.recvfrom(
                4096
            )
        )

        print(
            "Announce response:",
            len(response),
            "bytes"
        )

        return response
    def parse_announce_response(
        self,
        response
    ):

        action = int.from_bytes(
            response[0:4],
            "big"
        )

        transaction_id = int.from_bytes(
            response[4:8],
            "big"
        )

        interval = int.from_bytes(
            response[8:12],
            "big"
        )

        leechers = int.from_bytes(
            response[12:16],
            "big"
        )

        seeders = int.from_bytes(
            response[16:20],
            "big"
        )

        peers = []

        peer_data = response[20:]

        for i in range(
            0,
            len(peer_data),
            6
        ):

            ip = ".".join(
                str(b)
                for b in peer_data[
                    i:i+4
                ]
            )

            port = int.from_bytes(
                peer_data[
                    i+4:i+6
                ],
                "big"
            )

            peers.append(
                (ip, port)
            )

        return {
            "action": action,
            "interval": interval,
            "leechers": leechers,
            "seeders": seeders,
            "peers": peers
        }