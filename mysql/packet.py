from struct import unpack


class Packet:
    def __init__(self):
        self.size = 0
        self.id = 0
        self.data = bytearray()

    def parse(self, buf):
        it = unpack('BBB', buf[0:3])
        i1 = it[0]
        i2 = it[1]
        i3 = it[2]
        self.size = i3 << 16 | i2 << 8 | i1
        self.id = buf[3:4]
