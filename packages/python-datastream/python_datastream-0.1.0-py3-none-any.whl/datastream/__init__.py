"""
Read and write not only bytes in python (like DataStream in java)
"""
from .utils import float_to_bytes, float_from_bytes, normalize_byteorder
from .stream_wrapper import StreamWrapper, SEEK_CUR, SEEK_SET, SEEK_END
from .data_input_stream import DataInputStream
from .data_output_stream import DataOutputStream

__version__ = "0.1.0"
