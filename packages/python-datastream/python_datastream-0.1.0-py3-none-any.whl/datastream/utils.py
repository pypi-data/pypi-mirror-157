import ctypes
import typing


def normalize_byteorder(value: str) -> typing.Literal["big", "little"]:
    if not isinstance(value, str):
        raise TypeError("byteorder must be str")

    value = value.lower()
    if value in {'big', 'be'}:
        return 'big'
    if value in {'little', 'le'}:
        return 'little'

    raise ValueError("byteorder must be in {'big', 'be', 'little', 'le'}")


def get_float_type(size: int):
    for i in {ctypes.c_float, ctypes.c_double, ctypes.c_longdouble}:
        if ctypes.sizeof(i) == size:
            return i

    raise ValueError("Unsupported float size")


def float_from_bytes(data: bytes) -> float:
    float_type = get_float_type(len(data))
    arr = ctypes.ARRAY(ctypes.c_ubyte, len(data)).from_buffer_copy(data)
    return float_type.from_address(ctypes.addressof(arr)).value


def float_to_bytes(data: float, size: int) -> bytes:
    float_type = get_float_type(size)
    val = float_type(data)
    arr = ctypes.ARRAY(ctypes.c_ubyte, size).from_address(ctypes.addressof(val))
    return bytes(arr)
