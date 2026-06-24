def encode(data):

    if isinstance(data, int):
        return b'i' + str(data).encode() + b'e'

    elif isinstance(data, bytes):
        return str(len(data)).encode() + b':' + data

    elif isinstance(data, list):

        result = b'l'

        for item in data:
            result += encode(item)

        result += b'e'

        return result

    elif isinstance(data, dict):

        result = b'd'

        for key in sorted(data.keys()):
            result += encode(key)
            result += encode(data[key])

        result += b'e'

        return result