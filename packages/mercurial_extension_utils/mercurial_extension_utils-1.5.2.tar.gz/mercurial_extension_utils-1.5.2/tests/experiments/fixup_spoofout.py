
import doctest
import sys
orig_stdout = sys.stdout
sys.stdout = doctest._SpoofOut()

class FakeBuffer:
    def __init__(self, ioobj):
        self._ioobj = ioobj
    def write(self, *args, **kwargs):
        # Typowo jestesmy wołani z memoryview, to nie jest obsługiwane
        args = tuple(
            item.tobytes().decode() if isinstance(item, memoryview) else item
            for item in args)
        # sys.stderr.write(repr(args))
        # sys.stderr.write(repr(kwargs))
        return self._ioobj.write(*args, **kwargs)
        # There is an error with high characters, byte vs char len.

doctest._SpoofOut.buffer = property(lambda self: FakeBuffer(self))

from mercurial.ui import ui
uio = ui()
uio.write(b"Hej")
uio.write(b"Kup sobie klej")
uio.write(u"Żółw".encode('utf-8'))   # somewhat breaks

orig_stdout.write("Aggregated data:\n")
orig_stdout.write(sys.stdout.getvalue())
