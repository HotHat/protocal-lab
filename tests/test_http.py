import unittest
from http.http_parser import *


class TestHttp(unittest.TestCase):
    # def __init__(self):
    #     pass

    def test_status_line_text(self):
        response = b'HTTP/2.1 304 Not Modified\r\n'
        buffer = HttpBuffer()
        buffer.append(response)
        parser = HttpParse(buffer)
        status = parser.parse_status_line()
        print(status)
        print(parser.http_response.major)
        print(parser.http_response.minor)
        print(parser.http_response.code)
        print(parser.http_response.reason_phrase)

    def test_request_line_text(self):
        response = b'GET / HTTP/1.1\r\nHost: 192.168.33.10:8888\r\nConnection: keep-alive\r\nCache-Control: max-age=0\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7\r\n\r\n'
        parser = HttpParse()
        parser.add_buffer(response)
        status = parser.parse_http_request()
        print(status)
        print(parser.http_request.major)
        print(parser.http_request.minor)
        print(parser.http_request.method)
        print(parser.http_request.target)
        print(parser.http_request.headers)


    def test_head_text(self):
        response = b'x-served-by:     cache-hkg17929-HKG\r\n'
        buffer = HttpBuffer()
        buffer.append(response)
        parser = HttpParse(buffer)
        status = parser.parse_header(parser.http_response)
        print(status)
        print(parser.http_response.headers)


    def test_heads_text(self):
        # response = b'date: Mon, 20 Sep 2021 13:30:22 GMT\r\n' \
        #            b'via: 1.1 varnish\r\n' \
        #            b'etag: "613548ad-31283"\r\n' \
        #            b'age: 362104\r\n' \
        response = b'x-served-by: cache-hkg17929-HKG\r\n' \
                   b'x-cache: HIT\r\n' \
                   b'x-cache-hits: 2\r\n' \
                   b'x-timer: S1632144622.136722,VS0,VE1\r\n' \
                   b'vary: Accept-Encoding\r\n' \
                   b'X-Firefox-Spdy: h2\r\n\r\n'

        buffer = HttpBuffer()
        buffer.append(response)
        parser = HttpParse(buffer)
        while True:
            status = parser.parse_headers(parser.http_response)
            if status == HttpParseStatus.RETRY:
                continue
            else:
                break
        print(status)
        print(parser.http_response.headers)

    def test_header_file(self):
        file = open('/home/vagrant/header.html', 'br')
        content = file.read()
        buffer = HttpBuffer()
        buffer.append(content)
        parser = HttpParse(buffer)
        status = parser.parse_status_line()
        print(status)
        print(parser.http_response.major)
        print(parser.http_response.minor)
        print(parser.http_response.code)
        print(parser.http_response.reason_phrase)
        status = parser.parse_response_headers()
        print(status)
        print(parser.http_response.headers)

    def test_chunk_text(self):
        chunk_test = b'5;extname=value\r\n' \
                     b'12345\r\n' \
                     b'5\r\n' \
                     b'67890\r\n' \
                     b'0\r\n' \
                     b'x-served-by: cache-hkg17929-HKG\r\n' \
                     b'x-cache: HIT\r\n' \
                     b'x-cache-hits: 2\r\n' \
                     b'x-timer: S1632144622.136722,VS0,VE1\r\n' \
                     b'\r\n'
        buffer = HttpBuffer()
        buffer.append(chunk_test)
        parser = HttpParse(buffer)
        status = parser.parse_response_chunked()
        print(status)
        print(parser.http_response.headers)
        print(parser.http_response.message_body)

    def test_chunk_file(self):
        file = open('/home/vagrant/chunk.html', 'br')
        content = file.read()
        parser = HttpParse()
        parser.add_buffer(content)
        status = parser.parse_response_chunked()
        print(status)
        print(str(parser.http_response.message_body, 'gbk'))

    def test_response(self):
        file = open('/home/vagrant/response.html', 'br')
        content = file.read()
        parser = HttpParse()
        parser.add_buffer(content)
        status = parser.parse_http_request()
        # status = parser.parse_status_line()
        print(status)
        # status = parser.parse_response_headers()
        # print(status)
        # status = parser.parse_response_chunked()
        # print(status)
