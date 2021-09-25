from buffer import HttpBuffer
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


class StatusLineState(enum.Enum):
    START = 1
    H = 2
    HT = 3
    HTT = 4
    HTTP = 5
    SLASH = 6
    MAJOR = 7
    MINOR = 8
    MINOR_SPACE = 9
    CODE_1 = 10
    CODE_2 = 11
    CODE_3 = 12
    CODE_SPACE = 13
    REASON_PHRASE = 14
    ALMOST_DONE = 15
    DONE = 16


class HeaderState(enum.Enum):
    START = 1
    KEY = 2
    VALUE = 3
    OPTION_SPACE = 4
    ALMOST_DONE = 5
    HEADER_ALMOST_DONE = 6
    HEADER_DONE = 7


class ChunkState(enum.Enum):
    START = 1
    SIZE = 2
    SIZE_ALMOST_DONE = 3
    extend = 4
    DATA = 5
    DATA_ALMOST_DONE = 6
    TRAILER = 7
    CHUNK_ALMOST_DONE = 8


class HttpParseStatus(enum.Enum):
    OK = 1
    ERROR = 2
    AGAIN = 3
    RETRY = 4


class HttpParse:
    def __init__(self, buf: HttpBuffer):
        """
        :type buf: HttpBuffer
        """
        self.status_line_state = StatusLineState.START
        self.header_state = HeaderState.START
        self.chunk_state = ChunkState.START
        self.buffer = buf
        self.http_response = HttpResponse()
        # name character space
        self.key_name_space = b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0" \
                              b"\0\0\0\0\0\0\0\0\0\0\0\0\0-\0\00123456789\0\0\0\0\0\0" \
                              b"\0abcdefghijklmnopqrstuvwxyz\0\0\0\0\0" \
                              b"\0abcdefghijklmnopqrstuvwxyz\0\0\0\0\0" \
                              b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0" \
                              b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0" \
                              b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0" \
                              b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
        self.tmp_key = ''
        self.tmp_val = ''
        self.tmp_chunk_size = ''
        self.tmp_chunk_size_remain = 0

    def get_http_response(self):
        return self.http_response

    def __do_again(self):
        self.buffer.forward()
        return HttpParseStatus.AGAIN
    
    @staticmethod
    def __c(x):
        code = bytes(x, 'utf-8')[0]
        # print('code:', code)
        return code

    def __is_hex(self, char):
        if (char >= self.__c('0') and char <= self.__c('9')) or \
           (char >= self.__c('a') and char <= self.__c('f')) or \
           (char >= self.__c('A') and char <= self.__c('A')):
            return True
        else:
            return False

    def parse_status_line(self):

        for i in range(self.buffer.position, self.buffer.end):
            char = self.buffer[i]
            self.buffer.forward()

            if self.status_line_state == StatusLineState.START:
                if char != self.__c('H'):
                    return HttpParseStatus.ERROR
                else:
                    self.status_line_state = StatusLineState.H
                    continue

            elif self.status_line_state == StatusLineState.H:
                if char != self.__c('T'):
                    return HttpParseStatus.ERROR
                else:
                    self.status_line_state = StatusLineState.HT
                    continue

            elif self.status_line_state == StatusLineState.HT:
                if char != self.__c('T'):
                    return HttpParseStatus.ERROR
                else:
                    self.status_line_state = StatusLineState.HTT
                    continue

            elif self.status_line_state == StatusLineState.HTT:
                if char != self.__c('P'):
                    return HttpParseStatus.ERROR
                else:
                    self.status_line_state = StatusLineState.HTTP
                    continue
                pass

            elif self.status_line_state == StatusLineState.HTTP:
                if char != self.__c('/'):
                    return HttpParseStatus.ERROR
                else:
                    self.status_line_state = StatusLineState.SLASH
                    continue

            elif self.status_line_state == StatusLineState.SLASH:
                if char < self.__c('0') or char > self.__c('9'):
                    return HttpParseStatus.ERROR
                else:
                    # set http major
                    self.http_response.set_major(char - self.__c('0'))
                    self.status_line_state = StatusLineState.MAJOR
                    continue

            elif self.status_line_state == StatusLineState.MAJOR:
                if char == self.__c('.'):
                    self.status_line_state = StatusLineState.MINOR
                    continue

                elif char == self.__c(' '):
                    self.status_line_state = StatusLineState.CODE_1
                    continue
                else:
                    return HttpParseStatus.ERROR

            elif self.status_line_state == StatusLineState.MINOR:
                if char < self.__c('0') or char > self.__c('9'):
                    return HttpParseStatus.ERROR
                else:
                    # set http minor
                    self.http_response.set_minor(char - self.__c('0'))
                    self.status_line_state = StatusLineState.MINOR_SPACE
                    continue
            elif self.status_line_state == StatusLineState.MINOR_SPACE:
                if char == self.__c(' '):
                    self.status_line_state = StatusLineState.CODE_1
                else:
                    return HttpParseStatus.ERROR

            elif self.status_line_state == StatusLineState.CODE_1:
                if char < self.__c('0') or char > self.__c('9'):
                    return HttpParseStatus.ERROR
                else:
                    # set http major
                    self.http_response.set_code(char - self.__c('0'))
                    self.status_line_state = StatusLineState.CODE_2
                    continue

            elif self.status_line_state == StatusLineState.CODE_2:
                if char < self.__c('0') or char > self.__c('9'):
                    return HttpParseStatus.ERROR
                else:
                    # set http major
                    self.http_response.set_code(self.http_response.code * 10 + char - self.__c('0'))
                    self.status_line_state = StatusLineState.CODE_3
                    continue

            elif self.status_line_state == StatusLineState.CODE_3:
                if char < self.__c('0') or char > self.__c('9'):
                    return HttpParseStatus.ERROR
                else:
                    # set http major
                    self.http_response.set_code(self.http_response.code * 10 + char - self.__c('0'))
                    self.status_line_state = StatusLineState.CODE_SPACE
                    continue
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
                    continue
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

    def parse_headers(self):
        for i in range(self.buffer.position, self.buffer.end):
            char = self.buffer[i]
            self.buffer.forward()

            if self.header_state == HeaderState.START:
                c = self.key_name_space[char]
                if c is None:
                    return HttpParseStatus.ERROR
                elif char == self.__c('\r'):
                    self.header_state = HeaderState.HEADER_ALMOST_DONE
                    continue
                elif char == self.__c('\n'):
                    self.header_state = HeaderState.START
                    return HttpParseStatus.OK
                else:
                    self.header_state = HeaderState.KEY
                    self.tmp_key += chr(char)
                    continue

            elif self.header_state == HeaderState.KEY:
                c = self.key_name_space[char]
                if c is None:
                    return HttpParseStatus.ERROR

                elif char == self.__c(':'):
                    self.header_state = HeaderState.VALUE
                    continue
                else:
                    self.tmp_key += chr(char)

            elif self.header_state == HeaderState.VALUE:
                if char == self.__c('\r'):
                    self.header_state = HeaderState.ALMOST_DONE
                    self.http_response.set_header(self.tmp_key, self.tmp_val.strip(' '))
                    self.tmp_val = self.tmp_key = ''
                    continue
                elif char == self.__c('\n'):
                    self.header_state = HeaderState.START
                    # set header map
                    self.http_response.set_header(self.tmp_key, self.tmp_val.strip(' '))
                    self.tmp_val = self.tmp_key = ''
                    continue
                else:
                    self.tmp_val += chr(char)

            elif self.header_state == HeaderState.ALMOST_DONE:
                if char == self.__c('\n'):
                    self.header_state = HeaderState.START
                else:
                    return HttpParseStatus.ERROR

            elif self.header_state == HeaderState.HEADER_ALMOST_DONE:
                if char == self.__c('\n'):
                    self.header_state = HeaderState.HEADER_DONE
                    return HttpParseStatus.OK
                else:
                    return HttpParseStatus.ERROR
        return HttpParseStatus.AGAIN

    def parse_chunked(self):
        for i in range(self.buffer.position, self.buffer.end):
            char = self.buffer[i]
            print(chr(char))
            self.buffer.forward()
            if self.chunk_state == ChunkState.START:
                if self.__is_hex(char):
                    self.chunk_state = ChunkState.SIZE
                    self.tmp_chunk_size += chr(char)
                    continue
                # elif char == self.__c('\r'):
                #     self.chunk_state = ChunkState.CHUNK_ALMOST_DONE
                #     continue
                # elif char == self.__c('\n'):
                #     return HttpParseStatus.OK
                else:
                    return HttpParseStatus.ERROR

            elif self.chunk_state == ChunkState.SIZE:
                if self.__is_hex(char):
                    self.tmp_chunk_size += chr(char)
                elif char == self.__c('\r'):
                    self.chunk_state = ChunkState.SIZE_ALMOST_DONE
                    continue
                elif char == self.__c('\n'):
                    self.chunk_state = ChunkState.DATA
                    self.tmp_chunk_size_remain = int(self.tmp_chunk_size, 16)
                    self.tmp_chunk_size = ''
                    continue
                else:
                    # TODO: missing chunk extend parse
                    return HttpParseStatus.ERROR

            elif self.chunk_state == ChunkState.SIZE_ALMOST_DONE:
                if char == self.__c('\n'):
                    self.tmp_chunk_size_remain = int(self.tmp_chunk_size, 16)
                    self.tmp_chunk_size = ''
                    if self.tmp_chunk_size_remain == 0:
                        self.chunk_state = ChunkState.TRAILER
                        continue
                    else:
                        # fetch data
                        self.chunk_state = ChunkState.DATA
                        continue
                else:
                    return HttpParseStatus.ERROR

            elif self.chunk_state == ChunkState.DATA:
                if self.tmp_chunk_size_remain == 0:
                    if char == self.__c('\r'):
                        self.chunk_state = ChunkState.DATA_ALMOST_DONE
                        continue
                    elif char == self.__c('\n'):
                        self.chunk_state = ChunkState.START
                        continue
                    else:
                        return HttpParseStatus.ERROR

                else:
                    self.buffer.backward()
                    break

            elif self.chunk_state == ChunkState.DATA_ALMOST_DONE:
                if char == self.__c('\n'):
                    self.chunk_state = ChunkState.START
                else:
                    return HttpParseStatus.ERROR

            elif self.chunk_state == ChunkState.TRAILER:
                if char == self.__c('\r'):
                    self.chunk_state = ChunkState.CHUNK_ALMOST_DONE
                elif char == self.__c('\n'):
                    return HttpParseStatus.OK
                else:
                    return HttpParseStatus.ERROR

            elif self.chunk_state == ChunkState.CHUNK_ALMOST_DONE:
                if char == self.__c('\n'):
                    return HttpParseStatus.OK
                else:
                    return HttpParseStatus.ERROR
            else:
                return HttpParseStatus.ERROR

        if self.chunk_state == ChunkState.DATA:
            size = self.tmp_chunk_size_remain
            left = min(size, self.buffer.end - self.buffer.position)
            # maybe zip content
            self.http_response.message_body.extend(self.buffer[self.buffer.position:self.buffer.position+left])
            self.buffer.forward(left)
            self.tmp_chunk_size_remain -= left
            return HttpParseStatus.RETRY

        return HttpParseStatus.AGAIN


