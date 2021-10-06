from http_buffer import HttpBuffer
import enum


class HttpResponse:
    def __init__(self):
        self.major = 0
        self.minor = 0
        self.code = 0
        self.reason_phrase = ''
        self.headers = {}
        self.message_body = bytearray()

    def set_major(self, major):
        self.major = major

    def set_minor(self, minor):
        self.minor = minor

    def set_code(self, code):
        self.code = code

    def set_reason_phrase(self, reason_phrase):
        self.reason_phrase = reason_phrase

    def set_message_body(self, message_body):
        self.message_body = message_body

    def set_header(self, key, val):
        self.headers[key] = val

    def set_headers(self, headers):
        self.headers = headers


class HttpRequest(HttpResponse):
    def __init__(self):
        HttpResponse.__init__(self)
        self.target = ''
        self.method = ''


class StatusLineState(enum.Enum):
    START = 1
    BEFORE_CODE = 2
    CODE_1 = 10
    CODE_2 = 11
    CODE_3 = 12
    CODE_SPACE = 13
    REASON_PHRASE = 14
    ALMOST_DONE = 15
    DONE = 16


class HeaderState(enum.Enum):
    START = 1
    KEY_VALUE = 2
    ALMOST_DONE = 6


class ChunkState(enum.Enum):
    START = 1
    SIZE = 2
    SIZE_ALMOST_DONE = 3
    EXT_NAME = 4
    BEF_EXT_VAL = 5
    EXT_VAL = 6
    DATA = 15
    DATA_ALMOST_DONE = 26
    TRAILER = 37
    ALMOST_DONE = 48


class HttpVersionState(enum.Enum):
    START = 1
    VER_H = 2
    VER_HT = 3
    VER_HTT = 4
    VER_HTTP = 5
    SLASH = 6
    MAJOR = 7
    DOT = 8
    MINOR = 9


class HttpHeaderState(enum.Enum):
    START = 1
    KEY = 2
    COLON = 3
    OPT_SPACE = 4
    VALUE = 5
    AFT_SPACE = 6
    ALMOST_DONE = 7


class HttpRequestLineState(enum.Enum):
    START = 1
    METHOD = 2
    TARGET = 3
    VERSION = 4
    AFT_VERSION = 5
    ALMOST_DONE = 6


class HttpParseStatus(enum.Enum):
    OK = 1
    ERROR = 2
    AGAIN = 3
    RETRY = 4


class HttpParseState(enum.Enum):
    START_LINE = 1
    HEADERS = 2
    MESSAGE_BODY = 3



