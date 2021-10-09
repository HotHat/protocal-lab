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
        auth = hash_password(b'secre1', res.auth_plugin_data_part)
        resp = HandshakeResponse41()
        byt = resp.set_capability_flags() \
            .set_username('homestead') \
            .set_auth_plugin_name('mysql_native_password') \
            .set_auth_response(auth) \
            .build()
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
        parser = ResponsePacketParser(resp.capability_flags)
        pk = parser.parse(resp_packet.data)
        print(pk)

        # TODO: send query


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
            .build()
        print(byt)
        pk = Packet()
        # pk.add_data(b'12345678901234567890')
        pk.add_data(byt)
        pk.set_id(1)
        print(pk.build())

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



