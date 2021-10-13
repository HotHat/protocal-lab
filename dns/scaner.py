from struct import unpack


class Scanner:
    def __init__(self, data: bytes):
        self.data = data
        self.__offset_byte = 0
        self.__len = len(self.data)

    def next_int(self, n=1, unassigned=True):
        assert self.__len - self.__offset_byte >= n

        if n == 1:
            res = self.data[self.__offset_byte]
            self.__offset_byte += 1
            return res
        elif n == 2:
            res = unpack('>' + ('H' if unassigned else 'h'), self.data[self.__offset_byte:self.__offset_byte+2])[0]
            self.__offset_byte += 2
            return res
        elif n == 4:
            res = unpack('>' + ('L' if unassigned else 'l'), self.data[self.__offset_byte:self.__offset_byte+4])[0]
            self.__offset_byte += 4
            return res
        else:
            raise RuntimeError('读取整型字节数只能为1, 2, 4')

    def next_bytes(self, n=1):
        assert self.__len - self.__offset_byte >= n
        res = self.data[self.__offset_byte:self.__offset_byte+n]
        self.__offset_byte += n
        return res

    def is_pointer(self, p):
        return p >> 6 == 3

    def next_name(self, start=0):
        assert self.__len - self.__offset_byte >= 1
        name = []
        idx = self.__offset_byte if start == 0 else start
        ln = self.data[idx]
        # The root domain name is defined by a single octet of zeros the root domain name has no labels
        if ln == 0:
            return '.'

        if self.is_pointer(ln):
            # 0011 1111 1111 1111
            by = self.next_int(2)
            start = by & 0x3fff
            return '.'.join(name) + self.next_name(start)

        while ln != 0:
            assert self.__len - self.__offset_byte >= ln + 1
            l = idx + 1
            h = l + ln
            name.append(str(self.data[l:h], 'utf8'))
            idx = h
            ln = self.data[idx]
            if self.is_pointer(ln):
                by = self.next_int(2)
                start = by & 0x3fff
                return '.'.join(name) + self.next_name(start)

        self.__offset_byte = idx + 1 if start == 0 else self.__offset_byte
        return '.'.join(name)



