import socket


def read_exact(sock, size):

    data = b""

    while len(data) < size:

        try:
            chunk = sock.recv(
                size - len(data)
            )
        except socket.timeout:
            raise socket.timeout(
                f"Timeout reading {size - len(data)} bytes"
            )

        if not chunk:
            return None

        data += chunk

    return data


def read_message(sock):

    length_data = read_exact(
        sock,
        4
    )

    if not length_data:
        return None

    length = int.from_bytes(
        length_data,
        "big"
    )

    if length == 0:

        return {
            "name": "keepalive"
        }

    payload = read_exact(
        sock,
        length
    )

    return {
        "length": length,
        "id": payload[0],
        "payload": payload
    }