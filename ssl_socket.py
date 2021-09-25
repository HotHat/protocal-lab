
import socket, ssl

context = ssl.SSLContext()
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = True
context.load_default_certs()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_sock = context.wrap_socket(s, server_hostname='www.0597kk.com')
ssl_sock.connect(('www.0597kk.com', 443))

# ciphers = context.get_ciphers()
# print(ciphers)

ssl_sock.send(b'GET / HTTP/1.1\r\nHOST:www.0597kk.com\r\n\r\n')

file = open('/home/vagrant/response.html', 'bw+')
while True:
    data = ssl_sock.recv(1024)
    file.write(data)
    if data is None:
        break

# for i in range(0, 2):
#     print(data)

