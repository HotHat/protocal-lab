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
        #esp = b'\x00\x00\x80\x80\x00\x01\x00\x02\x00\x00\x00\x00\x05baidu\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x01c\x00\x04\xdc\xb5&\x94\xc0\x0c\x00\x01\x00\x01\x00\x00\x01c\x00\x04\xdc\xb5&\xfb'

        sock.sendto(data, ('114.114.114.114', 53))
        resp, address = sock.recvfrom(1024)
        print(resp)
        print(address)

    def test_packet(self):
        packet = DnsPacket()
        packet.add_query('google.com', DnsQType.A, DnsQClassValue.IN)

        print(packet.payload())

    def test_ip(self):
        ip = socket.inet_ntoa(b'\xdc\xb5&\xfb')
        print(ip)

    def test_bin(self):
        packet = DnsPacket()
        packet.set_query()
        print(bin(packet.option))
        print(packet.option)
        packet.set_response()
        print(bin(packet.option))
        print(packet.option)
        packet.set_opcode_standard_query()
        print(bin(packet.option))
        packet.set_opcode_invert_query()
        print(bin(packet.option))
        packet.set_opcode_status()
        print(bin(packet.option))
        # ra
        packet.set_ra()
        print(bin(packet.option))
        # rd
        packet.set_rd()
        print(bin(packet.option))
        # tc
        packet.set_tc()
        print(bin(packet.option))
        # aa
        packet.set_aa()
        print(bin(packet.option))

    def test_parse(self):
        resp = b'\x00\x00\x80\x80\x00\x01\x00\x02\x00\x00\x00\x00\x05baidu\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x01c\x00\x04\xdc\xb5&\x94\xc0\x0c\x00\x01\x00\x01\x00\x00\x01c\x00\x04\xdc\xb5&\xfb'
        packet = DnsPacket()
        packet.parse(resp)
        print(packet.id)
        print(packet.option)
        print(packet.get_rcode())
        print(packet.is_ra())
        # count
        print(packet.query_count)
        print(packet.answer_count)
        print(packet.authority_count)
        print(packet.addition_count)
        print(packet.question)
        # print(socket.inet_ntoa(packet.query[0][4]))
        print(packet.answer)
        print(socket.inet_ntoa(packet.answer[0][4]))





