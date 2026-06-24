def parse_bitfield(data):

    pieces = []

    for byte in data:

        for bit in range(8):

            if byte & (1 << (7 - bit)):
                pieces.append(True)
            else:
                pieces.append(False)

    return pieces