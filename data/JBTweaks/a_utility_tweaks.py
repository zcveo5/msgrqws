import json, tkinter
from data.lib.ui import Popup

Button(text='Quit this mainloop', command=main.quit).pack(anchor='se')

class TwkSettings:
    def __init__(self):
        try:
            self._j = json.load(open('./data/utils_twk.json', 'r'))
        except (json.JSONDecodeError, FileNotFoundError):
            print('[err] utils twk jsn fail')
            with open('./data/utils_twk.json', 'w') as fl:
                fl.write('{}')
            self._j = json.load(open('./data/utils_twk.json', 'r'))

    @property
    def json(self):
        return self._j

    def backup(self):
        json.dump(self._j, open('./data/utils_twk.json', 'w'))


def utils_Setts():
    def toggle_pass_server(event):
        _utils_setts.json['server_pass'] = not _utils_setts.json.get('server_pass', False)
        _utils_setts.backup()

    def toggle_minimalistic_loading(event):
        _utils_setts.json['minimalistic_loading'] = not _utils_setts.json.get('minimalistic_loading', False)
        _utils_setts.backup()

    w = Popup(title='Utils Settings')
    w.pack_propagate(False)
    pass_server = tkinter.Checkbutton(w, text='Server Connection Bypass Enabled')
    if _utils_setts.json.get('server_pass', False):
        pass_server.select()
    pass_server.pack()
    pass_server.bind('<ButtonRelease-1>', toggle_pass_server)

    minimalistic_loading = tkinter.Checkbutton(w, text='Mini loading')
    if _utils_setts.json.get('minimalistic_loading', False):
        pass_server.select()
    minimalistic_loading.pack()
    minimalistic_loading.bind('<ButtonRelease-1>', toggle_minimalistic_loading)


_utils_setts = TwkSettings()

setts_orig = Settings

class SettingsReloaded(setts_orig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._base_widgets.append(Button(self._o, text='Utils Settings',
                                                command=utils_Setts, bg=default_bg,
                                                fg=default_fg, font=font_theme))


Settings = SettingsReloaded

def passer(name):
    def _w(*args, **kwargs):
        print(f'[U_pass_con] {name}')
    return _w


if _utils_setts.json.get('server_pass', False):
    def wrapper_gda(*args, **kwargs):
        print('[warn] passed GDA!')
        return {'answer': ''}

    print('\x1b[33mSERVER CONNECTION DISABLED BY UtilTweakPassCon\x1b[0m')
    globals()['chat_lib'].Chat.connect = passer('chat_lib connect')
    globals()['auth'].User.get_data = wrapper_gda
    globals()['auth'].connect = passer('auth root.connect')
    globals()['auth'].update_personal_conf = passer('upc')

if _utils_setts.json.get('minimalistic_loading', False):
    print('[error] Disable LoadLblLog BY UtilTweakPassCon')
    root.his['load_lbl_log'].place(x=-2000, y=-2000)
    root.update()

def check_reinit(slf, msg):
    if msg['action_for_chat_server'] == 'ReadyToQ':
        print('[er] final reinit')
        reinit_window()

    globals()['chat_lib'].Chat.send_original(slf, msg)


globals()['chat_lib'].Chat.send_original = globals()['chat_lib'].Chat.send
globals()['chat_lib'].Chat.send = check_reinit