class HttpParse:
    def __init__(self):
        """
        :type buf: HttpBuffer
        """
        self.http_parse_state = HttpParseState.START_LINE
        self.status_line_state = StatusLineState.START
        self.header_state = HeaderState.START
        self.chunk_state = ChunkState.START
        self.http_version_state = HttpVersionState.START
        self.http_request_line_state = HttpRequestLineState.START
        self.http_header_state = HttpHeaderState.START
        self.buffer = HttpBuffer()
        self.http_response = HttpResponse()
        self.http_request = HttpRequest()
        # name character space
        # 31  13-
        self.key_name_space = b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0" \
                              b"\0\0\0\0\0\0\0\0\0\0\0\0\0-\0\0" b"0123456789\0\0\0\0\0\0" \
                              b"\0abcdefghijklmnopqrstuvwxyz\0\0\0\0\0" \
                              b"\0abcdefghijklmnopqrstuvwxyz\0\0\0\0\0" \
                              b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0" \
                              b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0" \
                              b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0" \
                              b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
        self.tmp_key = ''
        self.tmp_val = bytearray()
        self.tmp_chunk_size = ''
        self.tmp_chunk_size_remain = 0

    def reset(self):
        self.buffer.start = 0
        self.buffer.end = 0
        self.buffer.position = 0
        self.http_parse_state = HttpParseState.START_LINE
        self.status_line_state = StatusLineState.START
        self.header_state = HeaderState.START
        self.chunk_state = ChunkState.START
        self.http_version_state = HttpVersionState.START
        self.http_request_line_state = HttpRequestLineState.START
        self.http_header_state = HttpHeaderState.START
        self.http_request = HttpRequest()
        self.http_response = HttpResponse()

    def add_buffer(self, data):
        self.buffer.append(data)

    def get_http_response(self):
        return self.http_response

    def __do_again(self):
        self.buffer.forward()
        return HttpParseStatus.AGAIN

    def __raise(self, reason):
        raise Exception(reason)

    @staticmethod
    def __c(x):
        return ord(x)
        # print('code:', code)

    def __is_digit(self, ch):
        if self.__c('0') <= ch <= self.__c('9'):
            return True
        return False

    def __is_token(self, ch):
        if (self.__c('0') <= ch <= self.__c('9')) or \
                (self.__c('a') <= ch <= self.__c('z')) or \
                (self.__c('A') <= ch <= self.__c('Z')):
            return True
        else:
            return False

    def __is_target(self, ch):
        if (self.__c('0') <= ch <= self.__c('9')) or \
                (self.__c('a') <= ch <= self.__c('z')) or \
                (self.__c('A') <= ch <= self.__c('Z')) or \
                self.__c('/') == ch or self.__c('.') == ch:
            return True
        else:
            return False

    def __is_hex(self, char):
        if (self.__c('0') <= char <= self.__c('9')) or \
                (self.__c('a') <= char <= self.__c('f')) or \
                (self.__c('A') <= char <= self.__c('F')):
            return True
        else:
            return False

    def parse_http_version(self, http_request):
        while True:
            idx = self.buffer.position
            if idx >= self.buffer.end:
                break

            ch = self.buffer[idx]
            self.buffer.forward()

            if self.http_version_state == HttpVersionState.START:
                if ch == self.__c('H'):
                    self.http_version_state = HttpVersionState.VER_H
                else:
                    self.__raise(f"{chr(ch)} not match in state START")
            elif self.http_version_state == HttpVersionState.VER_H:
                if ch == self.__c('T'):
                    self.http_version_state = HttpVersionState.VER_HT
                else:
                    self.__raise(chr(ch) + ' not match in state VER_H')

            elif self.http_version_state == HttpVersionState.VER_HT:
                if ch == self.__c('T'):
                    self.http_version_state = HttpVersionState.VER_HTT
                else:
                    self.__raise(chr(ch) + ' not match in state VER_HT')
            elif self.http_version_state == HttpVersionState.VER_HTT:
                if ch == self.__c('P'):
                    self.http_version_state = HttpVersionState.VER_HTTP
                else:
                    self.__raise(chr(ch) + ' not match in state VER_HTT')
            elif self.http_version_state == HttpVersionState.VER_HTTP:
                if ch == self.__c('/'):
                    self.http_version_state = HttpVersionState.SLASH
                else:
                    self.__raise(chr(ch) + ' not match in state VER_HTTP')

            elif self.http_version_state == HttpVersionState.SLASH:
                if self.__is_digit(ch):
                    http_request.major = ch - self.__c('0')
                    self.http_version_state = HttpVersionState.MAJOR
                else:
                    self.__raise(chr(ch) + ' not match in state SLASH')
            elif self.http_version_state == HttpVersionState.MAJOR:
                if ch == self.__c('.'):
                    self.http_version_state = HttpVersionState.MINOR
                else:
                    self.buffer.backward()
                    self.http_version_state = HttpVersionState.START
                    return HttpParseStatus.OK

            elif self.http_version_state == HttpVersionState.MINOR:
                if self.__is_digit(ch):
                    http_request.minor = ch - self.__c('0')
                    self.http_version_state = HttpVersionState.START
                    return HttpParseStatus.OK
                else:
                    self.__raise(chr(ch) + ' not match in state DOT')
            else:
                self.__raise('state not find')

        return HttpParseStatus.AGAIN

    def parse_header(self, request):
        while True:
            idx = self.buffer.position
            if idx >= self.buffer.end:
                break

            ch = self.buffer[idx]
            self.buffer.forward()

            if self.http_header_state == HttpHeaderState.START:
                c = self.key_name_space[ch]
                if c != 0 or ch == self.__c('-'):
                    self.buffer.backward()
                    self.http_header_state = HttpHeaderState.KEY
                else:
                    self.__raise('parse header: ' + chr(ch) + ' not match in state START')

            elif self.http_header_state == HttpHeaderState.KEY:
                c = self.key_name_space[ch]
                if c != 0 or ch == self.__c('-'):
                    self.tmp_key += chr(ch)
                elif ch == self.__c(':'):
                    self.http_header_state = HttpHeaderState.COLON
                else:
                    self.__raise('parse header: ' + chr(ch) + ' not match in state KEY')

            elif self.http_header_state == HttpHeaderState.COLON:
                if ch == self.__c(' '):
                    self.http_header_state = HttpHeaderState.OPT_SPACE
                elif ch == self.__c('\r'):
                    self.http_header_state = HttpHeaderState.ALMOST_DONE
                elif ch == self.__c('\n'):
                    self.http_header_state = HttpHeaderState.START
                    request.headers[self.tmp_key] = ""
                    self.tmp_key = ''
                    return HttpParseStatus.OK
                elif ch == 0:
                    self.__raise('parse header: 0(int) not match in state COLON')
                else:
                    self.buffer.backward()
                    self.http_header_state = HttpHeaderState.VALUE

            elif self.http_header_state == HttpHeaderState.OPT_SPACE:
                if ch == self.__c(' '):
                    continue
                elif ch == 0:
                    self.__raise('parse header: 0(int) not match in state OPT_SPACE')
                else:
                    self.buffer.backward()
                    self.http_header_state = HttpHeaderState.VALUE

            elif self.http_header_state == HttpHeaderState.VALUE:
                if ch == self.__c('\r'):
                    self.http_header_state = HttpHeaderState.ALMOST_DONE
                elif ch == self.__c('\n'):
                    self.http_header_state = HttpHeaderState.START
                    request.headers[self.tmp_key] = str(self.tmp_val, 'utf-8')
                    self.tmp_key = ''
                    self.tmp_val = bytearray()
                    return HttpParseStatus.OK

                elif ch == 0:
                    self.__raise('parse header: 0(int) not match in state VALUE')
                else:
                    self.tmp_val.append(ch)

            elif self.http_header_state == HttpHeaderState.ALMOST_DONE:
                if ch == self.__c('\n'):
                    self.http_header_state = HttpHeaderState.START
                    request.headers[self.tmp_key] = str(self.tmp_val, 'utf-8').rstrip(' ')
                    self.tmp_key = ''
                    self.tmp_val = bytearray()
                    return HttpParseStatus.OK
                else:
                    self.__raise('parse header: 0(int) not match in state ALMOST_DONE')
            else:
                self.__raise('parse header: not match status')

        return HttpParseStatus.AGAIN

    def parse_request_line(self):
        while True:
            idx = self.buffer.position
            if idx >= self.buffer.end:
                break

            ch = self.buffer[idx]
            self.buffer.forward()

            if self.http_request_line_state == HttpRequestLineState.START:
                if self.__is_token(ch):
                    self.buffer.backward()
                    self.http_request_line_state = HttpRequestLineState.METHOD
                else:
                    self.__raise(chr(ch) + ' not match in state START')

            elif self.http_request_line_state == HttpRequestLineState.METHOD:
                if self.__is_token(ch):
                    self.http_request.method += chr(ch)
                elif ch == self.__c(' '):
                    self.http_request_line_state = HttpRequestLineState.TARGET
                else:
                    self.__raise(chr(ch) + ' not match in state METHOD')

            elif self.http_request_line_state == HttpRequestLineState.TARGET:
                if self.__is_target(ch):
                    self.http_request.target += chr(ch)
                elif ch == self.__c(' '):
                    self.http_request_line_state = HttpRequestLineState.VERSION
                else:
                    self.__raise(chr(ch) + ' not match in state TARGET')
            elif self.http_request_line_state == HttpRequestLineState.VERSION:
                self.buffer.backward()
                stat = self.parse_http_version(self.http_request)
                if stat == HttpParseStatus.OK:
                    self.http_request_line_state = HttpRequestLineState.AFT_VERSION
                else:
                    return stat

            elif self.http_request_line_state == HttpRequestLineState.AFT_VERSION:
                if ch == self.__c('\r'):
                    self.http_request_line_state = HttpRequestLineState.ALMOST_DONE
                elif ch == self.__c('\n'):
                    self.http_request_line_state = HttpRequestLineState.START
                    return HttpParseStatus.OK
                else:
                    self.__raise(chr(ch) + ' not match in state ALMOST_DONE')

            elif self.http_request_line_state == HttpRequestLineState.ALMOST_DONE:
                if ch != self.__c('\n'):
                    self.__raise(chr(ch) + ' not match in state ALMOST_DONE')
                else:
                    self.http_request_line_state = HttpRequestLineState.START
                    return HttpParseStatus.OK

        return HttpParseStatus.AGAIN

    def parse_status_line(self):

        while True:
            idx = self.buffer.position
            if idx >= self.buffer.end:
                break

            char = self.buffer[idx]
            self.buffer.forward()

            if self.status_line_state == StatusLineState.START:
                self.buffer.backward()
                stat = self.parse_http_version(self.http_response)
                if stat == HttpParseStatus.OK:
                    self.status_line_state = StatusLineState.BEFORE_CODE
                    continue
                else:
                    return stat

            elif self.status_line_state == StatusLineState.BEFORE_CODE:
                if char != self.__c(' '):
                    return HttpParseStatus.ERROR
                else:
                    self.status_line_state = StatusLineState.CODE_1
                    continue

            elif self.status_line_state == StatusLineState.CODE_1:
                if self.__is_digit(char):
                    self.http_response.set_code(char - self.__c('0'))
                    self.status_line_state = StatusLineState.CODE_2
                else:
                    return HttpParseStatus.ERROR

            elif self.status_line_state == StatusLineState.CODE_2:
                if self.__is_digit(char):
                    # set http major
                    self.http_response.set_code(self.http_response.code * 10 + char - self.__c('0'))
                    self.status_line_state = StatusLineState.CODE_3
                else:
                    return HttpParseStatus.ERROR

            elif self.status_line_state == StatusLineState.CODE_3:
                if self.__is_digit(char):
                    self.http_response.set_code(self.http_response.code * 10 + char - self.__c('0'))
                    self.status_line_state = StatusLineState.CODE_SPACE
                else:
                    return HttpParseStatus.ERROR

            elif self.status_line_state == StatusLineState.CODE_SPACE:
                if char == self.__c(' '):
                    self.status_line_state = StatusLineState.REASON_PHRASE
                else:
                    return HttpParseStatus.ERROR

            elif self.status_line_state == StatusLineState.REASON_PHRASE:
                if char == self.__c('\n'):
                    self.status_line_state = StatusLineState.START
                    return HttpParseStatus.OK
                elif char == self.__c('\r'):
                    self.status_line_state = StatusLineState.ALMOST_DONE
                else:
                    if len(self.http_response.reason_phrase) > 100:
                        return HttpParseStatus.ERROR
                    self.http_response.set_reason_phrase(self.http_response.reason_phrase + chr(char))

            elif self.status_line_state == StatusLineState.ALMOST_DONE:
                if char != self.__c('\n'):
                    return HttpParseStatus.ERROR
                else:
                    self.status_line_state = StatusLineState.START
                    return HttpParseStatus.OK

        return HttpParseStatus.AGAIN

    def parse_request_headers(self):
        return self.parse_headers(self.http_request)

    def parse_response_headers(self):
        return self.parse_headers(self.http_response)

    def parse_headers(self, request):
        while True:
            idx = self.buffer.position
            if idx >= self.buffer.end:
                break

            char = self.buffer[idx]
            self.buffer.forward()

            if self.header_state == HeaderState.START:
                c = self.key_name_space[char]
                if char == self.__c('\r'):
                    self.header_state = HeaderState.ALMOST_DONE
                elif char == self.__c('\n'):
                    self.header_state = HeaderState.START
                    return HttpParseStatus.OK
                elif c == 0 and char != self.__c('-'):
                    return HttpParseStatus.ERROR
                else:
                    self.buffer.backward()
                    self.header_state = HeaderState.KEY_VALUE

            elif self.header_state == HeaderState.KEY_VALUE:
                self.buffer.backward()
                stat = self.parse_header(request)
                if stat == HttpParseStatus.OK:
                    self.header_state = HeaderState.START
                else:
                    return stat

            elif self.header_state == HeaderState.ALMOST_DONE:
                if char == self.__c('\n'):
                    self.header_state = HeaderState.START
                    return HttpParseStatus.OK
                else:
                    return HttpParseStatus.ERROR
        return HttpParseStatus.AGAIN

    def parse_request_chunked(self):
        while True:
            st = self.parse_chunked(self.http_request)
            if st != HttpParseStatus.RETRY:
                return st

    def parse_response_chunked(self):
        while True:
            st = self.parse_chunked(self.http_response)
            if st != HttpParseStatus.RETRY:
                return st

    def parse_chunked(self, request):
        while True:
            idx = self.buffer.position
            if idx >= self.buffer.end:
                return HttpParseStatus.AGAIN

            ch = self.buffer[idx]
            self.buffer.forward()

            if self.chunk_state == ChunkState.START:
                if self.__is_hex(ch):
                    self.buffer.backward()
                    self.chunk_state = ChunkState.SIZE
                else:
                    self.__raise('parse chunked' + chr(ch) + ' not match in state START')

            elif self.chunk_state == ChunkState.SIZE:
                if self.__is_hex(ch):
                    self.tmp_chunk_size += chr(ch)
                elif ch == self.__c('\r'):
                    self.chunk_state = ChunkState.SIZE_ALMOST_DONE
                elif ch == self.__c('\n'):
                    self.chunk_state = ChunkState.DATA
                    self.tmp_chunk_size_remain = int(self.tmp_chunk_size, 16)
                    self.tmp_chunk_size = ''
                elif ch == self.__c(';'):
                    self.chunk_state = ChunkState.EXT_NAME
                else:
                    self.__raise('parse chunked' + chr(ch) + ' not match in state SIZE')

            elif self.chunk_state == ChunkState.EXT_NAME:
                if self.__is_token(ch):
                    # TODO: for chunk extend name
                    continue
                elif ch == self.__c('='):
                    self.chunk_state = ChunkState.BEF_EXT_VAL
                elif ch == self.__c('\r'):
                    self.chunk_state = ChunkState.SIZE_ALMOST_DONE
                elif ch == self.__c('\n'):
                    self.chunk_state = ChunkState.DATA
                    self.tmp_chunk_size_remain = int(self.tmp_chunk_size, 16)
                    self.tmp_chunk_size = ''
                else:
                    self.__raise('parse chunked' + chr(ch) + ' not match in state EXT_NAME')

            elif self.chunk_state == ChunkState.BEF_EXT_VAL:
                if self.__is_token(ch):
                    # TODO: for chunk extend value
                    continue
                elif ch == self.__c('\r'):
                    self.chunk_state = ChunkState.SIZE_ALMOST_DONE
                elif ch == self.__c('\n'):
                    self.chunk_state = ChunkState.DATA
                    self.tmp_chunk_size_remain = int(self.tmp_chunk_size, 16)
                    self.tmp_chunk_size = ''
                else:
                    self.__raise('parse chunked' + chr(ch) + ' not match in state BEF_EXT_VAL')

            elif self.chunk_state == ChunkState.SIZE_ALMOST_DONE:
                if ch == self.__c('\n'):
                    self.tmp_chunk_size_remain = int(self.tmp_chunk_size, 16)
                    self.tmp_chunk_size = ''
                    if self.tmp_chunk_size_remain == 0:
                        self.chunk_state = ChunkState.TRAILER
                    else:
                        self.chunk_state = ChunkState.DATA
                        # for operator data
                        break
                else:
                    self.__raise('parse chunked' + chr(ch) + ' not match in state SIZE_ALMOST_DONE')

            elif self.chunk_state == ChunkState.DATA:
                if self.tmp_chunk_size_remain == 0:
                    if ch == self.__c('\r'):
                        self.chunk_state = ChunkState.DATA_ALMOST_DONE
                    elif ch == self.__c('\n'):
                        self.chunk_state = ChunkState.START
                    else:
                        self.__raise('parse chunked' + chr(ch) + ' not match in state DATA, expect \r or \n')

                else:
                    # fetch more data
                    self.buffer.backward()
                    break

            elif self.chunk_state == ChunkState.DATA_ALMOST_DONE:
                if ch == self.__c('\n'):
                    self.chunk_state = ChunkState.START
                else:
                    self.__raise('parse chunked' + chr(ch) + ' not match in state DATA_ALMOST_DONE')

            elif self.chunk_state == ChunkState.TRAILER:
                self.buffer.backward()
                st = self.parse_headers(request)
                if st == HttpParseStatus.OK:
                    self.chunk_state = ChunkState.START
                    return HttpParseStatus.OK
                else:
                    return st

        if self.chunk_state == ChunkState.DATA:
            size = self.tmp_chunk_size_remain
            left = min(size, self.buffer.end - self.buffer.position)
            # maybe zip content
            self.http_response.message_body.extend(self.buffer[self.buffer.position:self.buffer.position + left])
            self.buffer.forward(left)
            self.tmp_chunk_size_remain -= left
            return HttpParseStatus.RETRY

        return HttpParseStatus.AGAIN

    def parse_http_request(self):
        while True:
            if self.http_parse_state == HttpParseState.START_LINE:
                st = self.parse_request_line()
                if st == HttpParseStatus.OK:
                    self.http_parse_state = HttpParseState.HEADERS
                else:
                    return st
            elif self.http_parse_state == HttpParseState.HEADERS:
                st = self.parse_request_headers()
                if st == HttpParseStatus.OK:
                    return HttpParseStatus.OK
                    # TODO: parse message boy or not
                    # self.http_parse_state = HttpState.HEADERS
                else:
                    return st

            elif self.http_parse_state == HttpParseState.MESSAGE_BODY:
                raise Exception('Not yet implement')

