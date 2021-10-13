from struct import pack, unpack
from dns.scaner import Scanner
import enum


class DnsType(enum.Enum):
    A = 1
    NS = 2
    MD = 3
    MF = 4
    CNAME = 5
    SOA = 6
    MB = 7
    MG = 8
    MR = 9
    NULL = 10
    WKS = 11
    PTR = 12
    HINFO = 13
    MINFO = 14
    MX = 15
    TXT = 16


class DnsQType(DnsType, enum.Enum):
    AXFR = 252
    MALLB = 253
    MAILA = 254
    # *
    STAR = 255


class DnsClassValue(enum.Enum):
    IN = 1
    CS = 2
    CH = 3
    HS = 4


class DnsQClassValue(DnsClassValue, enum.Enum):
    STAR = 255


class DnsPacket:
    """
    rfc: https://datatracker.ietf.org/doc/html/rfc1035
    """
    def __init__(self):
        self.id = 0
        self.option = 0x0000
        self.query = []
        self.question = []
        self.answer = []
        self.query_count = 0
        self.answer_count = 0
        self.authority_count = 0
        self.addition_count = 0

    def add_query(self, domain, q_type, q_class):
        self.query.append((domain, q_type, q_class))
        if len(self.query) > 1:
            raise Exception('not support query more than one')

    def set_query(self):
        self.option >>= 1

    def set_response(self):
        self.option |= 1 << 15

    def set_standard_query(self):
        self.option &= ~(0x0f << 11)

    def set_invert_query(self):
        self.option &= ~(0x0f << 11)
        self.option |= 1 << 11

    def set_status_query(self):
        self.option &= ~(0x0f << 11)
        self.option |= 1 << 12

    def set_aa(self):
        self.option |= 1 << 10

    def is_aa(self):
        return self.option >> 10 & 0x01

    def set_tc(self):
        self.option |= 1 << 9

    def is_tc(self):
        return self.option >> 9 & 0x01

    def set_rd(self):
        self.option |= 1 << 8

    def is_rd(self):
        return self.option >> 8 & 0x01

    def set_ra(self):
        self.option |= 1 << 7

    def is_ra(self):
        return self.option >> 7 & 0x01

    def get_rcode(self):
        return self.option & 0x0f

    @staticmethod
    def parse_name(buf, start):
        assert (len(buf) - start >= 1)
        name = []
        idx = start
        ln = buf[idx]
        while ln != 0:
            assert(len(buf) - idx >= ln)
            name.append(buf[idx+1:buf[idx]])
            idx += ln + 1
            ln = buf[idx]
        return '.'.join(name), idx

    def parse(self, buf):
        scanner = Scanner(buf)
        self.id = scanner.next_int(2, False)
        self.option = scanner.next_int(2)
        self.query_count = scanner.next_int(2)
        self.answer_count = scanner.next_int(2)
        self.authority_count = scanner.next_int(2)
        self.addition_count = scanner.next_int(2)

        # TODO: fetch query, answer, authority, addition
        for i in range(self.query_count):
            name = scanner.next_name()
            rr_type = scanner.next_int(2)
            rr_class = scanner.next_int(2)
            self.question.append((name, rr_type, rr_class))

        for i in range(self.answer_count + self.authority_count + self.addition_count):
            name = scanner.next_name()
            rr_type = scanner.next_int(2)
            rr_class = scanner.next_int(2)
            rr_ttl = scanner.next_int(4)
            rr_len = scanner.next_int(2)
            rr_data = scanner.next_bytes(rr_len)
            self.answer.append((name, rr_type, rr_class, rr_ttl, rr_data))

    def payload(self):
        data = b''
        data += pack('>H', self.id)
        data += pack('>H', self.option)
        data += pack('>H', len(self.query))
        data += pack('>H', 0)
        data += pack('>H', 0)
        data += pack('>H', 0)
        for i in self.query:
            im = i[0].split('.')
            for j in im:
                data += pack('>B', len(j)) + j.encode()
            data += b'\00'
            # QTYPE
            data += pack('>H', i[1].value)
            # QCLASS
            data += pack('>H', i[2].value)

        return data
