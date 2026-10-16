import os.path
import platform
import subprocess
import sys
import traceback

try:
    import tkinter
except ModuleNotFoundError:
    with open('./cmd_alert.py', 'w') as fl:
        fl.write('input("Please install tkinter module to continue")')
    subprocess.run([sys.executable, './cmd_alert.py'])
    exit()
from tkinter.messagebox import showerror, askyesno
try:
    import requests
except ModuleNotFoundError:
    showerror('Error', 'Requests Not Found')
    exit()

def excepthook(exc_type, exc_value=None, exc_traceback=None):
    tb_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print('===== TRACEBACK =====\n' + tb_text + f'\n===== END =====')
    input()
    try:
        showerror(f'Error: {exc_type.__name__}', tb_text)
    except AttributeError:
        showerror(f'Error: {exc_type.__class__}', tb_text)

class Log:
    def __init__(self, type_: str, _file):
        self.type_ = type_
        self.file = _file
        self.name = self.file.name
        self.last_v = ''

    def write(self, v):
        if v not in ['', ' ', '\n', '<VirtualEvent event x=0 y=0>'] and v != self.last_v:
            repr_v = repr(v)[1:-1]
            if repr(v)[1:-1][len(repr_v) - 2:len(repr_v)] == r'\n':
                v = v[:len(v) - 1]
            try:
                self.file.write(f'[{self.type_}]{v}\n')
            except UnicodeError:
                self.file.write(f'[{self.type_}][loader] log_file_unsupported_encoding\n')
            self.last_v = v
            self.file.flush()
        if v not in ['', ' ', '\n', '<VirtualEvent event x=0 y=0>']:
            try:
                sys.__stdout__.write(f'[{self.type_}]{v}\n')
            except AttributeError:
                pass

    def flush(self):
        self.file.flush()

os.makedirs('./data/logs', exist_ok=True)
with open('./data/logs/low_launcher.log', 'w'):
    pass

log_file = open('./data/logs/low_launcher.log', 'a')

if '-no-file-log' not in sys.argv:
    sys.stderr = Log(type_='  SE  ', _file=log_file)
    sys.stdout = Log(type_='  SO  ', _file=log_file)
sys.excepthook = excepthook

libs = ['./data/lib/encrypting.py', './data/lib/plugin_api.py', './data/lib/ru_to_en.py', './data/lib/threading_custom.py', './data/lib/types_adv.py', './data/lib/ui.py', './data/lib/utils.py', './data/lib/utils2.py', './data/lib/connect/auth.py', './data/lib/connect/chat.py']
files = ['msgr.py', 'loader.py',
         './data',
           './data/base_data.json',
            './data/locale',
             './data/locale/en',
              './data/locale/en/locale.cfg',
           './data/lib',
             './data/lib/connect',
           './data/theme',
            './data/theme/night.theme',
         './plugins']
py_ver = sys.version_info
url_patches = "https://raw.githubusercontent.com/zcveo5/msgr-patches/main"
url_main =    "https://raw.githubusercontent.com/zcveo5/msgr-qw/main"

DISABLE_UPDATES = True

if not DISABLE_UPDATES:
    pass
else:
    libs = []
    files = []

for i in sys.argv:
    if 'custom-update-server' in i:
        url_main = i.split('==')[1]

def download_patch(pyver, libn, save_path):
    content = requests.get(f'{url_patches}/{pyver}/{libn}.py').content
    with open(f'{save_path}/{libn}_backup', 'wb') as _backup_fl:
        _backup_fl.write(open(f'{save_path}/{libn}.py', 'rb').read())
    with open(f'{save_path}/{libn}.py', 'wb') as _file_save:
        _file_save.write(content)


def download_file(path, save_path):
    content = requests.get(f'{url_main}/{path.replace("./", "")}').content
    with open(save_path, 'w'):
        pass
    with open(save_path, 'wb') as _save_fl:
        _save_fl.write(content)

def check_for_updates():
    for _i in libs:
        ver = open(_i, 'rb').readlines(1)
        if not ver:
            return True
        elif ver[0] != b'# downloaded from msgr-patches for 3.8!\r\n':
            if 8 <= py_ver[1] < 13:
                return True
        elif ver[0] != b'# downloaded from msgr-patches!\r\n':
            if py_ver[1] >= 13:
                return True

    return False


def update_status(text, mode='set'):
    if mode == 'set':
        status_lbl['text'] = text + '\n'
    elif mode == 'plus':
        status_lbl['text'] += text + '\n'
    win.update()


print('[software checker] ~ INFO ~\n[ SYS ] Running on ' + platform.system() + ' ' + str(platform.release()) + '\n[ PY ] Python ' + str(py_ver[0]) + '.' + str(py_ver[1]) + '.' + str(py_ver[2]))

win = tkinter.Tk()
win.title('Info')
tkinter.Label(win,
              text='System: ' + str(platform.system()) + ' ' + str(platform.release()) + '\n' + 'Python: ' + str(py_ver[0]) + '.' + str(py_ver[1]) + '.' + str(py_ver[2]),
              font=('Consolas', 9)).pack()
