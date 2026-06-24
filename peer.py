import random

def generate_peer_id():

    return (
        b"-PY0001-" +
        ''.join(
            random.choice("0123456789")
            for _ in range(12)
        ).encode()
    )