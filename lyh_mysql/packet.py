from struct import unpack, pack
from lyh_mysql.protocol import *


def packet_header(buf):
    assert (len(buf) == 4)
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

    def payload(self):
        buf = b''
        buf += pack('<I', self.size)[0:3]
        buf += pack('<B', self.sid)
        buf += self.data
        return buf

    def is_ok_packet(self):
        return self.size >= 3 and self.data[0] == 0x00

    def is_eof_packet(self):
        return self.size <= 5 and self.data[0] == 0xfe

    def is_error_packet(self):
        return self.size > 0 and self.data[0] == 0xff


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


class FieldColumn:
    def __init__(self, fields=0):
        self.fields = fields


class ResultSetRow:
    def __init__(self):
        self.rows = []

    def add_row(self, row):
        self.rows.append(row)

    def __str__(self):
        return f'{self.rows}'


class ColumnDefinition41:
    def __init__(self):
        self.catalog = ''
        self.schema = ''
        self.table = ''
        self.org_table = ''
        self.name = ''
        self.org_name = ''
        self.fields_length = 0
        self.character_set = 0
        self.column_length = 0
        self.type = 0
        self.flags = 0
        self.decimals = 0
        self.filler = 0

    def __str__(self):
        return f'--column definition--\n' + \
               f'catalog: {self.catalog}\n' + \
               f'schema: {self.schema}\n' + \
               f'table: {self.table}\n' + \
               f'org_table: {self.org_table}\n' + \
               f'name: {self.name}\n' + \
               f'org_name: {self.org_name}\n' + \
               f'fields_length: {self.fields_length}\n' + \
               f'character_set: {self.character_set}\n' + \
               f'column_length: {self.column_length}\n' + \
               f'type: {self.type}\n' + \
               f'flags: {self.flags}\n' + \
               f'decimals: {self.decimals}\n' + \
               f'filler: {self.filler}\n'


def parse_error(buf):
    packet = ErrorPacket()
    packet.header = buf[0]
    packet.error_code = buf[2] << 8 | buf[1]
    last = 3
    if is_capability_flag(CLIENT_CAPABILITIES, CLIENT_PROTOCOL_41):
        packet.sql_state_marker = buf[3]
        packet.sql_state = buf[4:9]
        last = 9
    packet.error_message = buf[last:]
    return packet


def parse_ok(buf):
    packet = OkPacket()
    idx = 0
    packet.header = buf[idx]
    idx += 1
    ln, cn = int_length_encoded(buf[idx:])
    packet.affected_rows = ln
    idx += cn
    ln, cn = int_length_encoded(buf[1 + cn:])
    packet.last_insert_id = ln
    idx += cn

    if is_capability_flag(CLIENT_CAPABILITIES, CLIENT_PROTOCOL_41):
        packet.status_flags = buf[idx + 1] << 8 | buf[idx]
        idx += 2
        packet.warnings = buf[idx + 1] << 8 | buf[idx]
        idx += 2
    elif is_capability_flag(CLIENT_CAPABILITIES, CLIENT_TRANSACTIONS):
        packet.status_flags = buf[idx + 1] << 8 | buf[idx]
        idx += 2

    if idx >= len(buf):
        return packet

    if is_capability_flag(CLIENT_CAPABILITIES, CLIENT_SESSION_TRACK):
        packet.info, cn = string_length_encoded(buf[idx:])
        idx += cn
        if is_capability_flag(packet.status_flags, SERVER_SESSION_STATE_CHANGED):
            packet.session_state_changes, cn = string_length_encoded(buf[idx:])
            idx += cn
    else:
        packet.info = buf[idx:]
    return packet


def parse_eof(buf):
    packet = EofPacket()
    packet.header = buf[0]
    if is_capability_flag(CLIENT_CAPABILITIES, CLIENT_PROTOCOL_41):
        packet.status_flags = buf[2] << 8 | buf[1]
        packet.warnings = buf[4] << 8 | buf[3]
    return packet


class ResponsePacketParser:
    @staticmethod
    def parse(buf):
        header = buf[0]
        # error packet
        if header == 0xff:
            return parse_error(buf)
        # ok packet
        elif header == 0x00:
            return parse_ok(buf)
        # EOF packet
        elif header == 0xfe:
            return parse_eof(buf)


class QueryResponseParser:
    @staticmethod
    def parse(buf):
        header = buf[0]
        # error packet
        if header == 0xff:
            return parse_error(buf)
        # ok packet
        elif header == 0x00:
            return parse_ok(buf)
        # EOF packet
        elif header == 0xfe:
            return parse_eof(buf)
        # Protocol::LOCAL_INFILE_Request
        elif header == 0xfb:
            pass
        else:
            size, _ = int_length_encoded(buf)
            return FieldColumn(size)

    @staticmethod
    def parse_column(buf):
        col = ColumnDefinition41()
        idx = 0
        col.catalog, idx = string_length_encoded(buf)
        col.schema, cn = string_length_encoded(buf, idx)
        idx += cn
        col.table, cn = string_length_encoded(buf, idx)
        idx += cn
        col.org_table, cn = string_length_encoded(buf, idx)
        idx += cn
        col.name, cn = string_length_encoded(buf, idx)
        idx += cn
        col.org_name, cn = string_length_encoded(buf, idx)
        idx += cn
        col.fields_length, cn = int_length_encoded(buf, idx)
        idx += cn
        col.character_set = int_fixed_length(buf, 2, idx)
        idx += 2
        col.column_length = int_fixed_length(buf, 4, idx)
        idx += 4
        col.type = buf[idx]
        idx += 1
        col.flags = int_fixed_length(buf, 2, idx)
        idx += 2
        col.decimals = buf[idx]
        idx += 1
        col.filler = int_fixed_length(buf, 2, idx)
        idx += 2
        return col

    @staticmethod
    def parse_row(buf):
        header = buf[0]
        # error packet
        if header == 0xfe:
            return parse_eof(buf)
        # ok packet
        elif header == 0x00:
            return parse_ok(buf)
        else:
            row = ResultSetRow()
            idx = 0
            while idx < len(buf):
                if buf[idx] == 0xfb:
                    row.add_row(None)
                    idx += 1
                else:
                    txt, cn = string_length_encoded(buf, idx)
                    idx += cn
                    row.add_row(str(txt, 'utf8'))
                    # row.add_row(txt)
            return row




