class BencodeDecoder:

    def __init__(self, data):
        self.data = data
        self.index = 0

    def decode(self):

        char = self.data[self.index:self.index + 1]

        if char == b'i':
            return self.decode_int()

        elif char == b'l':
            return self.decode_list()

        elif char == b'd':
            return self.decode_dict()

        elif char.isdigit():
            return self.decode_string()

    def decode_int(self):

        self.index += 1

        end = self.data.index(b'e', self.index)

        number = int(
            self.data[self.index:end]
        )

        self.index = end + 1

        return number

    def decode_string(self):

            colon = self.data.index(b':', self.index)

            length = int(
                self.data[self.index:colon]
            )

            self.index = colon + 1

            value = self.data[
                self.index:self.index + length
            ]

            self.index += length

            return value
    def decode_list(self):

        self.index += 1

        result = []

        while self.data[self.index:self.index + 1] != b'e':
            result.append(
                self.decode()
            )

        self.index += 1

        return result
    def decode_dict(self):

        self.index += 1

        result = {}

        while self.data[self.index:self.index + 1] != b'e':

            key = self.decode()

            value = self.decode()

            result[key] = value

        self.index += 1

        return result
    def decode_dict(self):

        self.index += 1

        result = {}

        while self.data[self.index:self.index + 1] != b'e':

            key = self.decode()

            value = self.decode()

            result[key] = value

        self.index += 1

        return result