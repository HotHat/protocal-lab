from struct import pack


class DnsPacket:
    def __init__(self):
        self.id = 0
        self.option = 0x0000
        self.query = ''

    def add_query(self, domain):
        self.query = domain

    # def set_query(self):
    #     self.option &=

    def payload(self):
        data = b''
        data += pack('>H', self.id)
        data += pack('>H', self.option)
        data += pack('>H', 1)
        data += pack('>H', 0)
        data += pack('>H', 0)
        data += pack('>H', 0)
        im = self.query.split('.')
        for i in im:
            data += pack('>B', len(i)) + i.encode()

        data += b'\00'
        # QTYPE
        data += pack('>H', 1)
        # QCLASS
        data += pack('>H', 1)

        return data
