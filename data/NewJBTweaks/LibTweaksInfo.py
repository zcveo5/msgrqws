import pathlib
import random
import sys
import threading
import J

LOGGERS: 'list[Log]' = []
_dump_logs = '--lti-dump-logs' in sys.argv

DUMP_DIR = pathlib.Path(__file__).absolute().parent / 'LTI_Dump'

class Event:
    def __init__(self):
        self._c = {}

    def __call__(self, fnc):
        _id = random.randint(0, 0xffff)
        self._c[_id] = fnc
        return _id

    def fire(self, *args):
        [i(*args) for i in self._c]

    def rm(self, _id):
        self._c.pop(_id)


class Log:
    def __init__(self, name):
        self.name = name
        LOGGERS.append(self)

        self.content = ''
        self._lock = threading.Lock()
        self.on_content = Event()

    def _log(self, s):
        with self._lock:
            self.content += s
            self.on_content.fire()

    def __call__(self, s, end='\n'):
        self._log(s + end)


def dump_logs():
    global _dump_logs
    _dump_logs = True


@J.API.on_exit
def _dump():
    if _dump_logs:
        print(f'Saving logs in {DUMP_DIR}')
        DUMP_DIR.mkdir(exist_ok=True)
        for i in LOGGERS:
            fp = DUMP_DIR / f'{i.name}.log'
            fp.touch()
            fp.write_text(f'LTI_Logger {i.name}\n' + i.content)
        print('Saved')

