import socket
from http_parser import HttpParse, HttpParseStatus

HOST = '0.0.0.0'
PORT = 8888

if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))

    server_socket.listen(512)

    parser = HttpParse()

    while True:
        parser.reset()

        conn, address = server_socket.accept()
        data = conn.recv(1024)
        print(data)
        parser.add_buffer(data)
        st = parser.parse_http_request()
        if st == HttpParseStatus.OK:
            print(parser.http_request.major)
            print(parser.http_request.minor)
            print(parser.http_request.target)
            print(parser.http_request.headers)
            conn.send(b'HTTP/1.1 200 OK\r\nContent-Length: 11\r\n\r\nhello world\r\n')
            conn.close()

    # server_socket.close()


