# METADATA
# {}
import io

import J, Application


class _FStream:
    def __init__(self, f):
        self._f = f
        self._buff = io.StringIO()

    def read(self):
        return self._buff.read()

    def write(self, s):
        self._buff.write(s)
        self._f.write(s)

    def __getattr__(self, item):
        return getattr(self._f, item)


@J.API.on_init
def fix_stdout():
    # sys will be in Application
    Application.sys.stdout = _FStream(Application.sys.__stdout__)
    Application.sys.stderr = _FStream(Application.sys.__stderr__)