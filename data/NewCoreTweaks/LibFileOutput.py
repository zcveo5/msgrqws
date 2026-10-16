import io
import sys


class Log(io.TextIOBase):
    def __init__(self, base):
        self.fl = open('./data/msgr.log', 'w')
        self.base = base

    def write(self, s, /):
        self.base.write(s)
        self.base.flush()
        self.fl.write(s)
        self.fl.flush()

glb['sys'].stdout = sout = Log(sys.modules['sys'].__stdout__)
glb['sys'].stderr = serr = Log(sys.modules['sys'].__stderr__)
glb['sys'].__stdout__ = sout
glb['sys'].__stderr__ = serr

@sys.modules['J'].API.on_exit
def flush():
    print('Flushing!')
    sys.__stdout__.flush()