status_lbl = tkinter.Label(win, justify='left', font=('Consolas', 9))
status_lbl.pack()
update_status('checking files...')
need_to_download = []
for _fl in files + libs:
    res = os.path.exists(_fl)
    if res:
        path_spl = _fl.split('/')
        if '.' in path_spl[len(path_spl) - 1]:
            _frst = open(_fl, 'rb').readlines(1)
            if not _frst:
                update_status(f'[  ER  ] {_fl} not found on repo', 'plus')
                #showerror('Error', f'[  ER  ] {_fl} not found on repo')
            elif _frst[0]  == b'404: Not Found' and _fl != './data/data.nc':
                update_status(f'[  ER  ] {_fl} not found on repo', 'plus')
                showerror('Error', f'[  ER  ] {_fl} not found on repo')
        update_status(f'[  OK  ] {_fl} exists', 'plus')
    else:
        update_status(f'[  ER  ] {_fl} not exists, creating', 'plus')
        path_spl = _fl.split('/')
        if '.' in path_spl[len(path_spl) - 1]:
            need_to_download.append(_fl)
            with open(_fl, 'w'):
                pass
            update_status(f'[  OK  ] created {_fl} as file', 'plus')
        else:
            os.mkdir(_fl)
            update_status(f'[  OK  ] created {_fl} as directory', 'plus')

if '--update-line' in sys.argv:
    def add_to_download_list():
        global need_to_download
        need_to_download += add.get().split()
    req_win = tkinter.Tk()
    req_win.protocol('WM_DELETE_WINDOW', lambda: exec('req_win.quit() ; req_win.destroy()'))
    add = tkinter.Entry(req_win)
    add.pack()
    tkinter.Button(req_win, text='add', command=add_to_download_list).pack()
    req_win.mainloop()

ns = '\n'
update_status('')
if need_to_download:
    if askyesno('Warning', f'You need to download files:\n\n{ns.join(need_to_download)}.\n\nDownload it now?'):
        update_status('[  OK  ] downloading needed files')
        for file in need_to_download:
            if file not in libs:
                update_status(f'[  WR  ] downloading {file}', 'plus')
                path_spl = file.split('/')
                try:
                    os.makedirs('/'.join(path_spl[0:len(path_spl) - 1]), exist_ok=True)
                except FileNotFoundError:
                    pass
                download_file(file, file)
            else:
                update_status(f'[  WR  ] {file} is lib, passing', 'plus')


if py_ver[0] < 3:
    showerror('Error', 'Unsupported Python major Version ' + str(py_ver[0]) + ' < 3')
    sys.exit()
if py_ver[1] < 8:
    showerror('Error', 'Unsupported Python minor Version 3.' + str(py_ver[1]) + ' < 3.8')
    sys.exit()
print(f'[  OK  ] supported python {py_ver[0]}.{py_ver[1]}')
if platform.system() not in ['Windows', 'Linux']:
    if not askyesno('Warning', 'Not Windows system detected. On your system MSGR not tested and some functions can not work. If it works, you can comment my repo on GitHub.\n\nContinue?'):
        sys.exit()
elif platform.system() == 'Windows':
    if platform.release() not in ['7', '10', '11']:
        showerror('Error', 'Unsupported Windows version')
        sys.exit()
elif platform.system() == 'Linux':
    ...
print(f'[  OK  ] supported platform {platform.system()}')
if py_ver[0] == 3 and 8 <= py_ver[1] < 13 and check_for_updates() or '--force-update' in sys.argv:
    #ask = askyesno('Warn', f'Detected Python 3.{py_ver[1]}.{py_ver[2]}. You need to download patched libs optimized for version 3.8 - 3.12.\nDownload it now?')
    ask = False
    if ask:
        win.winfo_children()[0]['text'] = 'Update in progress!\ndownloading utils...'; win.update()
        download_patch('3.8', 'utils', './data')

        win.winfo_children()[0]['text'] = 'Update in progress!\ndownloading auth...'; win.update()
        download_patch('3.8', 'auth', './plugins/btac')

        win.winfo_children()[0]['text'] = 'Update in progress!\ndownloading chat...'; win.update()
        download_patch('3.8', 'chat', './plugins/btac')

        win.winfo_children()[0]['text'] = 'Update in progress!\ndownloading core...'; win.update()
        download_patch('3.8', 'mod', './plugins/core')

        win.winfo_children()[0]['text'] = 'Update in progress!\ndownloading btaeui...'; win.update()
        download_patch('3.8', 'btaeui', './data')
elif py_ver[0] == 3 and py_ver[1] == 13 and check_for_updates() or '--force-update' in sys.argv:
    #ask = askyesno('Warn', 'Detected Python 3.13. You need to download patched libs optimized for version 3.13 and above.\nDownload it now?')
    ask = False
    if ask:
        win.winfo_children()[0]['text'] = 'Update in progress!\ndownloading utils...' ; win.update()
        download_patch('3.13', 'utils', './data')

        win.winfo_children()[0]['text'] = 'Update in progress!\ndownloading auth...' ; win.update()
        download_patch('3.13', 'auth', './plugins/btac')

        win.winfo_children()[0]['text'] = 'Update in progress!\ndownloading chat...' ; win.update()
        download_patch('3.13', 'chat', './plugins/btac')

        win.winfo_children()[0]['text'] = 'Update in progress!\ndownloading core...' ; win.update()
        download_patch('3.13', 'mod', './plugins/core')

        win.winfo_children()[0]['text'] = 'Update in progress!\ndownloading btaeui...' ; win.update()
        download_patch('3.13', 'btaeui', './data')

win.quit() ; win.destroy()
print('  -  ~  *  LOADER  *  ~  -')
os.environ['__LOW_LAUNCHER'] = os.path.abspath(__file__)
subprocess.run([sys.executable, 'loader.py'] + sys.argv[1::])
