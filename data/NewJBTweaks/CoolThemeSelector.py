#meta
# {"req": ["LibSettings"]}
import tkinter

import J
import Application
from LibSettings import SettingsAPI
import TweakAPI
from data.lib.ui import Popup

st = TweakAPI.GetTweakStorage()

if 'Theme' not in st:
    st['Theme'] = {}

th = st['Theme']
last_bg = th.get('bg', Application.default_bg)
last_fg = th.get('fg', Application.default_fg)


def tkinter_color_to_hex(color_name):
    root = Application.root
    # winfo_rgb returns a tuple of 16-bit RGB values (0-65535)
    try:
        r, g, b = root.winfo_rgb(color_name)
    except Exception as _ex:
        _ex.add_note(f'While converting {color_name!r}')
        raise _ex

    # Convert 16-bit to 8-bit (0-255)
    r8, g8, b8 = r >> 8, g >> 8, b >> 8

    # Format into a hex string
    hex_code = f"#{r8:02x}{g8:02x}{b8:02x}"
    return hex_code, (r8, g8, b8)


def hex_str_to_rgb(hex_str: str) -> tuple[int, int, int]:
    if not hex_str.startswith('#'):
        raise ValueError(f"Некорректный формат цвета: '{hex_str}'")

    code = hex_str[1:]

    if len(code) == 3:
        code = ''.join(c * 2 for c in code) + 'ff'

    r, g, b = int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16)

    return r, g, b


class _ColorChooser(tkinter.Frame):
    def __init__(self, master, on_change, text, start_value_func, **kw):
        super().__init__(master, **kw)
        self.on_change = on_change
        hx, rgb = tkinter_color_to_hex(start_value_func())
        self.r_var = tkinter.IntVar(value=rgb[0])
        self.g_var = tkinter.IntVar(value=rgb[1])
        self.b_var = tkinter.IntVar(value=rgb[2])
        self.hex_var = tkinter.StringVar(value=hx)

        tkinter.Label(self, text=text).pack()

        self.r = tkinter.Scale(self, from_=0, to=255, variable=self.r_var, orient='horizontal')
        self.g = tkinter.Scale(self, from_=0, to=255, variable=self.g_var, orient='horizontal')
        self.b = tkinter.Scale(self, from_=0, to=255, variable=self.b_var, orient='horizontal')

        self.hex = tkinter.Entry(self, textvariable=self.hex_var)

        self.r.pack()
        self.g.pack()
        self.b.pack()
        self.hex.pack()

        self.r_var.trace_add('write', self._upd)
        self.g_var.trace_add('write', self._upd)
        self.b_var.trace_add('write', self._upd)
        self.hex_var.trace_add('write', self._upd_hex)

        self.color = '#000000'
        self.hex_setting = False

    def _upd_hex(self, *_):
        try:
            r, g, b = hex_str_to_rgb(self.hex_var.get())
            tkinter_color_to_hex(self.hex_var.get())
            self.hex['fg'] = Application.default_fg
        except (ValueError, tkinter.TclError):
            self.hex['fg'] = 'red'
            return

        self.hex_setting = True
        self.r_var.set(r)
        self.g_var.set(g)
        self.b_var.set(b)
        self.hex_setting = False
        self.color = self.hex_var.get()
        self.on_change(self.color)

    def _upd(self, *_):
        if self.hex_setting:
            return
        r, g, b = self.r_var.get(), self.g_var.get(), self.b_var.get()
        self.color = f'#{r:02x}{g:02x}{b:02x}'
        self.hex_var.set(self.color)
        self.on_change(self.color)

def _set_colors(fg=None, bg=None):
    global last_bg, last_fg
    r = False
    if fg is not None:
        Application.default_fg = fg
        last_fg = fg
        r = True
    if bg is not None:
        Application.default_bg = bg
        last_bg = bg
        r = True
    if r:
        Application.commit_theme('#000000', '#000000')


def ask(cb):
    def complete():
        w = e.get()
        if w.strip():
            cb(w)
            pop.destroy()
    pop = Popup()
    pop.pack_propagate(True)
    pop.root_frame.pack_propagate(True)
    e = tkinter.Entry(pop)
    e.pack()
    tkinter.Button(pop, text='Commit', command=complete).pack()


def save_current(name):
    Application.nc_themes.dct[f'[{name}]'] = f'main={Application.default_bg}\nfg={Application.default_fg}\nfont={Application.font_theme[0]} {Application.font_theme[1]}'


SettingsAPI.create_page('CoolThemeSelector')
SettingsAPI.extent_wtypes('CTS_ColorChooser', _ColorChooser)
SettingsAPI.create_widget('CoolThemeSelector', 'CTS_ColorChooser', on_change=lambda clr: _set_colors(bg=clr),
                          text='Background', start_value_func=lambda: last_bg)
SettingsAPI.create_widget('CoolThemeSelector', 'CTS_ColorChooser', on_change=lambda clr: _set_colors(fg=clr),
                          text='Foreground', start_value_func=lambda: last_fg)
SettingsAPI.create_widget('CoolThemeSelector', 'Button', text='Save as...', command=lambda: ask(save_current))

@J.API.on_mainloop
def commit():
    return _set_colors(last_fg, last_bg)

last_th = ''

def _load_theme(file2, ret=False):
    global last_th
    last_th = file2
    if enabled:
        return commit()
    else:
        return th_original(file2, ret)

enabled = True

def toggle(*_):
    global enabled
    v = var.get()
    enabled = v
    if not enabled:
        th_original(last_th)
    else:
        commit()


th_original = Application.theme
Application.theme = _load_theme

var = tkinter.BooleanVar(value=True)
var.trace_add('write', toggle)

SettingsAPI.create_widget('CoolThemeSelector', 'Button', text='Update theme', command=commit)
SettingsAPI.create_widget('CoolThemeSelector', 'Checkbutton', text='Enabled', variable=var)


@J.API.on_exit
def save():
    st['Theme']['bg'] = last_bg
    st['Theme']['fg'] = last_fg
    TweakAPI.SaveTweakStorage()