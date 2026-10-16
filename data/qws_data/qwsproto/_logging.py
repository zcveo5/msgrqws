import logging
import sys
import threading

color_types = {
    'black': '\033[30m',
    'red': '\033[91m',
    'green': '\033[32m',
    'yellow': '\033[93m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'd-gray': '\033[90m',
    'white': '\033[37m',
    'b-red': '\033[91;1m'
}
logs = {'debug': [], 'info': [], 'warning': [], 'error': [], 'critical': []}


def get_logs(k='all'):
    if k != 'all':
        return logs[k]
    else:
        return logs


class AnsiColorFormatter(logging.Formatter):
    RESET_CODE = '\033[0m'

    def __init__(self, fmt=None, date_fmt=None, colors=None, stl='loggername#20, threadname#30, level#8, msgsub#30'):
        _colors = {
            'DEBUG': color_types['d-gray'],
            'INFO': color_types['blue'],
            'WARNING': color_types['yellow'],
            'ERROR': color_types['red'],
            'CRITICAL': color_types['b-red']}
        if colors is not None:
            for k, v in colors.items():
                v: str
                _colors[k.upper()] = color_types[v] if not v.startswith('$$') else v[2::]
        self.COLOR_CODES = _colors
        self.stl = stl
        super().__init__(fmt=fmt, datefmt=date_fmt)

    def format(self, record: logging.LogRecord) -> str:
        def w_space(o, maximum):
            return o + " " * (maximum - len(o))

        try:
            _info = super().format(record).replace(record.getMessage(), '')
        except TypeError:
            return ''

        module_name = record.name
        th_name = threading.current_thread().name

        msg = record.getMessage().split(': ')
        if len(msg) > 1 and len(msg[0]) < 20:
            msg_sub = f'{msg[0]}'
            msg_total = f'{': '.join(msg[1::])}'
        else:
            msg_sub = f'Base'
            msg_total = f'{': '.join(msg[0::])}'

        inf_things = {
            'loggername': module_name,
            'threadname': th_name,
            'level': record.levelname,
            'msgsub': msg_sub
        }

        _info = ''

        for inf_name in self.stl.split(', '):
            name, w_sp = inf_name.split('#')
            w_sp = int(w_sp)

            _info += f'{w_space(inf_things[name], w_sp)} : '


        color_start = self.COLOR_CODES.get(record.levelname, self.RESET_CODE)
        logs[record.levelname.lower()].append(record.getMessage())

        to_return = f"{color_start}[ {_info[:-2]} ] {msg_total}{self.RESET_CODE}"
        return to_return


def get_logger(name=__name__, stream=None, show_full_name=False, **formatter_kw):
    if not show_full_name:
        name = name.split('.')[-1]
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if stream is None:
         stream = sys.stdout
    handler = logging.StreamHandler(stream=stream)
    handler.setLevel(logging.DEBUG)
    formatter = AnsiColorFormatter(
        '%(message)s',
        date_fmt='%H:%M:%S',
        **formatter_kw
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
