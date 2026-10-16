import json
from typing import TextIO
from data.lib.types_adv import SupportWrite
from data.lib.ui import *


class Json:
    def __init__(self, fl: TextIO, fl_writeable: SupportWrite | None = None):
        self._fl = fl
        self._wrt = fl_writeable
        self._data = self._load()

    def _load(self):
        self._fl.seek(0)
        return json.load(self._fl)

    def _dump(self):
        if self._wrt is not None:
            json.dump(self._data, self._wrt)

    def __setitem__(self, key, value):
        self._data[key] = value
        self._dump()

    def __getitem__(self, item):
        return self._data[item]


def load_file():



root = Win()
root.title('Json Editor')
root.option_add('*Background', 'grey16')
root.option_add('*Foreground', 'white')
root.option_add('*Font', ('Consolas', 10))



root.mainloop()