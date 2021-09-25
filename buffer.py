
class HttpBuffer:
    def __init__(self):
        self.buffer = bytearray()
        self.start = 0
        self.end = len(self.buffer) - 1
        self.position = 0

    def append(self, x):
        self.buffer.extend(x)
        self.end = len(self.buffer)

    # goto next position
    def forward(self, count=1):
        self.position += count

    def backward(self, count=1):
        self.position -= count

    def __getitem__(self, item):
        if isinstance(item, slice):
            # Get the start, stop, and step from the slice
            return [self[ii] for ii in range(*item.indices(len(self.buffer)))]
        elif isinstance(item, int):
            if item < 0:  # Handle negative indices
                item += len(self)
            if item < 0 or item >= len(self.buffer):
                raise IndexError
            return self.buffer[item]  # Get the data from elsewhere
        else:
            raise TypeError

