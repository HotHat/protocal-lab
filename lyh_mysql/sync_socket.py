import socket
from lyh_mysql.packet import *


class SyncSocket:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.packet = Packet()

    def connect(self, ip_address, port):
        self.socket.connect((ip_address, port))

    def read_packet(self):
        packet = Packet()
        while not packet.is_ready:
            header = self.recv(4)
            size, sid = packet_header(header)
            packet.size += size
            # if packet.id == 0:
            packet.sid = sid
            data = self.recv(size)
            packet.add_data(data)

            if size < 0xff:
                break

        return packet

    def recv(self, size):
        data = b''
        ln = 0
        while ln < size:
            data += self.socket.recv(size - ln)
            ln += len(data)
        return data

    def send(self, packet):
        mod = 0xffffff
        m = int(packet.size / mod)
        i = 0
        sid = packet.sid
        while i < m:
            tmp = Packet()
            tmp.sid = sid
            tmp.size = mod
            low = i * mod
            high = (i + 1) * mod
            tmp.data = packet.data[low:high]
            # print(tmp.id)
            # print(tmp.size)
            # print(tmp.data)
            self.socket.send(tmp.payload())
            i += 1
            sid += 1

        al = m * mod
        if al == packet.size:
            # print('0: ', b'\00\00\00' + pack('<B', cid))
            self.socket.send(Packet(0, 0).payload())
        else:
            # print('1: ', p + pack('<B', cid) + packet.data[al:packet.size])
            self.socket.send(Packet(packet.size - al, sid, packet.data[al:packet.size]).payload())

    def close(self):
        self.socket.close()

    def read_query(self):
        pass

