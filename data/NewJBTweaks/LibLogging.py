# METADATA
# {"reprint": false}
import logging
import sys

import J
import Application


color_types = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'd-gray': '\033[90m',
    'white': '\033[37m',
}

def get_logger(name=__name__, stream=None):
    class AnsiColorFormatter(logging.Formatter):
        RESET_CODE = '\033[0m'

        def __init__(self, fmt=None, date_fmt=None, colors=None):
            if colors is None:
                colors = {
                    'DEBUG': color_types['d-gray'],
                    'INFO': color_types['blue'],
                    'WARNING': color_types['yellow'],
                    'ERROR': color_types['red'],
                    'CRITICAL': color_types['red']}
            self.COLOR_CODES = colors
            super().__init__(fmt=fmt, datefmt=date_fmt)

        def format(self, record: logging.LogRecord) -> str:
            try:
                _info = super().format(record).replace(record.getMessage(), '')
            except TypeError:
                return ''
            # for k in dir(record):
            #    if not k.startswith('_'):
            #        print(f'{k}: {getattr(record, k)} | {'Not callable' if not callable(getattr(record, k)) else getattr(record, k)()}')
            color_start = self.COLOR_CODES.get(record.levelname, self.RESET_CODE)
            msg = record.getMessage().split(': ')
            if len(msg) > 1:
                formatted = f'[{msg[0]}{" " * (30 - len(msg[0]))}] {': '.join(msg[1::])}'
            else:
                formatted = f'[Base{" " * 56 }] {': '.join(msg[0::])}'
            to_return = f"{color_start}{_info}{formatted}{self.RESET_CODE}"
            return to_return
    _logger = logging.getLogger(name)
    _logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream=stream)
    handler.setLevel(logging.DEBUG)
    formatter = AnsiColorFormatter(

        '[%(levelname)-8s : %(asctime)s] %(message)s',
        date_fmt='%H:%M:%S'
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger


logger = get_logger('main')

def print_adv_logger(*s, sep=' ', file=None, end='', flush=False):
    to_print = ''
    for i in s:
        to_print += f'{i}{sep}'
    to_print = to_print[:-len(sep)]

    if isinstance(end, str):
        if end.startswith('##'):
            logger.log(int(end[2::]) * 10, to_print)
            return

    if '[info]' in to_print:
        logger.info(to_print)
    elif '[warning]' in to_print or '[warn]' in to_print:
        logger.warning(to_print)
    elif '[error]' in to_print or '[err]' in to_print or 'Exception' in to_print or '[er]' in to_print:
        logger.error(to_print)
    else:
        logger.debug(to_print)


def printer(name):
    def _ppr(*s):
        print_adv_logger(f'[{name}]: {' '.join([f'{i}' for i in s])}')
    return _ppr


@J.API.on_init
def replace_created():
    Application.pprint = printer('')
    Application.print = printer('')