import io
import typing

from . import StreamWrapper, normalize_byteorder, float_from_bytes


class DataInputStream(StreamWrapper):
    __slots__ = ('_byteorder',)

    def __init__(self, fp: io.BufferedIOBase, byteorder: str = 'little'):
        super().__init__(fp)
        self.byteorder = byteorder

    @property
    def byteorder(self) -> typing.Literal["big", "little"]:
        return self._byteorder

    @byteorder.setter
    def byteorder(self, value: str):
        self._byteorder = normalize_byteorder(value)

    def _real_byteorder(self, byteorder: typing.Optional[str] = None) -> typing.Literal["big", "little"]:
        if byteorder is not None:
            return normalize_byteorder(byteorder)
        return self._byteorder

    # bytes

    def read_exact(self, size: int) -> bytes:
        """
        Read exact size bytes from the stream.

        Raises EOFError if eof is reached.
        """
        # XXX: for interactive raw streams (as well as sockets and pipes)
        # a short result does not imply that EOF is imminent.
        data = self.read(size)
        if len(data) != size:
            raise EOFError("EOF")

        return data

    def read_until(self, stop: bytes) -> bytes:
        """
        Read bytes until given terminator is reached.

        Terminator must be bytes with length one.
        Terminator is not included into result, it just skipped.
        """
        result = []

        while True:
            b = self.read(1)
            if not b:
                raise EOFError()

            if b == stop:
                break

            result.append(b[0])

        return bytes(result)

    # other

    def read_bool(self) -> bool:
        """Read single byte boolean value from the stream"""
        return self.read_u1() != 0

    def read_str(self, size: int, encoding=None) -> str:
        """Read string with given size (in bytes) from stream"""
        return self.read_bytes(size).decode(encoding)

    def read_bytesz(self) -> bytes:
        """Read bytes until zero-byte terminator is reached"""
        return self.read_until(b'\x00')

    def read_strz(self, encoding=None) -> str:
        """Read string with zero-byte terminator (c-string)"""
        return self.read_bytesz().decode(encoding)

    read_bytes = read_exact

    # float

    def read_f2(self) -> float:
        """Read float with length 2 bytes value from the stream"""
        return float_from_bytes(self.read_exact(2))

    def read_f4(self) -> float:
        """Read float with length 4 bytes value from the stream"""
        return float_from_bytes(self.read_exact(4))

    def read_f8(self) -> float:
        """Read float with length 8 bytes value from the stream"""
        return float_from_bytes(self.read_exact(8))

    def read_f10(self) -> float:
        """Read float with length 10 bytes value from the stream"""
        return float_from_bytes(self.read_exact(10))

    def read_f16(self) -> float:
        """Read float with length 16 bytes value from the stream"""
        return float_from_bytes(self.read_exact(16))

    read_float = read_f4
    read_double = read_f8
    read_long_double = read_f16

    # java types

    def read_int(self, size: int = 4, *, byteorder: typing.Optional[str] = None, signed: bool = True) -> int:
        """
        Read integer value from the stream.

          size
            Count of bytes to read and size of resulting value.
          byteorder
            The byte order used to represent the integer. If byteorder is 'big', the most significant byte is at the
            beginning of the stream. If byteorder is 'little', the most significant byte is at the end of the stream.
            If byteorder is None (default) class property will be used.
          signed
            Indicates whether two's complement is used to represent the integer.
        """
        data = self.read_exact(size)
        byteorder = self._real_byteorder(byteorder)
        return int.from_bytes(data, byteorder=byteorder, signed=signed)

    def read_uint(self, size: int = 4, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to read_int(size, signed=False)"""
        return self.read_int(size, byteorder=byteorder, signed=False)

    # sX/uX

    def read_u1(self, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to read_uint(1)"""
        return self.read_int(1, byteorder=byteorder, signed=False)

    def read_s1(self, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to read_int(1)"""
        return self.read_int(1, byteorder=byteorder, signed=True)

    def read_u2(self, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to read_uint(2)"""
        return self.read_int(2, byteorder=byteorder, signed=False)

    def read_s2(self, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to read_int(2)"""
        return self.read_int(2, byteorder=byteorder, signed=True)

    def read_u4(self, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to read_uint(4)"""
        return self.read_int(4, byteorder=byteorder, signed=False)

    def read_s4(self, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to read_int(4)"""
        return self.read_int(4, byteorder=byteorder, signed=True)

    def read_u8(self, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to read_uint(8)"""
        return self.read_int(8, byteorder=byteorder, signed=False)

    def read_s8(self, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to read_int(8)"""
        return self.read_int(8, byteorder=byteorder, signed=True)

    read_ubyte = read_u1
    read_byte = read_s1
    read_ushort = read_u2
    read_short = read_s2
    read_ulong = read_u8
    read_long = read_s8
