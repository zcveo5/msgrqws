import sys
from typing import TextIO
class StdoutReader:
    def __init__(self, file=TextIO):
        self.file = file
        self.__StdoutReader_buffer__ = []

    def write(self, s, /):
        self.__StdoutReader_buffer__.append(s)
        sys.__stdout__.write(s)

    def read(self, n=-1, /):
        return ''.join(self.__StdoutReader_buffer__)



if '__HasCompatibilityTweak__' in globals():
    sys.stdout = StdoutReader()
    print('# sys.stdout replaced! Enjoy #')
else:
    print('# In Non-legacy mode, log_read is not needed #')