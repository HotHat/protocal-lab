import unittest

import socket
from mysql.packet import *


class TestMySql(unittest.TestCase):
    def test_abc(self):
        packet = Packet()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 3306))
        b = s.recv(4)
        packet.parse(b)
        print(packet.size)
        print(packet.id)
        b = s.recv(packet.size)
        print(b)
