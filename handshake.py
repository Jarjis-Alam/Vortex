class Handshake:

    def __init__(
        self,
        info_hash,
        peer_id
    ):

        self.info_hash = info_hash
        self.peer_id = peer_id

    def build(self):

        protocol = (
            b"BitTorrent protocol"
        )

        packet = (
            bytes([len(protocol)])
            + protocol
            + b"\x00" * 8
            + self.info_hash
            + self.peer_id
        )

        return packet
    @staticmethod
    def parse(data):

        pstrlen = data[0]

        protocol = data[1:20]

        reserved = data[20:28]

        info_hash = data[28:48]

        peer_id = data[48:68]

        return {
            "pstrlen": pstrlen,
            "protocol": protocol,
            "reserved": reserved,
            "info_hash": info_hash,
            "peer_id": peer_id
        }