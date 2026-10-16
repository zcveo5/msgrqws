# METADATA
# {"req": ["LibTweaksInfo"]}
import os.path
import tkinter
import traceback
from typing import Callable

import Application
import J
import LibTweaksInfo


adv = LibTweaksInfo.Log('LibSettings-StsCreateStacks')
w_errors = LibTweaksInfo.Log('LibSettings-WidgetErrors')


class SettsElement:
    def __init__(self, wtype, semeta, secreate=None, **kwargs):
        self.w = wtype
        self.kw = kwargs
        self.semeta = semeta
        self.secreate = secreate

    def copy(self):
        return SettsElement(self.w, self.semeta, self.secreate, **self.kw.copy())

    def __repr__(self):
        return f'<SettingsElement {self.w!r} {self.semeta!r}>'


BASIC_BUTTONS: list[SettsElement] = []
SETTS_DATA: dict[str, list[SettsElement]] = {}
BASE_WIDGET_HOOKS: dict[int, Callable[[SettsElement], SettsElement]] = {}
WTYPES = {}

_safe_mode = False


def wrap_class(cls):
    def wrapper(*args, **kwargs):
        try:
            return cls(*args, **kwargs)
        except Exception as _ex:
            _ex.add_note(f'Failed to create instance of {cls.__name__}\n'
                         f'Args: {', '.join([f'{i.__class__.__name__}: {i}' for i in args])}\n'
                         f'Kwargs: {', '.join([f'{k}: {v.__class__.__name__} - {v}' for k, v in kwargs.items()])}\n')
            raise _ex
    return wrapper


@wrap_class
class SafeLabel(tkinter.Label):
    pass


class SettsRewrite(Application.Settings):
    def __init__(self):
        adv(f'====StsCreated=====\n{''.join(traceback.format_stack())}\n=====')
        super().__init__()
        self._basic_buttons = []
        self._bb = []
        for idx, w in enumerate(self._base_widgets.copy()):
            w: tkinter.Button
            wdg = SettsElement(
                w.__class__.__name__,
                f'BBRecreated-{idx}',
                text=w['text'],
                command=w.cget('command')
            )
            self._bb.append(wdg.copy())

            if idx in BASE_WIDGET_HOOKS:
                wdg_o = BASE_WIDGET_HOOKS[idx](wdg)
                print(f'OVERRIDE bb {wdg} -> {wdg_o}')
                wdg = wdg_o
            else:
                print(f'Created bb {wdg}')

            if wdg is not None:
                self._basic_buttons.append(wdg)

        self._basic_buttons += BASIC_BUTTONS
        self._basic_buttons.append(SettsElement('Label', 'SapiJBTitle', text='LibSettings By timixees :3'))

        self._base_widgets.clear()

        self.debug = True

        self._settings_data = SETTS_DATA
        self._current_page = ''
        self._path = []
        self._offset = 0
        self.bind('<MouseWheel>', self._set_offset)
        self._ch = 0

    def _set_offset(self, e):
        d = -(e.delta / abs(e.delta))
        d *= 3
        if self._ch >= self._offset + int(d) >= 0:
            self._offset += int(d)
            if self.root_frame.winfo_ismapped():
                self.build()

    def _set_page(self, name):
        if name == '..':
            self._path.pop(len(self._path) - 1)
            try:
                self._current_page = self._path[-1]
            except IndexError:
                self._current_page = ''
        else:
            self._path.append(name)
            self._current_page = name
        self.build()

    def to_page(self, name):
        return lambda n=name: self._set_page(n)

    def _create_base_actual(self, sm=False):
        for _w in self.winfo_children():
            if _w.winfo_name().startswith('setts-runtime-'):
                _w.destroy()
        if _safe_mode or sm:
            for idx, i in enumerate(self._bb):
                wdg = getattr(tkinter, i.w, None)
                ready = wdg(master=self, name=f'setts-runtime-{idx}-sm', **i.kw)
                ready.pack()
            print('SAPI safe mode')
            return
        for i in self._base_widgets:
            i.pack_forget()

        NF = SettsElement('Label', 'SAPI-INTERNAL NFP', text=f'Not found page {self._current_page!r}')
        BACK = SettsElement('Button', 'SAPI-INTERNAL BACK', text='Back', command=self.to_page('..'))

        y = 0

        if self._current_page == '':
            to_render = self._basic_buttons
        else:
            to_render = [BACK] + self._settings_data.get(self._current_page, [NF])

        c = 0

        self.pack_propagate(True)

        for wid in to_render[self._offset::]:
            wid: SettsElement

            if wid.secreate is not None:
                ready = wid.secreate(self)
            else:
                wdg = WTYPES.get(wid.w, None)
                if not wdg:
                    wdg = getattr(tkinter, wid.w, None)
                if not wdg:
                    ready = tkinter.Label(self, text=f'Unknown wType {wid.w!r}\n{''.join(f'{k}: {v}\n' for k, v in wid.kw.items())}', name=f'setts-runtime-{c}')
                else:
                    comma = None
                    if 'command' in wid.kw:
                        comma = wid.kw['command']
                        if isinstance(comma, str):
                            if comma.startswith('PAGE'):
                                comma = self.to_page(comma[4::])

                    text = 'no text'
                    if 'text' in wid.kw:
                        text = wid.kw['text']
                    elif 'textfunc' in wid.kw:
                        text = wid.kw['textfunc']()

                    cfg = wid.kw.copy()
                    cfg.pop('text', None)
                    cfg.pop('textfunc', None)
                    cfg.pop('command', None)

                    try:
                        ready = wdg(master=self, command=comma, text=text, name=f'setts-runtime-{c}', **cfg)
                        ready.bind('<MouseWheel>', self._set_offset)
                    except Exception as _ex:
                        print(f'Error: widget not created {wid}, see LTI LibSettings-WidgetErrors')
                        w_errors(f'=====Error creating {wid.w}=====:\n{''.join(f'{k}: {v}\n' for k, v in wid.kw.items())}{''.join(traceback.format_exception(_ex))}\n\n')
                        ready = None

            if ready is not None:
                ready.place(x=0, y=y, relwidth=1.0)
                ready.update_idletasks()
                y += ready.winfo_height()
                c += 1

            if y > self.winfo_height():
                break

        self._ch = len(to_render) - (c - 2)

    def _create_base(self, sm=False):
        try:
            self._create_base_actual(sm)
        except Exception as _ex_default:
            SafeLabel(self, text=f'Failed to run default build').pack()
            try:
                self._create_base_actual(True)
            except Exception as _ex:
                SafeLabel(self, text=f'Failed to run SAFEMODE build').pack()

    def build(self):
        super().build()