if '__main__' == __name__:
    response = b'HTTP/2 304 Not Modified\r\n' \
               b'date: Mon, 20 Sep 2021 13:30:22 GMT\r\n' \
               b'via: 1.1 varnish\r\n' \
               b'etag: "613548ad-31283"\r\n' \
               b'age: 362104\r\n' \
               b'x-served-by: cache-hkg17929-HKG\r\n' \
               b'x-cache: HIT\r\n' \
               b'x-cache-hits: 2\r\n' \
               b'x-timer: S1632144622.136722,VS0,VE1\r\n' \
               b'vary: Accept-Encoding\r\n' \
               b'X-Firefox-Spdy: h2\r\n\r\n' \
               b'5\r\n' \
               b'533333' \
               b'0\r\n\r\n'
    chunk_test = b'5\r\n' \
                 b'12345\r\n' \
                 b'5\r\n' \
                 b'67890\r\n' \
                 b'0\r\n\r\n'
    buffer = HttpBuffer()
    buffer.append(response)
    parser = HttpParse(buffer)
    status = parser.parse_status_line()
    status = parser.parse_headers()
    print(status)
    while True:
        if status == HttpParseStatus.RETRY:
            status = parser.parse_headers()

        if status == HttpParseStatus.OK:
            print('parse chunk ok')
            break
    # while True:
    #     status = parser.parse_request_line()
    #     if status == HttpParseStatus.OK:
    #         print('parse status line done!')
    #     elif status == HttpParseStatus.ERROR:
    #         print('parse status error happen!')
    #         break
    #
    #     status = parser.parse_headers()
    #
    #     if status == HttpParseStatus.OK:
    #         print('parse headers line done!')
    #         break
    #     elif status == HttpParseStatus.ERROR:
    #         print('parse headers error happen!')
    #         break
    #     else:
    #         print('parse headers again!')

    # print(status)

    print('---')
