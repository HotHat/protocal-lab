import unittest

import socket
from lyh_mysql.packet import *
from lyh_mysql.handshake import HandshakeV10, HandshakeResponse41, hash_password
from lyh_mysql.sync_socket import SyncSocket


class TestMySql(unittest.TestCase):
    def test_abc(self):
        conn = SyncSocket()
        conn.connect('127.0.0.1', 3306)
        packet = conn.read_packet()

        res = HandshakeV10.parse(packet.data)
        print(res)
        print(res.auth_plugin_data_part)
        print(res.auth_plugin_data_part.hex())
        auth = hash_password(b'secret', res.auth_plugin_data_part)
        resp = HandshakeResponse41()
        byt = resp.set_username('homestead') \
            .set_auth_plugin_name('mysql_native_password') \
            .set_auth_response(auth) \
            .payload()
        print(byt)
        p = Packet()
        p.set_id(packet.sid + 1)
        p.add_data(byt)
        conn.send(p)
        # login back
        resp_packet = conn.read_packet()
        print(resp_packet.size)
        print(resp_packet.sid)
        print(resp_packet.data)
        pk = ResponsePacketParser().parse(resp_packet.data)
        print(pk)

        # TODO: send query
        conn.send(Packet().add_data(ComInitDB('god_bless_you').payload()))
        pk = conn.read_packet()
        resp = ResponsePacketParser().parse(pk.data)
        print('sql: use god_bless_you')
        print(resp)
        conn.send(Packet().add_data(ComQuery('select id,name from book limit 10').payload()))
        pk = conn.read_packet()
        print(pk.data)
        field = QueryResponseParser.parse(pk.data)
        print('sql: select id,name from book limit 10')
        print(field)
        for i in range(field.fields):
            pk = conn.read_packet()
            print(pk.data)
            col = QueryResponseParser.parse_column(pk.data)
            print(col)

        # EOF
        pk = conn.read_packet()
        print('----EOF----')
        print(pk.data)
        resp = ResponsePacketParser().parse(pk.data)
        print(resp)

        # data begin
        while True:
            pk = conn.read_packet()
            if pk.is_eof_packet() or pk.is_error_packet():
                print('-----eof/error')
                print(pk.data)
                break
            print(pk.payload())
            resp = QueryResponseParser().parse_row(pk.data)
            print(resp)

        conn.close()

    def test_init(self):
        bt = b'\n5.7.27-0ubuntu0.18.04.1-log\x00\x02\x00\x00\x00wS\x01N\x0c4[\x7f\x00\xff\xf7\x08\x02\x00\xff\x81\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00z#Z\x13\x1fPaG\x18\x0enA\x00mysql_native_password\x00'
        p = HandshakeV10.parse(bt)

        print(p.protocol_version)
        print(p.server_version)
        print(p.connection_id)
        print(p.auth_plugin_data_part_1)
        print(p.filler)
        # print(p.capability_flags)
        print(p.character_set)
        print(p.status_flags)
        print(p.capability_flags)
        print(p.length_of_auth_plugin_data)
        print(p.reserved)
        print(p.auth_plugin_data_part_2)
        print(p.auth_plugin_name)
        print(p.is_client_plugin_auth())
        print(p.is_client_protocol_41())
        print(p.is_client_ssl())
        print(p.is_client_plugin_auth_lenenc_client_data())
        print(p.is_client_secure_connection())
        print(p.is_client_connect_with_db())
        print(p.is_client_plugin_auth())
        print(p.is_client_connect_attrs())

    def test_response(self):
        resp = HandshakeResponse41()
        byt = resp.set_capability_flags()\
            .set_username('homestead')\
            .set_auth_plugin_name('mysql_native_password')\
            .set_auth_response('password')\
            .payload()
        print(byt)
        pk = Packet()
        # pk.add_data(b'12345678901234567890')
        pk.add_data(byt)
        pk.set_id(1)
        print(pk.payload())

    def test_password(self):
        from lyh_mysql.handshake import hash_password
        p = b'\30\37\47\44\01\6c\17\43\01\2b\10\6e\77\14\6c\37\7b\60\11\33'
        h = hash_password(b'secret', p)
        print(h.hex())

    def test_multi_o(self):
        sync = SyncSocket()
        b = b'123456789012345678901234567890'
        pk = Packet()
        pk.set_id(0)
        pk.add_data(b)

        sync.send(pk)

    def test_ok(self):
        byt = b'\x00\x00\x00\x02\x00\x00\x00'
        parser = ResponsePacketParser(set_capability_flag(0, CLIENT_PROTOCOL_41))
        pk = parser.parse(byt)
        print(pk)

    def test_error(self):
        byt = b"\xff\x15\x04#28000Access denied for user 'homestead'@'_gateway' (using password: YES)"
        parser = ResponsePacketParser(set_capability_flag(0, CLIENT_PROTOCOL_41))
        pk = parser.parse(byt)
        print(pk)

    def test_fixed_int(self):
        byt = b'\01\02\03'
        print(int_fixed_length(byt, 1, 1))
        print(int_fixed_length(byt, 2, 1))
        print(int_fixed_length(byt, 3))

    def test_col_def(self):
        byt = b'\x03def\rgod_bless_you\x04book\x04book\x02id\x02id\x0c?\x00\x0b\x00\x00\x00\x03\x03B\x00\x00\x00'
        col = QueryResponseParser.parse_column(byt)
        print(col)

    def test_col_row(self):
        byt = b'\x03154\t\xe5\xa2\x93\xe7\x9b\x9c\xe6\x9b\xb8'
        col = QueryResponseParser.parse_row(byt)
        print(col)


