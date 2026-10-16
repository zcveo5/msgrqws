# downloaded from msgr-patches!
import os
import random
import time
import traceback
from os import mkdir

import math
import os.path
import sys
from tkinter import TclError, Frame
import tkinter
from tkinter.messagebox import showerror
from typing import Literal, Union
import data.lib.ru_to_en

_ADVLOG = False # DO ADVLOG
_MODULE_LOG = False # DO ANY THIS MODULE LOGS

_windows = []
_widgets = {}
widgets = _widgets
app_root_window = None
root_scaling = 1.0

def lift_popups():
    for _w in _widgets['popups'].values():
        if isinstance(_w, Popup):
            try:
                _w.tkraise()
                _w.root_frame.lift()
            except TclError:
                pass


def update_win_scaling():
    for _win in _windows:
        try:
            _win.tk.call('tk', 'scaling', root_scaling)
        except TclError:
            pass


def _create_copy(wid, master):
    wid_class = wid.__class__
    new_widget = wid_class(master)
    for _cfg_elem in wid.keys():
        new_widget.config({_cfg_elem: wid[_cfg_elem]})
    return new_widget


def _pass():
    pass

class Widget:
    def __init__(self, mast, obj, name: str, **kw):
        self._root_win = mast
        self.tk = obj
        self._kwargs = kw
        self._name = name
        self._place_mode = 'NotPlaced'
        self.destroyed = False
        if 'widgets' not in _widgets:
            _widgets['widgets'] = {}
            _widgets['widgets'][self._name] = self
        else:
            _widgets['widgets'][self._name] = self

    def build(self, mode: Literal['place', 'grid', 'pack'], **kwargs):
        if mode == 'place':
            self.tk.place(**kwargs)
        elif mode == 'grid':
            self.tk.grid(**kwargs)
        elif mode == 'pack':
            self.tk.pack(**kwargs)
        self._place_mode = mode

    def forget(self):
        if self._place_mode == 'place':
            self.tk.place_forget()
        elif self._place_mode == 'grid':
            self.tk.grid_forget()
        elif self._place_mode == 'pack':
            self.tk.pack_forget()

    def destroy(self):
        if self.tk.winfo_exists():
            self.forget()
            self.tk.destroy()
            self.destroyed = True

    def configure(self, **kwargs):
        self.tk.configure(**kwargs)

    def __getitem__(self, item):
        return self.tk[item]

    def __setitem__(self, key, value):
        self.tk[key] = value


class ProgressBar(tkinter.Label):
    def __init__(self, len_to_count=100, **kwargs):
        super().__init__(**kwargs)
        self.percentage = 0
        self._ltc = len_to_count
        self._progress = "." * 100

        self['text'] = f'[{self._progress}] {self.percentage}/100'

    def plus(self, v=1):
        if self.percentage < 100:
            self.percentage += math.ceil(v * self._gen_percent())
            self._progress = '|' * self.percentage + '.' * (100 - self.percentage)
            try:
                if self.winfo_exists():
                    self['text'] = f'[{self._progress}] {self.percentage}/100'
            except TclError:
                pass
        else:
            self['text'] = f'[{self._progress}] Completed'
        self.update()

    def _gen_percent(self):
        return 100 / self._ltc



class Button(tkinter.Button):
    def __init__(self, master=None, command="", **kwargs):
        if command != "":
            command = self._wrap_command(command)
        super().__init__(
            master=master,
            command=command,
            **kwargs
        )

    def _wrap_command(self, cmd):
        def safe_command():
            try:
                cmd()
            except Exception as e:
                traceback.print_exception(e)
                showerror(f'{self}', ''.join(traceback.format_exception(e)))
        safe_command.__name__ = cmd.__name__
        return safe_command


class Label(tkinter.Label):
    def __init__(self, master=None, **kwargs):
        super().__init__(
            master=master,
            **kwargs)


