from bencode import BencodeDecoder
from encoder import encode

import hashlib


class Torrent:

    def __init__(self, filename):

        with open(filename, "rb") as f:
            data = f.read()

        self.data = data

        self.meta = BencodeDecoder(
            data
        ).decode()

        self.info = self.meta[b'info']

    def get_name(self):

        return self.info[b'name']

    def get_piece_length(self):

        return self.info[b'piece length']

    def get_number_of_pieces(self):

        return len(
            self.info[b'pieces']
        ) // 20

    def get_info_hash(self):

        bencoded_info = encode(
            self.info
        )

        return hashlib.sha1(
            bencoded_info
        ).hexdigest()
    def get_size(self):

        if b'length' in self.info:
            return self.info[b'length']
        elif b'files' in self.info:
            return sum(f[b'length'] for f in self.info[b'files'])
        return 0
    def get_piece_hash(self, index):

        pieces = self.info[b'pieces']

        start = index * 20

        end = start + 20

        return pieces[start:end]

    def get_piece_count(self):

        return len(
            self.info[b'pieces']
        ) // 20

    def get_total_size(self):

        return self.get_size()

    def get_piece_size(self, piece_index):

        piece_length = self.get_piece_length()
        total_size = self.get_size()
        piece_count = self.get_piece_count()

        if piece_index == piece_count - 1:
            return total_size - (piece_index * piece_length)

        return piece_length

    def get_info_hash_bytes(self):

        bencoded_info = encode(
            self.info
        )

        return hashlib.sha1(
            bencoded_info
        ).digest()