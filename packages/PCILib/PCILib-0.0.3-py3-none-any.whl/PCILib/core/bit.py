
class bits(object):
    """read-only bits"""
    def __init__(self, b: bytes):
        self.origin_bytes = b
        self.length = len(b) * 8

        # idx和cur_bit是遍历用的
        self.idx = 0
        self.cur_bit = 7

    def __len__(self):
        return self.length

    def get_index(self, i):
        if i < 0:
            i = self.length + i
        if i >= self.length or i < 0:
            # raise IndexError("index out of range")
            raise IndexError(f"index {i} out of range 0:{self.length}")
        return i

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = 0 if item.start is None else self.get_index(item.start)
            stop = self.length if item.stop is None else self.get_index(item.stop)
            step = 1 if item.step is None else item.step
            return ''.join((str(self[i]) for i in range(start, stop, step)))

        item = self.get_index(item)
        return (self.origin_bytes[item // 8] >> (7 - item % 8)) & 1

    def __iter__(self):
        """迭代器，生成迭代对象时调用一次，返回值必须是对象自己，然后for可以循环调用__next__()方法"""
        self.idx = 0
        self.cur_bit = 7
        return self

    def __next__(self):
        """每一次for循环都调用该方法（必须存在）"""
        if self.idx*8+(8-self.cur_bit) > self.length:
            raise StopIteration
        ret_bit = (self.origin_bytes[self.idx] >> self.cur_bit) & 1
        if self.cur_bit==0:
            self.idx+=1
            self.cur_bit=7
        else:
            self.cur_bit-=1
        return ret_bit

    def __str__(self):
        return ''.join((str(x) for x in self))  # ()是生成器语法

    def to_bytes(self):
        return self.origin_bytes


class bitarray(object):
    """writable bit array"""
    def __init__(self, b=None):
        if isinstance(b, (bytearray, list)):
            self.array = b
        elif isinstance(b, (bytes, memoryview)):
            self.array = bytearray(b)
        else:
            self.array = bytearray()
        self.length = len(self.array) * 8

        # idx和cur_bit是遍历用的
        self.idx = 0
        self.cur_bit = 7

    def __len__(self):
        return self.length

    def get_index(self, i):
        if i < 0:
            i = self.length + i
        if i >= self.length or i < 0:
            # raise IndexError("index out of range")
            raise IndexError(f"index {i} out of range 0:{self.length}")
        return i

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = 0 if item.start is None else self.get_index(item.start)
            stop = self.length if item.stop is None else self.get_index(item.stop)
            step = 1 if item.step is None else item.step
            return ''.join((str(self[i]) for i in range(start, stop, step)))

        item = self.get_index(item)
        return (self.array[item // 8] >> (7 - item % 8)) & 1

    def __setitem__(self, key, value):
        if isinstance(value, (bytes, bytearray, memoryview)):
            value = bits(value)

        if isinstance(key, slice):
            start = 0 if key.start is None else self.get_index(key.start)
            stop = self.length if key.stop is None else self.get_index(key.stop)
            step = 1 if key.step is None else key.step
            j = 0
            for i in range(start, stop, step):
                self[i] = value[j]
                j += 1
            return

        if value:
            new_bit = 1
        else:
            new_bit = 0

        key = self.get_index(key)
        k = 7 - key % 8
        self.array[key // 8] = (self.array[key // 8] & (0b11111111&(~(1<<k)))) + (new_bit << k)

    def __iter__(self):
        """迭代器，生成迭代对象时调用一次，返回值必须是对象自己，然后for可以循环调用__next__()方法"""
        self.idx = 0
        self.cur_bit = 7
        return self

    def __next__(self):
        """每一次for循环都调用该方法（必须存在）"""
        if self.idx*8+(8-self.cur_bit) > self.length:
            raise StopIteration
        ret_bit = (self.array[self.idx] >> self.cur_bit) & 1
        if self.cur_bit==0:
            self.idx+=1
            self.cur_bit=7
        else:
            self.cur_bit-=1
        return ret_bit

    def __str__(self):
        return ''.join((str(x) for x in self))  # ()是生成器语法

    def append(self, __bit):
        if __bit:
            new_bit = 1
        else:
            new_bit = 0

        if self.length % 8 == 0:
            self.array.append(new_bit)
        else:
            self.array[-1] = (self.array[-1] << 1) + new_bit
        self.length += 1

    def extend(self, __iterable):
        for x in __iterable:
            self.append(x)

    def to_bytearray(self, copy=False):
        if copy:
            return self.array.copy()
        else:
            return self.array

    def to_bytes(self):
        return bytes(self.array)


if __name__ == '__main__':
    print(bits(b"aaa"))
    print(bits(b"aaa")[:8])

    b=bitarray(b"aaa")
    print(b)
    print(b[::])
    print(b[-6:-1])
    b[:8]=[1,1,1,1,0,0,0,1]
    print(b)
    b[:8]=b"\xff"
    print(b)
