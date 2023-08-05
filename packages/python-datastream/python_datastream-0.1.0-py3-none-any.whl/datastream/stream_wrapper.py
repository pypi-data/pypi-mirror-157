import io


SEEK_SET = io.SEEK_SET
SEEK_CUR = io.SEEK_CUR
SEEK_END = io.SEEK_END


class StreamWrapper(io.BufferedIOBase):
    __slots__ = ('_fp', )
    """
    Wraps buffered stream
    """
    def __init__(self, fp: io.BufferedIOBase):
        self._fp = fp

    def close(self):
        """
        Flush and close the IO object.

        This method has no effect if the file is already closed.
        """
        self._fp.close()

    @property
    def closed(self):
        return self._fp.closed

    def fileno(self):
        """
        Returns underlying file descriptor if one exists.

        OSError is raised if the IO object does not use a file descriptor.
        """
        return self._fp.fileno()

    def flush(self):
        """
        Flush write buffers, if applicable.

        This is not implemented for read-only and non-blocking streams.
        """
        self._fp.flush()

    def isatty(self):
        """
        Return whether this is an 'interactive' stream.

        Return False if it can't be determined.
        """
        return self._fp.isatty()

    def readable(self):
        """
        Return whether object was opened for reading.

        If False, read() will raise OSError.
        """
        return self._fp.readable()

    def seekable(self):
        """
        Return whether object supports random access.

        If False, seek(), tell() and truncate() will raise OSError.
        This method may need to do a test seek().
        """
        return self._fp.seekable()

    def writable(self):
        """
        Return whether object was opened for writing.

        If False, write() will raise OSError.
        """
        return self._fp.writable()

    def readline(self, __size=None):
        """
        Read and return a line from the stream.

        If size is specified, at most size bytes will be read.

        The line terminator is always b'\n' for binary files; for text
        files, the newlines argument to open can be used to select the line
        terminator(s) recognized.
        """
        return self._fp.readline(__size)

    def readlines(self, __hint=None):
        """
        Return a list of lines from the stream.

        hint can be specified to control the number of lines read: no more
        lines will be read if the total size (in bytes/characters) of all
        lines so far exceeds hint.
        """
        return self._fp.readlines(__hint)

    def writelines(self, __lines):
        """
        Write a list of lines to stream.

        Line separators are not added, so it is usual for each of the
        lines provided to have a line separator at the end.
        """
        self._fp.writelines(__lines)

    def seek(self, __offset, __whence=SEEK_SET):
        """
        Change stream position.

        Change the stream position to the given byte offset. The offset is
        interpreted relative to the position indicated by whence.  Values
        for whence are:

        * 0 -- start of stream (the default); offset should be zero or positive
        * 1 -- current stream position; offset may be negative
        * 2 -- end of stream; offset is usually negative

        Return the new absolute position.
        """
        return self._fp.seek(__offset, __whence)

    def tell(self):
        """ Return current stream position. """
        return self._fp.tell()

    def truncate(self, __size=None):
        """
        Truncate file to size bytes.

        File pointer is left unchanged.  Size defaults to the current IO
        position as reported by tell().  Returns the new size.
        """
        return self._fp.truncate(__size)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        return self.readline()

    @property
    def raw(self):
        return self._fp.raw

    def detach(self):
        """
        Disconnect this buffer from its underlying raw stream and return it.

        After the raw stream has been detached, the buffer is in an unusable
        state.
        """
        return self._fp.detach()

    def read(self, __size=None):
        """
        Read and return up to n bytes.

        If the argument is omitted, None, or negative, reads and
        returns all data until EOF.

        If the argument is positive, and the underlying raw stream is
        not 'interactive', multiple raw reads may be issued to satisfy
        the byte count (unless EOF is reached first).  But for
        interactive raw streams (as well as sockets and pipes), at most
        one raw read will be issued, and a short result does not imply
        that EOF is imminent.

        Returns an empty bytes object on EOF.

        Returns None if the underlying raw stream was open in non-blocking
        mode and no data is available at the moment.
        """
        return self._fp.read(__size)

    def read1(self, __size=None):
        """
        Read and return up to n bytes, with at most one read() call
        to the underlying raw stream. A short result does not imply
        that EOF is imminent.

        Returns an empty bytes object on EOF.
        """
        return self._fp.read1(__size)

    def readinto(self, __buffer):
        return self._fp.readinto(__buffer)

    def readinto1(self, __buffer):
        return self._fp.readinto1(__buffer)

    def write(self, __buffer):
        """
        Write the given buffer to the IO stream.

        Returns the number of bytes written, which is always the length of b
        in bytes.

        Raises BlockingIOError if the buffer is full and the
        underlying raw stream cannot accept more data at the moment.
        """
        return self._fp.write(__buffer)

    def peek(self, __size):
        return self._fp.peek(__size)

    @property
    def mode(self):
        return self._fp.mode

    @property
    def name(self):
        return self._fp.name
