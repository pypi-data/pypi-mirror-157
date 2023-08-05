import io
import typing

from . import StreamWrapper, normalize_byteorder, float_to_bytes


class DataOutputStream(StreamWrapper):
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

    # other

    def write_bool(self, value: bool) -> int:
        """Write single byte boolean value to the stream"""
        return self.write_u1(bool(value)) != 0

    def write_bytes(self, value: bytes) -> int:
        """Write bytes (like just write(value))"""
        return self.write(value)

    def write_str(self, value: str, encoding=None) -> int:
        """Write string without terminator"""
        return self.write(value.encode(encoding))

    def write_bytesz(self, value: bytes) -> int:
        """Write bytes value with zero byte terminator"""
        cnt = self.write(value)
        return cnt + self.write(b'\x00')

    def write_strz(self, value: str, encoding=None) -> int:
        """Write string value with zero byte terminator (c-string)"""
        return self.write_bytesz(value.encode(encoding))

    # float

    def write_f2(self, value: float) -> int:
        """Write float with length 2 bytes value to the stream"""
        return self.write(float_to_bytes(value, 2))

    def write_f4(self, value: float) -> int:
        """Write float with length 4 bytes value to the stream"""
        return self.write(float_to_bytes(value, 4))

    def write_f8(self, value: float) -> int:
        """Write float with length 8 bytes value to the stream"""
        return self.write(float_to_bytes(value, 8))

    def write_f10(self, value: float) -> int:
        """Write float with length 10 bytes value to the stream"""
        return self.write(float_to_bytes(value, 10))

    def write_f16(self, value: float) -> int:
        """Write float with length 16 bytes value to the stream"""
        return self.write(float_to_bytes(value, 16))

    write_float = write_f4
    write_double = write_f8
    write_long_double = write_f16

    # java types

    def write_int(self, value: int, size: int = 4, *, byteorder: typing.Optional[str] = None, signed=True) -> int:
        """
        Write integer value to the stream.

        Returns the number of bytes written, which is always equal to size.
          size
            Count of bytes to write. An OverflowError is raised if the integer is not representable with the given
            number of bytes.
          byteorder
            The byte order used to represent the integer. If byteorder is 'big', the most significant byte is at the
            beginning of the stream. If byteorder is 'little', the most significant byte is at the end of the stream.
            If byteorder is None (default) class property will be used.
          signed
            Determines whether two's complement is used to represent the integer. If signed is False and a negative
            integer is given, an OverflowError is raised.
        """
        byteorder = self._real_byteorder(byteorder)
        data = value.to_bytes(size, byteorder=byteorder, signed=signed)
        return self.write(data)

    def write_uint(self, value: int, size: int = 4, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to write_int(value, size, signed=False)"""
        return self.write_int(value, size, byteorder=byteorder, signed=False)

    # sX/uX

    def write_u1(self, value: int, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to write_uint(value, 1)"""
        return self.write_int(value, 1, byteorder=byteorder, signed=False)

    def write_s1(self, value: int, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to write_int(value, 1)"""
        return self.write_int(value, 1, byteorder=byteorder, signed=True)

    def write_u2(self, value: int, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to write_uint(value, 2)"""
        return self.write_int(value, 2, byteorder=byteorder, signed=False)

    def write_s2(self, value: int, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to write_int(value, 2)"""
        return self.write_int(value, 2, byteorder=byteorder, signed=True)

    def write_u4(self, value: int, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to write_uint(value, 4)"""
        return self.write_int(value, 4, byteorder=byteorder, signed=False)

    def write_s4(self, value: int, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to write_int(value, 4)"""
        return self.write_int(value, 4, byteorder=byteorder, signed=True)

    def write_u8(self, value: int, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to write_uint(value, 8)"""
        return self.write_int(value, 8, byteorder=byteorder, signed=False)

    def write_s8(self, value: int, *, byteorder: typing.Optional[str] = None) -> int:
        """Alias to write_int(value, 8)"""
        return self.write_int(value, 8, byteorder=byteorder, signed=True)

    write_ubyte = write_u1
    write_byte = write_s1
    write_ushort = write_u2
    write_short = write_s2
    write_ulong = write_u8
    write_long = write_s8
