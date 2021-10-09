from struct import unpack, pack
from lyh_mysql.protocol import *

def packet_header(buf):
    assert(len(buf) == 4)
    it = unpack('BBB', buf[0:3])
    i1 = it[0]
    i2 = it[1]
    i3 = it[2]
    size = i3 << 16 | i2 << 8 | i1
    cid = buf[3]
    return size, cid


# class PacketSet:
#     def __init__(self):
#         self.packet = []
#         self.size = 0
#         self.id = 0
#         self.is_ready = False
#
#     def add_packet(self, packet):
#         self.packet.append(packet)
#         self.size += packet.size
#         if self.id == 0:
#             self.id = packet.sid
#
#         if packet.size < 0xff:
#             self.is_ready = True
#
#     def fetch_data(self):
#         data = b''
#         for packet in self.packet:
#             data += packet.data
#         return data


class Packet:
    def __init__(self, size=0, sid=0, data=b''):
        self.size = size
        self.sid = sid
        self.is_ready = False
        self.data = data

    def add_data(self, data):
        self.data = data
        self.size = len(self.data)
        return self

    def set_id(self, cid):
        self.sid = cid
        return self

    def build(self):
        buf = b''
        buf += pack('<I', self.size)[0:3]
        buf += pack('<B', self.sid)
        buf += self.data
        return buf

    def parse_header(self, buf):
        it = unpack('BBB', buf[0:3])
        i1 = it[0]
        i2 = it[1]
        i3 = it[2]
        self.size = i3 << 16 | i2 << 8 | i1
        self.sid = buf[3]


class OkPacket:
    def __init__(self):
        self.header = 0
        self.affected_rows = 0
        self.last_insert_id = 0
        self.status_flags = 0
        self.warnings = 0
        self.info = ''
        self.session_state_changes = ''


class ErrorPacket:
    def __init__(self):
        self.header = 0xff
        self.error_code = 0
        self.sql_state_marker = ''
        self.sql_state = ''
        self.error_message = ''


class EofPacket:
    def __init__(self):
        self.header = 0xff
        self.warnings = 0
        self.status_flags = 0


class ResponsePacketParser:
    def __init__(self, capabilities):
        self.capabilities = capabilities

    def parse_error(self, buf):
        packet = ErrorPacket()
        packet.header = buf[0]
        packet.error_code = buf[2] << 8 | buf[1]
        last = 3
        if is_capability_flag(self.capabilities, CLIENT_PROTOCOL_41):
            packet.sql_state_marker = buf[3]
            packet.sql_state = buf[4:9]
            last = 9
        packet.error_message = buf[last:]
        return packet

    def parse_ok(self, buf):
        packet = OkPacket()
        idx = 0
        packet.header = buf[idx]
        idx += 1
        ln, cn = int_length_encoded(buf[idx:])
        packet.affected_rows = ln
        idx += cn
        ln, cn = int_length_encoded(buf[1+cn:])
        packet.last_insert_id = ln
        idx += cn

        if is_capability_flag(self.capabilities, CLIENT_PROTOCOL_41):
            packet.status_flags = buf[idx+1] << 8 | buf[idx]
            idx += 2
            packet.warnings = buf[idx+1] << 8 | buf[idx]
            idx += 2
        elif is_capability_flag(self.capabilities,  CLIENT_TRANSACTIONS):
            packet.status_flags = buf[idx+1] << 8 | buf[idx]
            idx += 2

        if idx >= len(buf):
            return packet

        if is_capability_flag(self.capabilities, CLIENT_SESSION_TRACK):
            print(self.capabilities)
            packet.info, cn = string_length_encoded(buf[idx:])
            idx += cn
            if is_capability_flag(packet.status_flags, SERVER_SESSION_STATE_CHANGED):
                packet.session_state_changes, cn = string_length_encoded(buf[idx:])
                idx += cn
        else:
            packet.info = buf[idx:]
        return packet

    def parse_eof(self, buf):
        packet = EofPacket()
        packet.header = buf[0]
        if is_capability_flag(self.capabilities, CLIENT_PROTOCOL_41):
            packet.status_flags = buf[2] << 8 | buf[1]
            packet.warnings = buf[4] << 8 | buf[3]
        return packet

    def parse(self, buf):
        header = buf[0]
        # error packet
        if header == 0xff:
            return self.parse_error(buf)
        # ok packet
        elif header == 0x00:
            return self.parse_ok(buf)
        # EOF packet
        elif header == 0xfe:
            return self.parse_ok(buf)

