import enum


class HttpUriState(enum.Enum):
    IPV4_START =  100
    IPV4_SINGLE = 101
    IPV4_DOUBLE = 102
    IPV4_TREBLE = 103
    IPV4_DOT = 104
    PATH_ABEMPTY_START = 200
    PATH_ABEMPTY_SLASH = 201
    PATH_ABEMPTY_SEGMENT = 202
    QUERY_START = 300
    QUERY = 301
    FRAGMENT = 401
    DONT = 500



class HttpUri:
    def __init__(self, uri):
        self.uri = uri
        self.buffer = None
        self.current = 0
        self.ipv4_count = 0
        self.uri_state = HttpUriState.IPV4_START
        self.ipv4_address = []
        self.ipv4_number = ''
        self.scheme = ''
        self.path = ''

    def get_current_char(self):
        return self.uri[self.current]

    def next(self, num=1):
        self.current += num

    def is_end(self):
        return self.current == len(self.uri)

    def forward_match(self, st):
        s_l = len(st)
        ll = len(self.uri) - self.current
        if ll < s_l:
            return False, ''
        match = ''
        for k, v in enumerate(st):
            if isinstance(v, str):
                if self.uri[self.current + k] != v:
                    return False, ''
            # function
            else:
                if not v(self.uri[self.current + k]):
                    return False, ''
            match += self.uri[self.current + k]
        return True, match

    @staticmethod
    def is_gen_delims(ch):
        return ch in [":", "/", "?", "#", "[", "]", "@"]

    @staticmethod
    def is_sub_delims(ch):
        return ch in ["!", "$", "&", "'", "(", ")", "*", "+", ",", ";", "="]

    @staticmethod
    def is_reserved(ch):
        return HttpUri.is_sub_delims(ch) or HttpUri.is_gen_delims(ch)

    @staticmethod
    def is_digit(ch):
        return ch in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    @staticmethod
    def is_alpha(ch):
        return 'a' <= ch <= 'z' or 'A' <= ch <= 'Z'

    @staticmethod
    def is_scheme(ch):
        return HttpUri.is_digit(ch) or HttpUri.is_alpha(ch) or ch in ['+', '-', '.']

    @staticmethod
    def is_hex(ch):
        return HttpUri.is_digit(ch) or ch in ['a', 'b', 'c', 'd', 'e', 'f', 'A', 'B', 'C', 'D', 'E', 'F']

    @staticmethod
    def is_unreserved(ch):
        return HttpUri.is_alpha(ch) or HttpUri.is_digit(ch) or ch in ["-", ".", "_", "~"]

    @staticmethod
    def is_pchar(ch):
        return HttpUri.is_unreserved(ch) or HttpUri.is_digit(ch) or HttpUri.is_sub_delims(ch) or ch in ["%", ":", "@"]

    @staticmethod
    def is_query(ch):
        return HttpUri.is_pchar(ch) or ch in ["/", "?"]

    def parse_pct_encoded(self):
        idx = self.buffer.position
        cur = self.buffer[idx]

    def parse_ipv4(self):
        while not self.is_end():
            if self.ipv4_count == 4:
                return True

            if self.is_end() and self.uri_state != HttpUriState.IPV4_DOT:
                raise Exception('parse ipv4 error')

            if self.uri_state == HttpUriState.IPV4_START:
                if self.is_digit(self.get_current_char()):
                    self.uri_state = HttpUriState.IPV4_SINGLE
                    self.ipv4_number += self.get_current_char()
                    self.next()
                else:
                    raise Exception('parse ipv4 expect digit char' + self.get_current_char())
            elif self.uri_state == HttpUriState.IPV4_SINGLE:
                if self.is_digit(self.get_current_char()):
                    self.uri_state = HttpUriState.IPV4_DOUBLE
                    self.ipv4_number += self.get_current_char()
                    self.next()

                elif self.get_current_char() == '.':
                    self.uri_state = HttpUriState.IPV4_DOT
                    self.next()
                elif self.get_current_char() == '/':
                    self.uri_state = HttpUriState.PATH_ABEMPTY_START
                    break
                else:
                    raise Exception('expect digit char 2')

            elif self.uri_state == HttpUriState.IPV4_DOUBLE:
                if self.is_digit(self.get_current_char()):
                    self.uri_state = HttpUriState.IPV4_TREBLE
                    self.ipv4_number += self.get_current_char()
                    self.next()

                elif self.get_current_char() == '.':
                    self.uri_state = HttpUriState.IPV4_DOT
                    self.next()
                elif self.get_current_char() == '/':
                    self.uri_state = HttpUriState.PATH_ABEMPTY_START
                    break
                else:
                    raise Exception('expect digit char 3')

            elif self.uri_state == HttpUriState.IPV4_TREBLE:
                if self.get_current_char() == '.':
                    self.uri_state = HttpUriState.IPV4_DOT
                    self.next()
                else:
                    raise Exception('expect char dot')
            elif self.uri_state == HttpUriState.IPV4_DOT:
                self.uri_state = HttpUriState.IPV4_START
                num = int(self.ipv4_number, 10)
                if 0 <= num <= 255:
                    self.ipv4_address.append(num)
                    self.ipv4_number = ''
                    self.ipv4_count += 1
                    # not need call self.next()
                else:
                    raise Exception('illegal ipv4 number: ' + str(num))

            else:
                raise Exception('error')

        if self.ipv4_count == 3:
            num = int(self.ipv4_number, 10)
            if 0 <= num <= 255:
                self.ipv4_address.append(num)
                self.ipv4_number = ''
                self.ipv4_count += 1
            else:
                raise Exception('illegal ipv4 number: ' + str(num))
            self.uri_state = HttpUriState.PATH_ABEMPTY_START
            return True
        raise Exception('not match ipv4 address')


    def parse_scheme(self):
        if self.is_end():
            raise Exception('empty scheme')

        if HttpUri.is_alpha(self.get_current_char()):
            self.scheme += self.get_current_char()
            self.next()
            if self.is_end():
                return True

            while HttpUri.is_scheme(self.get_current_char()):
                self.scheme += self.get_current_char()
                self.next()
                if self.is_end():
                    return True
            return True
        else:
            raise Exception(self.get_current_char() + ' is not a alpha')

    def parse_query_fragment(self):
        if self.is_end():
            return True

        while not self.is_end():
            if self.uri_state == HttpUriState.QUERY_START:
                if self.get_current_char() == '?':
                    self.uri_state = HttpUriState.QUERY
                    self.path += self.get_current_char()
                    self.next()
                elif self.get_current_char() == '#':
                    self.uri_state = HttpUriState.FRAGMENT
                    self.path += self.get_current_char()
                    self.next()
                else:
                    raise Exception('parse query not match ?')
            elif self.uri_state == HttpUriState.QUERY:
                if self.get_current_char() == '#':
                    self.uri_state = HttpUriState.FRAGMENT
                    self.path += self.get_current_char()
                    self.next()
                elif self.get_current_char() == '%':
                    t, match = self.forward_match(['%', self.is_hex, self.is_hex])
                    if t:
                        self.path += match
                        self.next(3)
                        continue
                    else:
                        raise Exception('parse path expect percent encoded')
                elif self.is_query(self.get_current_char()):
                    self.path += self.get_current_char()
                    self.next()
                else:
                    raise Exception('parse query not match query char')
            elif self.uri_state == HttpUriState.FRAGMENT:
                if self.get_current_char() == '%':
                    t, match = self.forward_match(['%', self.is_hex, self.is_hex])
                    if t:
                        self.path += match
                        self.next(3)
                        continue
                    else:
                        raise Exception('parse path expect percent encoded')
                elif self.is_query(self.get_current_char()):
                    self.path += self.get_current_char()
                    self.next()
                else:
                    raise Exception('parse query not match query char')
            else:
                raise Exception('parse query not match state')
        self.uri_state = HttpUriState.DONT

    def parse_path_abempty(self):
        if self.is_end():
            return True

        while not self.is_end():
            if self.uri_state == HttpUriState.PATH_ABEMPTY_START:
                if self.get_current_char() != '/':
                    raise Exception('parse path abempty expect /')
                self.path += '/'
                self.uri_state = HttpUriState.PATH_ABEMPTY_SLASH
                self.next()

            elif self.uri_state == HttpUriState.PATH_ABEMPTY_SLASH:
                if HttpUri.is_pchar(self.get_current_char()):
                    self.uri_state = HttpUriState.PATH_ABEMPTY_SEGMENT
                else:
                    raise Exception('parse path expect pchar but get ' + self.get_current_char())

            elif self.uri_state == HttpUriState.PATH_ABEMPTY_SEGMENT:
                if self.get_current_char() == '/':
                    self.uri_state = HttpUriState.PATH_ABEMPTY_START
                    continue

                elif self.get_current_char() == '?' or self.get_current_char() == '#':
                    self.uri_state = HttpUriState.QUERY_START
                    return True

                elif HttpUri.is_pchar(self.get_current_char()):
                    self.uri_state = HttpUriState.PATH_ABEMPTY_SEGMENT

                    if self.get_current_char() == '%':
                        t, match = self.forward_match(['%', self.is_hex, self.is_hex])
                        if t:
                            self.path += match
                            self.next(3)
                            continue
                        else:
                            raise Exception('parse path expect percent encoded')
                    else:
                        self.path += self.get_current_char()
                        self.next()

                else:
                    raise Exception('parse path expect pchar but get ' + self.get_current_char())
            else:
                raise Exception('parse path unexpect state')
        self.uri_state = HttpUriState.DONT
        return True

    def parse_uri(self):
        self.parse_scheme()
        t, _ = self.forward_match('://')
        if not t:
            raise Exception('not match //')
        self.next(3)
        self.parse_ipv4()
        self.parse_path_abempty()
        self.parse_query_fragment()


