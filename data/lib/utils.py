# downloaded from msgr-patches!

import datetime
import os.path
import time
from io import StringIO
from tkinter.messagebox import showerror as shw_error
from typing import TextIO
import sys
import data.lib.ru_to_en


class Config:
    """Other Version of Config"""
    def __init__(self, file, encoding='utf-8'):
        self._path = file
        self._enc = encoding
        if not os.path.exists(file):
            with open(file, 'w'):
                pass
        self._file = open(file, 'r', encoding=encoding)

    def _update(self, key, value):
        _data = self.get().copy()
        _data.update({key: value})
        self._commit(_data)

    def get(self):
        self._file.seek(0)
        _data = self._file.read()
        _decoded = {}
        for _item in _data.split('\n'):
            if is_str_not_empty(_item):
                _decoded.update({_item.split(':')[0]: _item.split(':')[1]})
        return _decoded

    def _commit(self, _data):
        _encoded = ''
        for key, val in _data.items():
            _encoded += f'{key}:{val}'
            _encoded += '\n'
        with open(self._path, 'w') as fl:
            fl.write(_encoded)
        self._file = open(self._path, 'r', encoding=self._enc)

    def __contains__(self, item):
        return item in self.get()

    def __getitem__(self, item):
        return self.get()[item]

    def __setitem__(self, key, value):
        self._update(key, value)


class Log:
    """For sys.stdout/err replace. Emulate sys.stdout/err, writes into console (if available) and in file"""
    def __init__(self, type_: str, file: TextIO=None, show_in_messagebox=False):
        self.type_ = type_
        self.file = file
        if file is not None:
            self.name = self.file.name
        else:
            self.name = ''
        self.last_v = ''
        self.buffer = StringIO()
        self.show_in_messagebox = show_in_messagebox

    def write(self, v):
        if self.show_in_messagebox:
            shw_error(f'{self.type_}', v)
            return
        if v not in ['', ' ', '\n', '<VirtualEvent event x=0 y=0>'] and v != self.last_v:
            repr_v = repr(v)[1:-1]
            if repr(v)[1:-1][len(repr_v) - 2:len(repr_v)] == r'\n':
                v = v[:len(v) - 1]
            if self.file is not None:
                try:
                    self.file.write(f'[{self.type_}]{data.lib.ru_to_en.replace_letters(v)}\n')
                except UnicodeError:
                    self.file.write(f'[{self.type_}][loader] log_file_unsupported_encoding\n')
            self.last_v = v
            self.file.flush()
            self.buffer.write(f'[{self.type_}]{v}\n')
        if v not in ['', ' ', '\n', '<VirtualEvent event x=0 y=0>']:
            try:
                sys.__stdout__.write(f'[{self.type_}]{v}\n')
            except AttributeError:
                pass

    def flush(self):
        if self.file is not None:
            self.file.flush()

    def read(self):
        return self.buffer.getvalue()


class TickSys:
    def __init__(self, tick_rate: int = 20):
        """Tick System for apps

        :param tick_rate - tick per second
        """
        self.tick_rate = tick_rate
        self.stop = False
        self.t = 0

    def start_tick(self):
        """Starts tick system. Need to run by threading.Thread"""
        while not self.stop:
            try:
                time.sleep(1 / self.tick_rate)
                self.t += 1
            except KeyboardInterrupt:
                break
            except Exception as _tick_thread_ex:
                print(_tick_thread_ex)
                return
        else:
            return


def is_subscriptable(obj):
    """Checks object on subscriptable"""
    if not isinstance(obj, str):
        return hasattr(obj, '__getitem__')
    else:
        return False


def is_str_not_empty(d):
    """Checks is str empty"""
    if d not in ['', ' ', '\n']:
        return True
    else:
        return False


def convert_path_to_module(_p):
    """Coverts ./path/to/file to path.to.module"""
    _r_p = _p
    _r_p = _r_p.replace('./', '')
    _r_p = _r_p.replace('/', '.')
    _r_p = _r_p.replace('.py', '').replace('.pyw', '')
    return _r_p


def today():
    """Today"""
    return str(datetime.date.today()).replace('-', '.')


def to_time(_t):
    """Converts seconds into normal time string"""
    hours = int(_t) // 3600
    minutes = int(_t) // 60 - hours * 60
    if minutes > 0 and hours > 0:
        return f'{hours}h {minutes}m'
    elif minutes == 0 and hours > 0:
        return f'{hours}h'
    elif minutes > 0 and hours == 0:
        return f'{minutes}m'
    else:
        return f'{_t}s'


def get_var_name(var_value, use_custom=False, **kwargs):
    """Gets var name from globals() / locals()
    :param var_value: value of variable
    :param use_custom: use custom dict to find var_name. need to give 'where' argument to kwargs"""
    where = globals()
    if use_custom:
        where = kwargs['where']
    vl = list(where.values())
    ks = list(where.keys())
    if var_value in vl:
        ind = vl.index(var_value)
    else:
        ind = -1
    if ind >= 0:
        return ks[ind]
    else:
        return 'not found'


def get_not_in_list_items(from_list, second):
    _a = []
    for i in second:
        if i not in from_list:
            _a.append(i)
    return _a
