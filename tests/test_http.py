import unittest
from http_parser import *


class TestHttp(unittest.TestCase):
    # def __init__(self):
    #     pass

    def test_status_line_text(self):
        response = b'HTTP/2 304 Not Modified\r\n'
        buffer = HttpBuffer()
        buffer.append(response)
        parser = HttpParse(buffer)
        status = parser.parse_status_line()
        print(status)


    def test_head_text(self):
        response = b'date: Mon, 20 Sep 2021 13:30:22 GMT\r\n' \
                   b'via: 1.1 varnish\r\n' \
                   b'etag: "613548ad-31283"\r\n' \
                   b'age: 362104\r\n' \
                   b'x-served-by: cache-hkg17929-HKG\r\n' \
                   b'x-cache: HIT\r\n' \
                   b'x-cache-hits: 2\r\n' \
                   b'x-timer: S1632144622.136722,VS0,VE1\r\n' \
                   b'vary: Accept-Encoding\r\n' \
                   b'X-Firefox-Spdy: h2\r\n\r\n'

        buffer = HttpBuffer()
        buffer.append(response)
        parser = HttpParse(buffer)
        status = parser.parse_headers()
        print(status)

    def test_header_file(self):
        file = open('/home/vagrant/header.html', 'br')
        content = file.read()
        buffer = HttpBuffer()
        buffer.append(content)
        parser = HttpParse(buffer)
        status = parser.parse_status_line()
        status = parser.parse_headers()
        print(status)
        print(parser.http_response.headers)

    def test_chunk_text(self):
        chunk_test = b'5\r\n' \
                     b'12345\r\n' \
                     b'5\r\n' \
                     b'67890\r\n' \
                     b'0\r\n\r\n'
        buffer = HttpBuffer()
        buffer.append(chunk_test)
        parser = HttpParse(buffer)
        status = parser.parse_chunked()
        print(status)
        while True:
            if status == HttpParseStatus.RETRY:
                status = parser.parse_chunked()

            if status == HttpParseStatus.OK:
                print('parse chunk ok')
                break

    def test_chunk_file(self):
        file = open('/home/vagrant/chunk.html', 'br')
        content = file.read()
        buffer = HttpBuffer()
        buffer.append(content)
        parser = HttpParse(buffer)
        while True:
            status = parser.parse_chunked()
            if status != HttpParseStatus.RETRY:
                break

        print(str(parser.http_response.message_body, 'gbk'))

    def test_response(self):
        file = open('/home/vagrant/response.html', 'br')
        content = file.read()
        buffer = HttpBuffer()
        buffer.append(content)
        parser = HttpParse(buffer)
        status = parser.parse_status_line()
        print(status)
        status = parser.parse_headers()
        print(status)
        while True:
            status = parser.parse_chunked()
            if status != HttpParseStatus.RETRY:
                break

        print(status)