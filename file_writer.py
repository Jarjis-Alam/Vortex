class FileWriter:

    def __init__(self, filename):

        self.filename = filename

    def write_piece(
        self,
        offset,
        data
    ):

        with open(
            self.filename,
            "r+b"
        ) as f:

            f.seek(offset)

            f.write(data)