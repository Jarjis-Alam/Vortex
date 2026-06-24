import struct
from message import request
from protocol import read_message


PIPELINE_SIZE = 32


def download_piece(
    peer,
    piece_index,
    piece_length,
    pipeline_size=32
):
    """
    Download a piece using pipelined requests.
    Sends pipeline_size requests at once, then
    reads responses and sends more as they arrive.
    """

    blocks = {}
    block_size = 16384

    # Build list of all block requests
    all_blocks = []
    offset = 0

    while offset < piece_length:

        length = min(
            block_size,
            piece_length - offset
        )

        all_blocks.append(
            (offset, length)
        )

        offset += block_size

    total_blocks = len(all_blocks)
    sent = 0
    received = 0

    # Send initial pipeline batch
    initial = min(
        pipeline_size,
        total_blocks
    )

    for i in range(initial):

        off, length = all_blocks[i]

        peer.sock.sendall(
            request(
                piece_index,
                off,
                length
            )
        )

        sent += 1

    # Receive responses and refill pipeline
    while received < total_blocks:

        msg = read_message(
            peer.sock
        )

        if msg is None:
            return None

        msg_id = msg.get("id", -1)

        # Handle non-piece messages
        if msg_id == 0:
            # Choked
            return None

        if msg_id != 7:
            # Keepalive or other message
            continue

        payload = msg["payload"]

        # payload format:
        # [0]    = id (7)
        # [1:5]  = piece index
        # [5:9]  = begin offset
        # [9:]   = block data
        block_begin = struct.unpack(
            "!I",
            payload[5:9]
        )[0]

        block_data = payload[9:]

        blocks[block_begin] = block_data
        received += 1

        # Send next request if available
        if sent < total_blocks:

            off, length = all_blocks[sent]

            peer.sock.sendall(
                request(
                    piece_index,
                    off,
                    length
                )
            )

            sent += 1

    # Assemble piece in offset order
    piece_data = b""

    for off, _ in all_blocks:

        if off not in blocks:
            return None

        piece_data += blocks[off]

    return piece_data