class SettingsAPI:
    @classmethod
    def create_page(cls, name):
        print(f'Created page {name}')
        SETTS_DATA[name] = []
        cls.create_widget(None, 'Button', text=name, command=f'PAGE{name}')

    @classmethod
    def create_widget(cls, page, wtp, **kwargs):
        f_tweak = 'UNKNOWN'

        for _i in traceback.extract_stack():
            if 'NewJBTweaks' in _i.filename:
                f_tweak = _i.filename
                break

        se = SettsElement(wtp, f'SAPI-CREATED {os.path.basename(f_tweak)}', **kwargs)

        if page in [None, '', 'ROOT']:
            print(f'Created {se} in BASIC_BUTTONS')
            BASIC_BUTTONS.append(se)
        else:
            print(f'Created {se} in {page}')
            SETTS_DATA[page].append(se)

    @classmethod
    def extent_wtypes(cls, name, _cl: object, overwrite=False):
        if not overwrite and name in WTYPES:
            raise ValueError(f'{name} already registered')
        WTYPES[name] = _cl
        return name

    @classmethod
    def rebuild(cls):
        if isinstance(Application.settings_cl, SettsRewrite):
            Application.settings_cl.build()
        else:
            entry()
            Application.settings_cl.build()

    @classmethod
    def add_base_widget_hook(cls, idx, callback):
        """Replaces base_widget on idx to return of callback

        Base widgets:
        0 - Interface settings
        1 - Debug settings
        2 - Account settings
        3 - Plugin repository
        4 - Memory manager"""
        if idx in BASE_WIDGET_HOOKS:
            raise ValueError('Already hooked')
        print(f'Hooked {idx} on {callback}')
        BASE_WIDGET_HOOKS[idx] = callback

    @classmethod
    def recreate_settings(cls):
        entry()


def entry():
    Application.settings_cl = Application.Settings()
    Application.reinit_ui()

def toggle_sm():
    global _safe_mode
    _safe_mode = not _safe_mode
    print(f'[!] Safe mode state: {_safe_mode}')


Application.Settings = SettsRewrite

@J.API.on_ready_window
def _set_k():
    Application.main.bind('<Control-a>', lambda e: entry())
    Application.main.bind('<Control-g>', lambda e: toggle_sm())


J.SharedMemory['SettingsAPI'] = SettingsAPI

print(f'Created api')
