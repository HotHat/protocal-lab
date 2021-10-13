import unittest
import socket
from dns.dns_packet import *


class TestDns(unittest.TestCase):
    def test_udp(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        # little endian
        # data = b'\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x05baidu\x03com\x00\x01\x00\x01\x00'
        # big endian
        data = b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x05baidu\x03com\x00\x00\x01\x00\x01'

        sock.sendto(data, ('114.114.114.114', 53))
        resp, address = sock.recvfrom(1024)
        print(resp)
        print(address)

    def test_packet(self):
        packet = DnsPacket()
        packet.add_query('baidu.com')

        print(packet.payload())


