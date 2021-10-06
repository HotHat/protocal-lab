import unittest
from http.http_uri import *


class TestUri(unittest.TestCase):
    def test_ipv4(self):
        for i in ['255.255.255.255', '0.0.0.0', '1.1.1.344', '12.12.12.12']:
            uri = HttpUri(i)
            uri.parse_ipv4()
            print(uri.ipv4_address)

    def test_scheme(self):
        for i in ['ftp://', 'http://', 'https://', 'http']:
            uri = HttpUri(i)
            uri.parse_scheme()
            print(uri.scheme)

    def test_is_pchar(self):
        self.assertEqual(HttpUri.is_pchar('a'), True)
        self.assertEqual(HttpUri.is_pchar('1'), True)
        self.assertEqual(HttpUri.is_pchar('-'), True)
        self.assertEqual(HttpUri.is_pchar(':'), True)
        self.assertEqual(HttpUri.is_pchar('!'), True)
        self.assertEqual(HttpUri.is_pchar('%'), True)

    def test_segment(self):
        for i in ['/%20%20%82%32%af', '/abc/', '/abc/def', '']:
            uri = HttpUri(i)
            uri.uri_state = HttpUriState.PATH_ABEMPTY_START
            uri.parse_path_abempty()
            print(uri.path)

    def test_query(self):
        for i in ['?abc=123%13%24%83#haha', '#haha']:
            uri = HttpUri(i)
            uri.uri_state = HttpUriState.QUERY_START
            uri.parse_query_fragment()
            print(uri.path)

    def test_forward_match(self):
        uri = HttpUri('abc')
        t = uri.forward_match('a')
        print(t)
        t = uri.forward_match('ab')
        print(t)
        t = uri.forward_match('abc')
        print(t)
        t = uri.forward_match('b')
        print(t)
        t = uri.forward_match('abcd')
        print(t)

    def test_forward_match_fun(self):
        uri = HttpUri('20')
        t = uri.forward_match_fun([HttpUri.is_digit, HttpUri.is_digit])
        print(t)

    def test_scheme(self):
        for i in ['http://127.0.0.1/api/index%20?abc=123']:
            uri = HttpUri(i)
            uri.parse_uri()
            print(uri.scheme)
            print(uri.ipv4_address)
            print(uri.path)


