import socket

if 'local_jb_sockCache' in globals():
    local_jb_sock = globals()['local_jb_sockCache']
else:
    print('new socket')
    local_jb_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_jb_sock.connect(('127.0.0.1', 65523))

def reload_FromTweak():
    print('SEND!')

    local_jb_sock.send('Reload'.encode('utf-8'))

    print('Waiting to answer from server...')
    while True:
        re = local_jb_sock.recv(1024).decode('utf-8')
        if re == 'Ready':
            print('Server ready')
            break

    print('exit!')
    exit()


setts_orig = Settings

class SettingsReloaded(setts_orig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._base_widgets.append(Button(self._o, text='Full Reload',
                                                command=reload_FromTweak, bg=default_bg,
                                                fg='red', font=font_theme))


Settings = SettingsReloaded