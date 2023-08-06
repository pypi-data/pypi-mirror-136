# -*- coding: utf-8 -*-

# pylint: disable=missing-docstring,unused-argument,too-many-arguments

import os
import unittest
import doctest
import getpass
import mercurial_extension_utils
import sys

USING_PY3 = sys.version_info >= (3, 0, 0)

# There is strange problem with py3 mercurials ≥ 5.5: doctests
# crash with
#
# Failed example:
#    import mercurial.ui; uio = mercurial.ui.ui()
# …
#      File "…/site-packages/mercurial/utils/procutil.py", line 147, in <module>
#        stdout = _make_write_all(sys.stdout.buffer)
#    AttributeError: '_SpoofOut' object has no attribute 'buffer'
#
# This can be tested separately with
#      import doctest
#      import sys
#      sys.stdout = doctest._SpoofOut()
#      from mercurial.ui import ui       # crashes
#
# and is cause by doctest submitting fake object as sys.stdout. Not sure who
# is guilty, but this .buffer is to know how to .write(…), so let's tech def __iter__(self):

if USING_PY3:
    if not hasattr(doctest._SpoofOut, 'buffer'):
        class FakeBuffer:
            def __init__(self, ioobj):
                self._ioobj = ioobj
            def write(self, *args, **kwargs):
                args = tuple(
                    item.tobytes().decode() if isinstance(item, memoryview) else item
                    for item in args)
                return self._ioobj.write(*args, **kwargs)
        doctest._SpoofOut.buffer = property(lambda self: FakeBuffer(self))

# IMPORTANT NOTE:
#
# As I wanted doctests to be readable, most of them assume
# specific paths and names (for example some tests assume /home/lordvader
# as home directory). This is on purpose,
#
#    >>> normalize_path("~/src")
#    '/home/lordvader/src'
#
# is readable and fulfills documentation role well, whatever I could write
# instead to handle various accounts, would be unreadable mess.
#
# To make running tests possible, below we adapt docstrings
# before executing them.


class FixingUpDocTestParser(doctest.DocTestParser):  # pylint: disable=no-init

    PATTERN_HOME = '/home/lordvader'
    PATTERN_NAME = 'lordvader'
    TRUE_HOME = os.path.expanduser("~")
    TRUE_NAME = getpass.getuser()
    REL_TO_HOME = os.path.relpath(TRUE_HOME)

    def get_doctest(self, string, globs, name, filename, lineno):
        # Replace /home/lordvader with whatever true home is
        # (and similar)
        string = string \
            .replace(self.PATTERN_HOME, self.TRUE_HOME) \
            .replace(self.PATTERN_NAME, self.TRUE_NAME)
        # Special fixup for ../../.. pointing at home
        string = string.replace('"../../..', '"' + self.REL_TO_HOME)
        return doctest.DocTestParser.get_doctest(
            self, string, globs, name, filename, lineno)


def load_tests(loader, tests, pattern):
    if os.name != 'nt':
        if USING_PY3:
            finder = doctest.DocTestFinder(parser=FixingUpDocTestParser())
            suite = doctest.DocTestSuite(
                mercurial_extension_utils,
                test_finder=finder)
        else:
            suite = doctest.DocFileSuite(
                "py2_doctests_mercurial_extension_utils.py",
                module_relative=True,
                globs=mercurial_extension_utils.__dict__,
                parser=FixingUpDocTestParser())
    else:
        if USING_PY3:
            raise Exception("TODO: py3 tests for Windows")
        else:
            suite = doctest.DocFileSuite(
                "py2win_doctests_mercurial_extension_utils.py",
                module_relative=True,
                globs=mercurial_extension_utils.__dict__,
                parser=FixingUpDocTestParser())
    tests.addTests(suite)
    return tests


if __name__ == "__main__":
    unittest.main()

