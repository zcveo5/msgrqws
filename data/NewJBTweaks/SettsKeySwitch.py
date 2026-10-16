#meta
# {"req": ["LibSettings", "LibTweaksInfo"]}
import tkinter

import J
from LibSettings import SettingsAPI
import LibTweaksInfo
import Application

errors = LibTweaksInfo.Log('StsK_twk')

SettingsAPI.create_page('ScStsK')

ld = False

@J.API.on_mainloop
def _load():
    global ld
    if ld:
        return
    ld = True
    dat = Application.dat_d
    sc_sts_k = dat.get('[ScStsK]', None)
    errors(f'Dat d keys: {dat.keys()}, ScStsK: {sc_sts_k}')

    def _set_key(*_):
        skey, stype = dat['[ScStsK]'].split(';')
        skey = var.get()
        dat['[ScStsK]'] = f'{skey};{stype}'
        Application.s_key = skey

    def _set_type(*_):
        skey, stype = dat['[ScStsK]'].split(';')
        stype = 'Modern' if is_modern.get() else ''
        dat['[ScStsK]'] = f'{skey};{stype}'
        Application.sts_mode = stype

    var = tkinter.StringVar(value=Application.s_key)
    var.trace_add('write', _set_key)

    is_modern = tkinter.BooleanVar(value=Application.sts_mode == 'Modern')
    is_modern.trace_add('write', _set_type)

    if sc_sts_k:
        SettingsAPI.create_widget('ScStsK', 'Entry', textvariable=var)
        SettingsAPI.create_widget('ScStsK', 'Checkbutton', variable=is_modern, text='Modern')
        SettingsAPI.create_widget('ScStsK', 'Button', text='Reload NC', command=Application.reload_data_nc)
    else:
        SettingsAPI.create_widget('ScStsK', 'Label', text='Cannot find ScStsK in dat_d. Check version of application')