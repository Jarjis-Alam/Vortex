import struct

def interested():

    return struct.pack(
        "!IB",
        1,
        2
    )
def choke():

    return struct.pack(
        "!IB",
        1,
        0
    )


def unchoke():

    return struct.pack(
        "!IB",
        1,
        1
    )


def not_interested():

    return struct.pack(
        "!IB",
        1,
        3
    )

def parse(data):

    length = int.from_bytes(
        data[:4],
        byteorder="big"
    )

    msg_id = data[4]

    names = {
        0: "choke",
        1: "unchoke",
        2: "interested",
        3: "not interested",
        4: "have",
        5: "bitfield",
        6: "request",
        7: "piece"
    }

    result = {
        "length": length,
        "id": msg_id,
        "name": names.get(
            msg_id,
            "unknown"
        )
    }
    if msg_id == 4:
        result["piece_index"] = int.from_bytes(
            data[5:9],
            byteorder="big"
        )

    if msg_id == 6:
        result["piece_index"] = int.from_bytes(
            data[5:9],
            byteorder="big"
        )

        result["begin"] = int.from_bytes(
            data[9:13],
            byteorder="big"
        )

        result["request_length"] = int.from_bytes(
            data[13:17],
            byteorder="big"
        )
    if msg_id == 7:
        result["piece_index"] = int.from_bytes(
            data[5:9],
            byteorder="big"
        )

        result["begin"] = int.from_bytes(
            data[9:13],
            byteorder="big"
        )

        result["block"] = data[13:]

    return result
def request(
    piece_index,
    begin,
    length
):

    return struct.pack(
        "!IBIII",
        13,
        6,
        piece_index,
        begin,
        length
    )
def have(piece_index):

    return struct.pack(
        "!IBI",
        5,
        4,
        piece_index
    )
def piece(
    piece_index,
    begin,
    block
):

    length = 9 + len(block)

    return struct.pack(
        "!IBII",
        length,
        7,
        piece_index,
        begin
    ) + block