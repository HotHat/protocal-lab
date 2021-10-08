from struct import unpack, pack


class Packet:
    def __init__(self):
        self.size = 0
        self.id = 0
        self.data = bytearray()

    def add_data(self, data):
        self.data = data
        self.size = len(self.data)
        return self

    def set_id(self, cid):
        self.id = cid
        return self

    def build(self):
        buf = bytearray()
        buf.extend(pack('<I', self.size)[0:3])
        buf.append(self.id)
        buf.extend(self.data)
        return buf

    def parse(self, buf):
        it = unpack('BBB', buf[0:3])
        i1 = it[0]
        i2 = it[1]
        i3 = it[2]
        self.size = i3 << 16 | i2 << 8 | i1
        self.id = buf[3]
