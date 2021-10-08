from lyh_mysql.protocol import *
from struct import pack
from hashlib import sha1


class HandshakeV10:
    """
    url: https://dev.mysql.com/doc/internals/en/connection-phase-packets.html#packet-Protocol::Handshake
    """
    def __init__(self):
        # 1byte
        self.protocol_version = 0x0a
        # string[NUL]
        self.server_version = ''
        # 4 bytes
        self.connection_id = 0
        # string[8]
        self.auth_plugin_data_part = b''
        # 1 bytes
        self.filler = b'\00'
        # 2 bytes
        self.capability_flags = 0
        # 1 byte
        self.character_set = 0
        # 2 bytes
        self.status_flags = 0
        # 1 byte
        self.length_of_auth_plugin_data = 0
        # string[10]
        self.reserved = ''
        # string[$len]
        # self.auth_plugin_data_part_2 = ''
        # string[NUL]
        self.auth_plugin_name = ''
        self.is_capabilities = False

    def set_capabilities(self, b):
        self.is_capabilities = b

    def is_client_long_password(self):
        return is_capability_flag(self.capability_flags, CLIENT_LONG_PASSWORD)

    def is_client_found_rows(self):
        return is_capability_flag(self.capability_flags, CLIENT_FOUND_ROWS)

    def is_client_long_flag(self):
        return is_capability_flag(self.capability_flags, CLIENT_LONG_FLAG)

    def is_client_connect_with_db(self):
        return is_capability_flag(self.capability_flags, CLIENT_CONNECT_WITH_DB)

    def is_cLient_no_schema(self):
        return is_capability_flag(self.capability_flags, CLIENT_NO_SCHEMA)

    def is_client_compress(self):
        return is_capability_flag(self.capability_flags, CLIENT_COMPRESS)

    def is_client_odbc(self):
        return is_capability_flag(self.capability_flags, CLIENT_ODBC)

    def is_client_local_files(self):
        return is_capability_flag(self.capability_flags, CLIENT_LOCAL_FILES)

    def is_client_ignore_space(self):
        return is_capability_flag(self.capability_flags, CLIENT_IGNORE_SPACE)

    def is_client_protocol_41(self):
        return is_capability_flag(self.capability_flags, CLIENT_PROTOCOL_41)

    def is_client_interactive(self):
        return is_capability_flag(self.capability_flags, CLIENT_INTERACTIVE)

    def is_client_ssl(self):
        return is_capability_flag(self.capability_flags, CLIENT_SSL)

    def is_client_ignore_sigpipe(self):
        return is_capability_flag(self.capability_flags, CLIENT_IGNORE_SIGPIPE)

    def is_client_transactions(self):
        return is_capability_flag(self.capability_flags, CLIENT_TRANSACTIONS)

    def is_client_reserved(self):
        return is_capability_flag(self.capability_flags, CLIENT_RESERVED)

    def is_client_secure_connection(self):
        return is_capability_flag(self.capability_flags, CLIENT_SECURE_CONNECTION)

    def is_client_multi_statements(self):
        return is_capability_flag(self.capability_flags, CLIENT_MULTI_STATEMENTS)

    def is_client_multi_results(self):
        return is_capability_flag(self.capability_flags, CLIENT_MULTI_RESULTS)

    def is_client_ps_multi_results(self):
        return is_capability_flag(self.capability_flags, CLIENT_PS_MULTI_RESULTS)

    def is_client_plugin_auth(self):
        return is_capability_flag(self.capability_flags, CLIENT_PLUGIN_AUTH)

    def is_client_connect_attrs(self):
        return is_capability_flag(self.capability_flags, CLIENT_CONNECT_ATTRS)

    def is_client_plugin_auth_lenenc_client_data(self):
        return is_capability_flag(self.capability_flags, CLIENT_PLUGIN_AUTH_LENENC_CLIENT_DATA)

    def is_client_can_handle_expired_passwords(self):
        return is_capability_flag(self.capability_flags, CLIENT_CAN_HANDLE_EXPIRED_PASSWORDS)

    def is_client_session_track(self):
        return is_capability_flag(self.capability_flags, CLIENT_SESSION_TRACK)

    def is_client_deprecate_eof(self):
        return is_capability_flag(self.capability_flags, CLIENT_DEPRECATE_EOF)

    @staticmethod
    def parse(buf):
        idx = 0
        proto = HandshakeV10()
        proto.protocol_version = buf[idx]
        idx += 1
        while buf[idx] != 0:
            proto.server_version += chr(buf[idx])
            idx += 1
        # 00
        idx += 1

        proto.connection_id = buf[idx + 3] << 24 | buf[idx + 2] << 16 | buf[idx + 1] << 8 | buf[idx]
        idx += 4
        proto.auth_plugin_data_part = buf[idx:idx + 8]
        idx += 8
        proto.filler = buf[idx]
        idx += 1
        proto.capability_flags = buf[idx + 1] << 8 | buf[idx]
        idx += 2

        # not more data
        if len(buf) <= idx:
            return proto

        proto.set_capabilities(True)

        proto.character_set = buf[idx]
        idx += 1
        proto.status_flags = buf[idx + 1] << 8 | buf[idx]
        idx += 2

        proto.capability_flags = buf[idx + 1] << 24 | buf[idx] << 16 | proto.capability_flags
        idx += 2

        proto.length_of_auth_plugin_data = buf[idx]
        idx += 1
        proto.reserved = buf[idx:idx + 10]
        idx += 10

        if proto.is_client_secure_connection():
            ln = max(13, proto.length_of_auth_plugin_data - 8)
            proto.auth_plugin_data_part = proto.auth_plugin_data_part + buf[idx:idx + ln - 1]
            idx += ln

        if proto.is_client_plugin_auth():
            while buf[idx] != 0:
                proto.auth_plugin_name += chr(buf[idx])
                idx += 1
        # print('idx: ' + str(idx))

        return proto


