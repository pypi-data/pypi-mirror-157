"""Provides for system input and output through data streams,
serialization and the file system. Unless otherwise noted, passing a
null argument to a constructor or method in any class or interface in
this package will cause a NullPointerException to be thrown.
"""

from __future__ import print_function

__all__ = [
    "Closeable",
    "DataOutputStream",
    "FileDescriptor",
    "FileOutputStream",
    "FilterOutputStream",
    "InputStream",
    "OutputStream",
    "PrintStream",
]

from java.lang import AutoCloseable, Object


class Closeable(AutoCloseable):
    def close(self):
        # type: () -> None
        raise NotImplementedError


class FileDescriptor(Object):
    def sync(self):
        pass

    def valid(self):
        pass


class OutputStream(Object):
    def close(self):
        pass

    def flush(self):
        pass

    @staticmethod
    def nullOutputStream():
        return OutputStream()

    def write(self, *args):
        pass


class FileOutputStream(OutputStream):
    def __init__(self, *args):
        pass

    def getChannel(self):
        pass

    def getFD(self):
        print(self)
        return FileDescriptor()


class FilterOutputStream(OutputStream):
    _out = OutputStream()

    def __init__(self, out):
        self._out = out


class DataOutputStream(FilterOutputStream):
    out = None  # type: OutputStream
    written = 0  # type: int

    def __init__(self, out):
        self.out = out
        super(DataOutputStream, self).__init__(out)

    def size(self):
        pass

    def writeBoolean(self, v):
        pass

    def writeByte(self, v):
        pass

    def writeBytes(self, s):
        pass

    def writeChar(self, v):
        pass

    def writeChars(self, s):
        pass

    def writeDouble(self, v):
        pass

    def writeFloat(self, v):
        pass

    def writeInt(self, v):
        pass

    def writeLong(self, v):
        pass

    def writeShort(self, v):
        pass

    def writeUTF(self, s):
        pass


class PrintStream(FilterOutputStream):
    _out = OutputStream()

    def __init__(self, *args):
        print(args)
        super(PrintStream, self).__init__(self._out)

    def append(self, *args):
        pass

    def checkError(self):
        pass

    def clearError(self):
        pass

    def format(self, *args):
        pass

    def print(self, arg):
        pass

    def printf(self, *args):
        pass

    def println(self, arg):
        pass

    def setError(self):
        pass


class InputStream(Object):
    def available(self):
        pass

    def close(self):
        pass

    def mark(self, readlimit):
        pass

    def markSupported(self):
        pass

    def nullInputStream(self):
        pass

    def read(self, *args):
        pass

    def readAllBytes(self):
        pass

    def readNBytes(self, *args):
        pass

    def reset(self):
        pass

    def skip(self, n):
        pass

    def transferTo(self, out):
        pass
