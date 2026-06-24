class PieceAssembler:

    def __init__(self):

        self.blocks = {}

    def add_block(
        self,
        begin,
        block
    ):

        self.blocks[begin] = block

    def assemble(self):

        data = b""

        for offset in sorted(
            self.blocks.keys()
        ):

            data += self.blocks[offset]

        return data