class Text(tkinter.Text):
    def __init__(self, master=None, **kwargs):
        super().__init__(
            master=master,
            **kwargs)


class Entry(tkinter.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(
           master=master,
           **kwargs)


class Combobox:
    def __init__(self, master=app_root_window, bg=None, fg=None, font=None, values=None, _values=None, state='readonly',**kw):
        self.parent = master
        if _values is not None:
            values = _values
        if values is None:
            values = []
        self.values = values
        self.var = tkinter.StringVar()
        self.bg = bg
        self.fg = fg
        self.font = font

        self._root_frame = Frame(master, **kw)
        self._root_frame.pack_propagate(True)

        self.entry = tkinter.Entry(self._root_frame, textvariable=self.var, state=state)
        self.entry.grid(row=0, column=0)
        self.btn = tkinter.Button(self._root_frame, text="▼", command=self.toggle_listbox)
        self.btn.grid(row=0, column=1)
        self.listbox = tkinter.Listbox(self._root_frame, bg="white")

        if bg is not None:
            self._root_frame.configure(bg=bg)
            self.entry.configure(bg=bg)
            self.btn.configure(bg=bg)
            self.listbox.configure(bg=bg)
        if fg is not None:
            self.entry.configure(fg=fg)
            self.btn.configure(fg=fg)
            self.listbox.configure(fg=fg)
        if font is not None:
            self.entry.configure(font=font)
            self.btn.configure(font=font)
            self.listbox.configure(font=font)

        for value in values:
            self.listbox.insert('end', value)

        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.entry.bind("<KeyRelease>", self.filter_values)
        self.entry.bind("<Down>", lambda e: self.show_listbox())

    def build(self, mode: Literal['place', 'pack', 'grid'], **kw):
        if mode == 'place':
            self._root_frame.place(**kw)
        elif mode == 'pack':
            self._root_frame.pack(**kw)
        else:
            self._root_frame.grid(**kw)

    def toggle_listbox(self):
        if self.listbox.winfo_ismapped():
            self.hide_listbox()
        else:
            self.show_listbox()

    def show_listbox(self):
        self.listbox.grid(column=0, row=1, columnspan=2, sticky='nsew')
        #self._root_frame.configure(height=self._root_frame.winfo_height() + self.listbox.winfo_height())
        self.listbox.lift()
        self.listbox.focus_set()

    def hide_listbox(self):
        self.listbox.grid_forget()
        self.entry.focus_set()

    def on_select(self, event):
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            value = self.listbox.get(index)
            self.var.set(value)
        self.hide_listbox()

    def filter_values(self, event):
        pattern = self.var.get().lower()
        self.listbox.delete(0, 'end')
        for value in self.values:
            if pattern in value.lower():
                self.listbox.insert('end', value)

    def get(self):
        return self.var.get()

    def bind(self, _p, _a):
        if _p == '<<ComboboxSelected>>':
            def wrapper(event):
                self.on_select(event)
                _a(event)
            self.listbox.bind('<<ListboxSelect>>', wrapper)

    def pack(self, **kw):
        self.build('pack', **kw)


POSSIBLE_WIDGETS = [Label, Button, Text, Entry, ProgressBar]
POSSIBLE_WIDGETS_TK = [tkinter.Label, tkinter.Button, tkinter.Text, tkinter.Entry]


class _MiscSupportFrame(tkinter.Misc):
    """Fix of highlight not work on windows. Make highlight just border"""
    orig_color = '#FFFFFF'
    orig_thinness = 0
    root_master = None

    def commit(self, widget_cfg: dict):
        self.root_master = app_root_window
        self.orig_thinness = self['highlightthickness']
        if self.orig_thinness > 0:
            if 'highlightthickness' in widget_cfg:
                self.orig_thinness = widget_cfg['highlightthickness']

            self.orig_color = self['highlightcolor']
            if 'highlightcolor' in widget_cfg:
                color = widget_cfg['highlightcolor']
            else:
                color = self.root_master.option_get('foreground', '')
                if color == '':
                    color = self.root_master.option_get('*Foreground', '')

            self.force_set_color(color)
            if self.orig_color in ['SystemWindowFrame', '']:
                self.force_set_color(color)
            self.root_master.after(1, lambda: self.force_set_color(self.orig_color))

    def force_set_color(self, color):
        self.orig_color = color
        if self.orig_color != '':
            if self.winfo_exists():
                self.update_frame()

    def update_frame(self):
        if self.orig_color != '':
            self.configure(highlightcolor=self.orig_color,
                           highlightthickness=self.orig_thinness,
                           highlightbackground=self.orig_color)


class Frame(tkinter.Frame, _MiscSupportFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _MiscSupportFrame.commit(self, kwargs)


class Listbox(tkinter.Listbox, _MiscSupportFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(
           master=master,
           **kwargs)
        self._scrolled = 0
        self._data = []
        self.bind('<<MouseWheel>>', self._scroll_hook)
        _MiscSupportFrame.commit(self, kwargs)

    def _scroll_hook(self, event):
        if 0 < self._scrolled < len(self.get('0', 'end').split('\n')):
            self._scrolled + event.delta // 120

    def update(self):
        super().delete('0', 'end')
        for _elem in self._data:
            super().insert("end", _elem)
        super().update()

    def insert(self, index: int | Literal['end'], *elements):
        if index == 'end':
            for _elem in elements:
                self._data.append(_elem)
        elif isinstance(index, int):
            for _elem in elements:
                self._data.insert(index, _elem)
        self.update()

    def delete(self, first: int, last: int | Literal['end'] | None = None):
        if last is int or last == 'end':
            if last == 'end':
                last = len(self._data)
            for _ in range(first, last):
                self._data.pop(first)
        else:
            self._data.pop(first)
        self.update()


class Win(tkinter.Tk):
    """Advanced Tk Widget"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.his = {}
        self._registered_widgets = []
        self.his_being = {}
        self.widgets_name = []
        self.recovery_widgets = []
        self._work_threads = True
        self.bind('<Control-s>', self.recovery)
        self.on_exit_action = None
        self._thread_names = []
        self.option_save = {}
        self._thread_datas = {}
        _windows.append(self)
        if app_root_window is None:
            self.force_main()


    def recovery(self, event=None):
        """Recovery menu"""
        rec_pop = Popup(self)
        for i in self.recovery_widgets:
            if callable(i):
                i()
            else:
                rec_pop.create(i['name'], i['obj'], recreate_if_exists=True, **i['kwargs']).build(i['place_mode'], **i['place_kw'])


    def geometry(self, size=None, pos=None):
        """Sets / gets window's geometry & pos"""
        if size is None:
            size = []
        if pos is None:
            pos = []
        if size:
            super().geometry(f'{size[0]}x{size[1]}')
        if pos:
            super().geometry(f'{super().geometry().split("+")[0]}+{pos[0]}+{pos[1]}')
        if not size and not pos:
            return super().geometry()
        return None

    def create(self, name: str, obj, recreate_if_exists=False, **kwargs) -> Widget:
        """Creates widgets, then returns created"""
        if name in self.his:
            if not recreate_if_exists:
                print(f'{name} is already created')
            else:
                self.his[name].destroy()
                self.his.pop(name)
        if not callable(obj):
            raise TypeError(f"Widget {obj} can't be not callable")
        create_kw = kwargs
        self.his[name] = Widget(self, obj(**create_kw), name=name)
        self._registered_widgets.append(self.his[name].tk)
        self.his_being.update({name: self.his[name]})
        self.widgets_name.append(name)
        for k, v in self.option_save.items():
            try:
                self.his[name].configure(**{k: v})
            except TclError:
                pass
        return self.his[name]

    def being_ping(self):
        ans = {}
        for name in self.his_being:
            ans.update({name: self.his_being[name].tk.winfo_exists()})
        return ans

    def create_abstract(self, name: str, obj):
        self.his.update({name: obj})

    def destroy_all_in(self, dont_create_help=False):
        for name in list(self.his.keys()):
            self.his[name].destroy()
        for n in self.winfo_children():
            n.place_forget()
            n.pack_forget()
            n.grid_forget()
        self.config(bg=Button()['bg'])
        self.his = {}
        self.update()

    def update(self):
        super().update()

    def __getitem__(self, item):
        return self.his[item]

    def tk_thread(self, target, sleep_time, /, *args):
        """'thread' created by main.after
        :param target: target function
        :param sleep_time: time before calling target again
        :param args: *args for target

        to stop call Win().stop_threads()"""

        if sleep_time < 500:
            sleep_time = sleep_time

        self._thread_datas[target] = {'name': target.__name__, 'work': True}
        self._thread_names.append(target)

        def wrapper(*_args):
            _ret = target(*_args)
            if _ret != -1 and self._work_threads and self._thread_datas[target]['work']:
                self.after(sleep_time, wrapper, *args)
            else:
                self._thread_datas.pop(target)
                self._thread_names.remove(target)
        wrapper(*args)

    def get_threads(self):
        return self._thread_names.copy()

    def stop_thread(self, name):
        self._thread_datas[name]['work'] = False

    def stop_threads(self):
        self._work_threads = False
        def wrp():
            if not self._thread_names:
                self._work_threads = True
            else:
                self.after(100, wrp)
        wrp()

    def force_main(self):
        """Forces window to be root (ui.app_root_window)"""
        global app_root_window
        app_root_window = self

    def option_add(
        self, pattern, value, priority = None
    ):
        if pattern[0] != '*':
            pattern = f'*{pattern}'
        self.option_save[pattern[1::].lower()] = value
        if pattern.lower() == '*background':
            self['bg'] = value
        super().option_add(pattern, value, priority)

    def option_get(self, name, className=''):
        if className == '' and name in self.option_save:
            return self.option_save[name]
        else:
            return super().option_get(name, className)


app_root_window: Win


class NoFrameWin(Win):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)

        self.root_frame = Frame(self, highlightthickness=2)
        self.root_frame.pack(fill='both', expand=True)

        self.title_bar = Frame(self.root_frame, highlightthickness=2)
        self.title_bar.pack(fill='x', anchor='n')
        self._title_lbl = Label(self.title_bar, text='OverrideRedirectWin')
        self._title_lbl.pack(anchor='w', fill='y', side='left')
        self._close_btn = Button(self.title_bar, text='X', command=self.destroy)
        self._close_btn.pack(fill='y', anchor='e', side='right')
        self._iconify_btn = Button(self.title_bar, text='-', command=self.iconify)
        self._iconify_btn.pack(fill='y', anchor='e', side='right')
        self.container = Frame(self.root_frame)
        self.container.pack(fill='both', expand=True)
        self.wm_minsize(400, 400)
        self._title_lbl.bind('<Button-1>', self._start_move)
        self._title_lbl.bind('<B1-Motion>', self._move)
        self.title_bar.bind('<Button-1>', self._start_move)
        self.title_bar.bind('<B1-Motion>', self._move)

        def lift_t_bar():
            self.title_bar.pack(fill='x', anchor='n')
            self.title_bar.lift()

        self.recovery_widgets.append(lift_t_bar)

        for i in ['destroy', 'pack_forget']:
            setattr(self.title_bar, i, lambda: print('t_bar bypass'))
            setattr(self._title_lbl, i, lambda: print('t_lbl bypass'))
            setattr(self._iconify_btn, i, lambda: print('ic_btn bypass'))
            setattr(self._close_btn, i, lambda: print('cl_btn bypass'))



        #self.set_default_theme(highlightcolor='#f0f0f0', bg='black', fg='white')

        self._do_loop = True
        self.tk_thread(self._state_loop, 100)


    def _state_loop(self):
        self.title_bar.lift()
        if self._do_loop:
            if self.state() == 'normal' and not self.overrideredirect() and self.focus_get() is not None:
                self.overrideredirect(True)
            elif self.state() == 'normal' and self.focus_get() is None:
                self.overrideredirect(False)

    def bind(
        self,
        sequence = None,
        func = None,
        add = None,
    ):
        super().bind(sequence, func, add)

    def iconify(self):
        if self.state() != 'iconic':
            self._do_loop = False
            self.overrideredirect(False)
            self.update()
            try:
                self.wm_iconify()
            except TclError:
                pass
            self._do_loop = True

    def title(self, t=None):
        if t is not None:
            self._title_lbl['text'] = t
            super().title(t)
            return None
        else:
            return self._title_lbl['text']

    def _start_move(self, event=None):
        if hasattr(event, 'x') and hasattr(event, 'y'):
            self._start_x = event.x
            self._start_y = event.y

    def _move(self, event):
        x = self.winfo_rootx() + (event.x - self._start_x)
        y = self.winfo_rooty() + (event.y - self._start_y)
        self.pos_configure(x, y)

    def set_default_theme(self, to='all', **kwargs):
        super().set_default_theme(to, **kwargs)
        self.root_frame.force_set_color(self.option_get('foreground', ''))

    def destroy_children(self, mode='destroy'):
        for i in self.container.winfo_children():
            if mode == 'destroy':
                i.destroy()
            elif mode == 'forget':
                i.pack_forget()
                i.place_forget()
                i.grid_forget()

    def destroy_all_in(self, do_not_create_help=True):
        self.destroy_children('forget')

    def winfo_children(self):
        return self.container.winfo_children()


class SidePanelWidget:
    def __init__(self, win: Union[Win, tkinter.Tk], style=None, _side: Literal['R', 'L'] = 'R', title: str = 'Side Panel'):
        self.his = {}
        self._title = title
        if isinstance(win, Win):
            self._win = win
        else:
            self._win = win
        self._side = _side
        self._o = None
        self._widgets = []
        if style is None:
            self._style = ['SystemButtonFace', 'SystemButtonText', 'TkDefaultFont']
        else:
            self._style = style
        self._font = tuple(self._style[2].split(':'))
        if len(self._font) == 1:
            self._font = (self._style[2])

    def build(self):
        size = self._win.geometry().split('+')[0].split('x')
        size_x = int(size[0])
        size_y = int(size[1])
        pos_x = 0
        if self._side == 'L':
            pos_x = size_x - size_x // 3
        if not isinstance(self._win, Win):
            self._o = tkinter.Canvas(self._win, bg=self._style[0], height=size_y, width=size_x // 3)
        else:
            self._o = self._win.create(f'side-panel-_o-root${self._title}$', tkinter.Canvas, bg=self._style[0], height=size_y, width=size_x // 3).tk
        self._o.place(x=pos_x, y=0)

        close_btn = tkinter.Button(self._o, text='X', command=self.destroy, bg=self._style[0], fg=self._style[1], font=self._font)
        self._o.create_window(10, 15, window=close_btn)

        title_label = tkinter.Label(self._o, text=self._title, bg=self._style[0], fg=self._style[1], font=self._font)
        self._o.create_window(25, 15, window=title_label, anchor='w')

        self._custom_create()
        self.his.update({'_O': self._o})

    def create(self, widget, x, y, name: str = '',  **kw):
        if self._o is None and {'widget': widget, 'x': x, 'y': y, 'name': name, 'kw': kw} not in self._widgets:
            self._widgets.append({'widget': widget, 'x': x, 'y': y, 'name': name, 'kw': kw})
            return None
        else:
            if name != '':
                self.his.update({name: {'widget': widget, 'x': x, 'y': y, 'kw': kw}})
            if not isinstance(widget, int):
                if widget.winfo_exists() and widget.winfo_parent():
                    new_widget = self._create_widget_copy(widget)
                    item = self._o.create_window(x, y, window=new_widget, **kw) # If it fails, you forget to call build
                else:
                    widget.configure(bg=self._style[0], fg=self._style[1], font=self._font)
                    item = self._o.create_window(x, y, window=widget, **kw)
                self._o.tag_raise(item)
            else:
                item = widget
            return item

    def _custom_create(self):
        for widget_info in self._widgets:
            if list(widget_info.keys()) != ['widget']:
                self.create(widget_info['widget'], widget_info['x'], widget_info['y'], widget_info['name'],
                        **widget_info['kw'])

    def destroy(self):
        for item in self._widgets:
            try:
                if isinstance(item['widget'], tkinter.Widget):
                    item['widget'].destroy()
            except TclError:
                pass
        self._widgets.clear()
        try:
            if isinstance(self._win, Win):
                try:
                    self._win.his.pop(f'side-panel-_o-root${self._title}$')
                except KeyError:
                    pass
            if self._o:
                self._o.destroy()
        except AttributeError:
            pass
        self._o = None

    def _create_widget_copy(self, original):
        widget_class = original.__class__
        config = original.configure()

        new_widget = widget_class(self._o)

        for key in config:
            if key not in ['class', 'master']:
                new_widget[key] = original[key]

        if 'command' in original.keys():
            new_widget.config(command=original['command'])
        try:
            new_widget.config(bg=self._style[0], fg=self._style[1], font=self._font)
        except TclError:
            pass

        return new_widget


class SidePanel(SidePanelWidget):
    def __init__(self, win: Union[Win, tkinter.Tk], style=None, _side: Literal['R', 'L'] = 'R', title: str = 'Side Panel'):
        super().__init__(win, style, _side, title)
        self.custom_widgets = []

    def create_custom_widget(self, widget, x: int, y: int, name: str = '', **kw):
        self.custom_widgets.append({'widget': widget, 'x': x, 'y': y, 'name': name, 'kw': kw})

    def build(self):
        for i in self.custom_widgets:
            self.create(i['widget'], i['x'], i['y'], i['name'], **i['kw'])
        super().build()


class Empty(object):
    pass


class Popup(Frame):
    def __init__(self, master: Win | tkinter.Tk = app_root_window, x: int = -1, y: int = -1, size=None,
                 style=None, title: str = 'Popup', map_on_init=True):
        #if master is None:
        #    raise TypeError(f'Master win is not provided: {app_root_window}')
        if size is None:
            size = [300, 300]
        if master is None:
            master = app_root_window
        if x == -1:
            x = (master.winfo_width() // 2)
        if y == -1:
            y = (master.winfo_height() // 2)
        self.style = style
        self.size = size

        self.root_frame = Frame(master, width=size[0], height=size[1], highlightthickness=2)
        #self.root_frame.pack_propagate(False)

        self.close_btn = Button(self.root_frame, text='X', command=self.root_frame.place_forget)
        self.close_btn.pack(anchor='ne')
        self.title_lbl = Label(self.root_frame, text=title)
        self.title_lbl.place(x=0, y=0)

        super().__init__(self.root_frame, width=size[0], height=size[1], highlightthickness=2)
        self.pack_propagate(False)


        if style is not None:
            self.configure(bg=style[0], highlightcolor=style[1])
            self.root_frame.configure(bg=style[0], highlightcolor=style[1])
            self.close_btn.configure(bg=style[0], fg=style[1], font=style[2])
            self.title_lbl.configure(bg=style[0], fg=style[1], font=style[2])

        self.root_frame.bind('<Button-1>', self._start_move)
        self.root_frame.bind('<B1-Motion>', self._move)
        self.title_lbl.bind('<Button-1>', self._start_move)
        self.title_lbl.bind('<B1-Motion>', self._move)

        self._start_x = 0
        self._start_y = 0
        if 'popups' in _widgets:
            _widgets['popups'][self.title_lbl['text']] = self
        else:
            _widgets['popups'] = {}
            _widgets['popups'][self.title_lbl['text']] = self
        if map_on_init:
            self.root_frame.place(x=0, y=0)
            self.pack()

    def destroy(self):
        self.root_frame.place_forget()

    def destroy_all_in(self):
        for i in self.winfo_children():
            i.destroy()

    def update_idletasks(self):
        super().update_idletasks()
        self.root_frame.update_idletasks()
        self.size = [self.root_frame.winfo_width(), self.root_frame.winfo_height()]


    def lift(self):
        self.root_frame.lift()

    def _start_move(self, event=None):
        self.root_frame.lift()
        if hasattr(event, 'x') and hasattr(event, 'y'):
            self._start_x = event.x
            self._start_y = event.y

    def _move(self, event):
        x = self.root_frame.winfo_x() + (event.x - self._start_x)
        y = self.root_frame.winfo_y() + (event.y - self._start_y)
        #self.title_lbl['text'] = f'{self.root_frame.winfo_x()}/{self.root_frame.master.winfo_width() - self.root_frame.winfo_width()} {self.root_frame.winfo_y()}/{self.root_frame.master.winfo_height() - self.root_frame.winfo_height()}'
        if 0 <= x <= self.root_frame.master.winfo_width() - self.root_frame.winfo_width():
            self.root_frame.place(x=x)
        if 0 <= y <= self.root_frame.master.winfo_height() - self.root_frame.winfo_height():
            self.root_frame.place(y=y)

    def update_info(self):
        self._start_x = 0
        self._start_y = 0
        self.update_idletasks()

    def resizable(self, x, y):
        if x or y:
            self.pack_propagate(True)
        else:
            self.pack_propagate(True)

    def title(self, t=None):
        if t is None:
            return self.title_lbl['text']
        self.title_lbl['text'] = t
        return None

    def protocol(self, prot, callback):
        if prot == 'WM_DELETE_WINDOW':
            self.close_btn['command'] = callback

    def create(self, name: str, obj, recreate_if_exists=False, **kwargs) -> Widget:
        """Creates widgets, then returns created"""
        if not callable(obj):
            raise TypeError(f"Widget {obj} can't be not callable")
        create_kw = kwargs
        wid = Widget(self, obj(self, **create_kw), name=name)
        return wid


class FullScreenPopup(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        Button(self, text='X', command=self.destroy).pack(anchor='ne')
        self.title_lbl = Label(self, text='')
        self.title_lbl.place(x=0, y=0)
        self.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.lift()

    def title(self, t=None):
        if t is None:
            return ''
        else:
            self.title_lbl['text'] = t
            return None


class SidePanelRevision(Popup):
    """Revision of SidePanel, using Popup class"""
    def __init__(self, master: Win = app_root_window, style=None, title: str = 'SidePanelRevision'):
        super().__init__(master, style=style, title=title, map_on_init=False)
        self.close_btn['command'] = self.root_frame.place_forget
        self._o = self
        self.pack(fill='both', expand=True)

    def build(self):
        self.root_frame.place(x=0, y=0, relheight=1.0, relwidth=0.25)
        self.pack_propagate(True)
        self.pack()
        self.root_frame.lift()

    def lift(self):
        self.root_frame.lift()
        self.root_frame.focus_set()
        self.root_frame.focus_force()

    #def _move(self, event):
    #    ...


class Beta:
    """Contains unfinished and broken things"""
    pass

if __name__ == '__main__':
    app = Win()
    side = SidePanel(app)
    app.create('_T_Button1', Button, text='123').build('pack')
    app.create('_T_Label1', Label, text='123').build('pack')
    app.create('_T_Entry1', Entry).build('pack')
    app.create('_T_Button2-side', Button, text='side', command=side.build).build('pack')
    side.create_custom_widget(Button(text='123'), 50, 50)
    app.create('_T_Button3', Button, text='destroy all w', command=app.destroy_all_in).build('pack')
    app.mainloop()