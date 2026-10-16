# downloaded from msgr-patches!
# encoding: windows-1251

# Utils module. PLEASE DONT EDIT

from typing import TextIO
import traceback
from tkinter.messagebox import showinfo
import _tkinter
import sys
import tkinter
import os
import time

from data.lib.encrypting import *
from data.lib.types_adv import SupportRead

ui_module = None
app = None

def print_adv(v):
    print(f'[core.py]{v}')


class Config:
    """Config"""
    def __init__(self, title, coding=None):
        self.title = title
        try:
            open(title, 'r')
        except FileNotFoundError:
            with open(title, 'w'):
                pass
        self.config_w = open(title, 'a', encoding=coding)
        self.config_r = open(title, 'r', encoding=coding)
        self.dct = self._get_items()

    def write(self, key, value):
        self.config_w.write(f'{key}:{value}\n')
        self.config_w.close()
        self.config_w = open(self.title, 'a')

    def _get_items(self):
        self.config_r.seek(0)
        cnf = {}
        for elem in self.config_r.read().split('\n'):
            if len(elem.split(':')) == 2:
                cnf.update({elem.split(':')[0]: elem.split(':')[1]})
        return cnf

    def __getitem__(self, item):
        return self.dct[item]


class SConfig:
    """Config. Works Only With Strings"""
    def __init__(self, data):
        self.data = data
        self.dct = self._get_items()

    def _get_items(self):
        cnf = {}
        for elem in self.data.split('\n'):
            if len(elem.split(':')) == 2:
                cnf.update({elem.split(':')[0]: elem.split(':')[1]})
        return cnf

    def __getitem__(self, item):
        return self.dct[item]


class SNConfig:
    """NConfig. Works only with strings"""
    def __init__(self, fl: str):
        self.conf = fl

    def load(self):
        decoded = {}
        serializes = self.conf.split('Serialize:')

        for ser in serializes:
            lines = ser.split('\n')
            ser_name = lines[0]
            data = ''.join(lines[1::])
            data = dec_content_ord2(data)
            decoded[ser_name] = data

        decoded.pop('', None)

        return decoded

    @staticmethod
    def dump(conf):
        coded = ''
        for i in conf:
            coded += f'Serialize:{i}\n'
            coded += enc_content_ord2(conf[i]) + '\n'

        return coded


class JsonObject:
    """Empty file-like object. Correct type for json.dump/dumps"""
    def __init__(self, f: open):
        self.f = f

    def write(self, v):
        self.f.write(v)

    def read(self):
        return self.f.read()


class Locale:
    """Locale object, gets item from Config, if not found return 'UNK'"""
    def __init__(self, conf: Config | dict[str, str]):
        if isinstance(conf, Config):
            self.lc_dct = conf.dct
        else:
            self.lc_dct = conf
        self.conf = conf

    def __contains__(self, item):
        return item in self.lc_dct

    def __getitem__(self, item):
        if item in self.lc_dct:
            return self.lc_dct[item]
        else:
            return f'UNK:{item}'

    def get_key(self, item):
        if 'UNK:' in item:
            return item.split(':')[1]
        else:
            try:
                return list(self.lc_dct.keys())[list(self.lc_dct.values()).index(item)]
            except ValueError:
                return f'UNK:{item}'


def plugin_info():
    """Only For MSGR(QW)"""
    showinfo('BTAEML (BebraTech Application Engine Mod Loader)',
             "BTAEML (BebraTech Application Engine Mod Loader) coded by BebraTech Inc. (BTAE authors).\n"
             "ALL plugins/mods made by other people (not BebraTech Inc.)\n"
             "We aren't take responsibility if your PC damaged by plugins/mods.\n\n"
             "BTAEML is included in all BTAE version 2.8.9 and above.\n"
             "In other versions BTAEML work unstable.\n\n"
             "BTAEML Team (BebraTech subdivision) 2025")


def load_theme(theme_load: SupportRead | str):
    """Loads theme from special file"""
    theme = {}
    if isinstance(theme_load, str):
        temp = theme_load.split('\n')
    else:
        temp = theme_load.read().split('\n')
    for i in temp:
        try:
            if '=' in i:
                theme.update({i.split('=')[0]: i.split('=')[1]})
        except IndexError as _ex:
            _ex.add_note(f'Error decoding {i!r}')
            raise _ex
    try:
        def_bg = theme['main_color']
        def_fg = theme['secondary_color']
        def_font = theme['font'].split()
    except KeyError:
        try:
            def_bg = theme['main']
            def_fg = theme['fg']
            def_font = theme['font'].split()
        except KeyError:
            def_bg = '#111111'
            def_fg = '#ffffff'
            def_font = 'TkDefaultFont 12'
            print(f'[Theme loader] Loaded DCT {theme} doesnt have required keys: main_color/main, secondary_color/fg, font, DCT Loaded from {repr(temp)} (lines)')
    return def_bg, def_fg, def_font


def tk_wait(sec: int, win: tkinter.Tk):
    """Waits sec seconds & updates win"""
    _time = float(sec)
    while _time < sec:
        time.sleep(0.2)
        win.update()
        _time += 0.2


def get_win(exc_with_traceback='No-Information-Provided', program_title='No-Information-Provided'):
    """Crash Window"""
    print(f'[FatalTraceback] {exc_with_traceback}')
    try:
        rep = tkinter.Tk()
    except _tkinter.TclError:
            print_adv('[FATAL_ERROR] Invalid TCL configuration')
            print_adv(traceback.format_exc())
            return
    rep.title('Error')
    rep.resizable(False, False)
    tkinter.Label(rep, text=f'{program_title}\n\n\n'
                    f'{exc_with_traceback}', justify='left').pack()
    tkinter.Button(rep, text='Exit', command=sys.exit).pack(anchor='w')
    rep.mainloop()