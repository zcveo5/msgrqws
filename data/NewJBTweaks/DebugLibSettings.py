#meta
# {"req": ["LibSettings"]}
from LibSettings import SettingsAPI, BASIC_BUTTONS, SETTS_DATA, SettsElement
from data.lib.ui import Popup, Frame, Button, Label


class SettsElementRepresent(Frame):
    def __init__(self, master, setts_elem: SettsElement):
        self.elem = setts_elem
        super().__init__(master)
        self._lbl = Label(self, text=f'Wtype: {setts_elem.w}\nsecreate: {setts_elem.secreate}\n\n' + ('\n'.join([f'{k}: {v}' for k, v in setts_elem.kw.items()])))
        Button(self, text=f'{self.elem.semeta}', command=self._toggle_inf).pack()

    def _toggle_inf(self):
        if self._lbl.winfo_ismapped():
            self._lbl.pack_forget()
        else:
            self._lbl.pack()


class Openable(Frame):
    def __init__(self, master, text):
        super().__init__(master)
        self.content = Frame(self)
        Button(self, text=text, command=self._toggle_inf).pack()

    def _toggle_inf(self):
        if self.content.winfo_ismapped():
            self.content.pack_forget()
        else:
            self.content.pack()


def _watch_basic_buttons():
    pop = Popup(title='BASIC_BUTTONS Viewer')
    pop.pack_propagate(True)
    pop.root_frame.pack_propagate(True)
    for bb in BASIC_BUTTONS:
        SettsElementRepresent(pop, bb).pack(fill='x')


def _watch_setts_data():
    pop = Popup(title='BASIC_BUTTONS Viewer')
    pop.pack_propagate(True)
    pop.root_frame.pack_propagate(True)
    for k, v in SETTS_DATA.items():
        o = Openable(pop, f'{k}')
        o.pack(fill='x')
        for s in v:
            SettsElementRepresent(o.content, s).pack(fill='x', anchor='nw', padx=10)


if __debug__:
    SettingsAPI.create_page('Settings API Debug')
    SettingsAPI.create_widget('Settings API Debug', 'Button', text='See BASIC_BUTTONS', command=_watch_basic_buttons)
    SettingsAPI.create_widget('Settings API Debug', 'Button', text='See SETTS_DATA', command=_watch_setts_data)