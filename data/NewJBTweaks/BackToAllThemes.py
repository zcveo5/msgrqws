#meta
# {"req": ["LibSettings"]}
import os
import sys

import Application
from LibSettings import SettingsAPI, SettsElement

ui = sys.modules['data.lib.ui']


last_combobox_th = None


class _ComboboxWrapper(ui.Combobox):
    def __init__(self, master=ui.app_root_window, bg=None, fg=None, font=None, values=None, _values=None, state='readonly',**kw):
        super().__init__(master, bg, fg, font, values, _values, state, **kw)

    def bind(self, _p, _a):
        super().bind(_p, _a)
        if _a.__name__ == 'sel_t':
            global last_combobox_th
            last_combobox_th = self

ui.Combobox = _ComboboxWrapper
Application.Combobox = _ComboboxWrapper


def _sub_f_ui_modified():
    self = Application.settings_cl
    self.sub_f_ui()
    last_combobox_th.values = list(Application.nc_themes.dct.keys()) + os.listdir('./data/theme') + ['black', 'light']
    last_combobox_th.filter_values(None)


def modify_btn(wdg: SettsElement):
    wdg.kw['command'] = _sub_f_ui_modified
    wdg.semeta = 'F_UI BBT'
    return wdg


SettingsAPI.add_base_widget_hook(0, modify_btn)