class HandshakeV9:
    pass


class HandshakeResponse41:
    def __init__(self):
        self.capability_flags = 0x00000000
        self.max_packet_size = 0x40000000
        self.character_set = 33
        self.reserved = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.username = ''
        self.auth_response = b''
        self.database = ''
        self.auth_plugin_name = ''
        self.attrs = []

    def set_capability_flags(self):
        # from navicat
        self.capability_flags = 0x00EFA685
        return self

    def set_username(self, name):
        self.username = name
        return self

    def set_auth_response(self, auth):
        self.auth_response = auth
        return self

    def set_database(self, database):
        self.database = database
        return self

    def set_auth_plugin_name(self, plugin_name):
        self.auth_plugin_name = plugin_name
        return self

    def add_attr(self, key, value):
        self.attrs[key] = value
        return self

    def build(self):
        byt = bytearray()
        byt.extend(pack('<I', self.capability_flags))
        byt.extend((pack('<I', self.max_packet_size)))
        byt.append(self.character_set)
        byt.extend(self.reserved)
        byt.extend(bytes(self.username, 'utf8'))
        byt.append(0)

        if is_capability_flag(self.capability_flags, CLIENT_PLUGIN_AUTH_LENENC_CLIENT_DATA):
            ln = len(self.auth_response)
            if ln < 251:
                byt.append(ln)
            elif 251 <= ln < (2**16):
                byt.append(0xfc)
                byt.extend(pack('<H', ln))

            byt.extend(self.auth_response)
        elif is_capability_flag(self.capability_flags, CLIENT_SECURE_CONNECTION):
            byt.append(len(self.auth_response))
            byt.extend(self.auth_response)
        else:
            byt.extend(self.auth_response)
            byt.append(0)

        if is_capability_flag(self.capability_flags, CLIENT_CONNECT_WITH_DB):
            byt.extend(bytes(self.database, 'utf8'))
            byt.append(0)

        if is_capability_flag(self.capability_flags, CLIENT_PLUGIN_AUTH):
            byt.extend(bytes(self.auth_plugin_name, 'utf8'))
            byt.append(0)

        if is_capability_flag(self.capability_flags, CLIENT_CONNECT_ATTRS):
            pass

        return byt


def hash_password(password, rmd):
    var = sha1(password).digest()
    key = sha1(rmd + sha1(sha1(password).digest()).digest()).digest()
    return bytes(a ^ b for a, b in zip(var, key))

