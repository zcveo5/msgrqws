import json, os
import threading
import tkinter
import traceback
from tkinter import Tk, Label, Button
import tkinter.ttk as ttk
from data.lib.utils2 import SConfig, SNConfig, get_win, JsonObject
import ctypes
import platform
import sys
from tkinter.messagebox import showerror, askyesno

from data.lib.utils import Log, convert_path_to_module
from data.lib.encrypting import *

os.environ['__LOW_LAUNCHER'] = os.path.abspath('launcher.pyw')
_low = os.environ.get('__LOW_LAUNCHER')
if not _low:
    _low = ''

if 'launcher.py' not in sys.argv[0] and 'launcher.py' not in _low:
    sys.exit()

cons_shut = True

CLR_NC = "#$#$SER[SETTINGS]\n{'ADV_DATA': {}, 'USER_SETTINGS': {'TELEMETRY_ENABLED': 'False', 'SERVER': '', 'SEL_LOCALE': 'en', 'FIRST_BOOT': 'True', 'THEME': 'night', 'USERNAME': '', 'BTAEML': 'True', 'BT_SERV': '', 'PASSWORD': '', 'HASHING_METHOD': 'sha256', 'SCREEN_SETTINGS': [1, 0]}}\n#$#$SER[LOADER_CONFIG]\nCC_VERSIONS:msgr.py\nCC_ALLOW_GH_UPDATE:False\nCC_ALLOW_LLF_UPDATE:False"

def show(title, text, ret_win=False, custom_close=None):
    info = Tk()
    def exit_mb():
        nonlocal info
        info.destroy()
        info = None
        if custom_close is not None:
            custom_close()
    info.title(title)
    fnt = ('Consolas', 11)
    bg = 'white'
    fg = 'black'
    info.configure(bg=bg)
    info.resizable(False, False)
    info.attributes('-topmost', True)
    Label(info, text=text, bg=bg, fg=fg, font=fnt, justify=tkinter.LEFT).pack(anchor='center', pady=30, ipadx=10)
    Button(info, text='OK', bg=bg, fg=fg, font=fnt, command=exit_mb).pack(anchor='se', side='bottom', expand=True, ipadx=10, ipady=5)
    if ret_win:
        return info
    return None


def custom_exc_handler(exc_type, exc_value=None, exc_traceback=None):
    tb_lines = list(traceback.format_exception(exc_type, exc_value, exc_traceback))
    try:
        if 'safe_command' in tb_lines[1]:
            tb_lines = tb_lines[2::]
            tb_lines.insert(0, 'btae ui widget Traceback\nbtae ui widget called function, last returned raw traceback:\n')
    except IndexError:
        pass
    tb_text = "".join(tb_lines)
    print('===== TRACEBACK =====\n' + tb_text + f'\n===== END =====')
    with open('./data/logs/tracebacks.log', 'a') as f_l:
        f_l.write(tb_text + '\n\n')
    try:
        show(f'Error: {exc_type.__name__}', tb_text)
    except AttributeError:
        show(f'Error: {exc_type.__class__}', tb_text)


def custom_exc_handler_thread(exc_type, exc_value=None, exc_traceback=None):
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = "".join(tb_lines)
    print('===== TRACEBACK THREAD =====\n' + tb_text + '===== END =====')
    with open('./data/logs/tracebacks.log', 'a') as f_l:
        f_l.write(tb_text + '\n\n')
    show(f'Error from thread: {exc_type}', tb_text)


def custom_excepthook(exc_type, exc_value, exc_traceback):
    # Получаем последний кадр из объекта трассировки
    last_frame = exc_traceback.tb_frame

    # Из кадра получаем объект кода
    code_obj = last_frame.f_code

    # Из объекта кода получаем имя функции
    function_name = code_obj.co_name

    # Печатаем имя функции и другую полезную информацию
    print(f"Произошла ошибка в функции: {function_name}")
    print(f"Тип ошибки: {exc_type.__name__}")
    print(f"Сообщение: {exc_value}")

    # Можно также вывести стандартную трассировку
    traceback.print_exception(exc_type, exc_value, exc_traceback)


def cool_exception_print(exc_type, exc_value, _tb):
    show_lines = 3

    all_levels_exceptions = []

    def rec(master):
        if master is not None:
            all_levels_exceptions.append(master)
            rec(master.tb_next)
    rec(_tb)

    rev = all_levels_exceptions.copy()
    #rev.reverse()

    ready = []

    for _exc in rev:
        line = _exc.tb_lineno
        _file = _exc.tb_frame.f_code.co_filename
        try:
            code = open(f'{_file}', 'r', errors='replace').read().split('\n')
            lineno = _exc.tb_lineno
            string = code[lineno-1]
            code[lineno-1] = f'\033[31m{string} <-- {exc_type.__name__}: "{exc_value}"\033[0m'
            for _str in range(0, len(code)):
                code[_str] = f'{_str + 1}: {code[_str]}'

            with_show_lines = code[line - show_lines:line + show_lines]

            code = f'File: "\033[33m{_file}\033[0m:{line}", line {line}, in {_exc.tb_frame.f_code.co_name}:\n0-{line-show_lines} ...\n{'\n'.join(with_show_lines)}\n{line + show_lines}-{len(code)} ...\n'
        except (FileNotFoundError, OSError):
            code = f'File: {_file}, on line {line}, in {_exc.tb_frame.f_code.co_name}:\n\033[31m{exc_type.__name__}: "{exc_value}"\033[0m\n'
        ready.append(code)
    print(f'===== Traceback =====\n{'\n'.join(ready)}\n===== END =====')
    show('Error (cep)', f'===== Traceback =====\n{'\n'.join(ready)}\n===== END =====')


def multi_exc_hand(exc_type, exc_value, tb):
    cool_exception_print(exc_type, exc_value, tb)
    #custom_excepthook(exc_type, exc_value, tb)


sys.excepthook = multi_exc_hand
threading.excepthook = custom_exc_handler_thread


with open('./data/msgr.log', 'w'):
    pass
log_file = open('./data/msgr.log', 'a')

sys.stderr = Log(type_='--> STDERR <--', file=log_file if '--no-file-log' not in sys.argv else None)
sys.stdout = Log(type_=' STDOUT ', file=log_file if '--no-file-log' not in sys.argv else None)

try:
    print(' ~ LOG STARTED ~')
except Exception as _ex:
    showerror(f'Error {type(_ex)}', traceback.format_exc())
    sys.exit()


try:
    import requests
except ModuleNotFoundError:
    print('[loader][warning] !! Update is unavailable: requests not found !!')

# opening datas
version_0 = '0'
loader = Tk()

NC_TEMPLATE = {'LOAD_NC': 'DATA.NC', 'RUNT_ACTION': '', 'DATA_NC_CLEARED': CLR_NC, 'EXC_DATA': {}, 'CC': {}}

try:
    base_conf = json.load(open('./data/base_data.json'))
except (FileNotFoundError, json.JSONDecodeError):
    with open('./data/base_data.json', 'w') as fl:
        fl.write(json.dumps(NC_TEMPLATE))
    base_conf = json.load(open('./data/base_data.json'))

dump_base = False

for k, v in NC_TEMPLATE.items():
    if k not in base_conf:
        base_conf[k] = v
        dump_base = True

if dump_base:
    with open('./data/base_data.json', 'w') as fl:
        json.dump(base_conf, fl)

# configuring window
loader.title(f'loader')
loader.resizable(False, False)
loader.geometry('300x100')
Label(text=f'file: {__file__}\nname: {__name__}\n').pack()
# info and windows check
print(f'[loader][info] launcher&exception hook v.{version_0}')
print(f'[loader][info] win release {platform.release()}')
# loading data.nc

_file_path = (
    (sys._getframe(0).f_code.co_filename if hasattr(sys, '_getframe') else None) or
    (sys.argv[0] if (hasattr(sys, 'argv') and sys.argv) else '')
)

if _file_path:
    print(_file_path)
    os.chdir(os.path.dirname(os.path.abspath(_file_path)))

print(os.path.abspath('.'))

if not os.path.exists(f'./data/{base_conf["LOAD_NC"]}'):
    with open(f'./data/{base_conf["LOAD_NC"]}', 'w'):
        pass

with open(f'./data/{base_conf["LOAD_NC"]}', 'rb') as fl:
    print(json.detect_encoding(fl.read()))

try:
    dat = SNConfig(decrypt(open(f'./data/{base_conf["LOAD_NC"]}', 'r', encoding='utf-8').read(), eval(base_conf['CC'])))
    data_ = dat.load()
    cnf = SConfig(data_['[LOADER_CONFIG]'])
    versions = cnf['CC_VERSIONS'].split('$%')
    vers = cnf['CC_VERSIONS'].split('$%')[0]
except (KeyError, TypeError, FileNotFoundError) as nc_load_ex:
    showerror('Error', f'{base_conf["LOAD_NC"]} not loaded. All configuration will be reset. If this is first launch, ignore this error.\nInfo: {nc_load_ex.__class__.__name__}: {nc_load_ex}')
    if askyesno(f'Clear {base_conf["LOAD_NC"]}?', f'Clear {base_conf["LOAD_NC"]}?'):
        if askyesno('?', f'Reset codec key?\nIf you see this error many times, click yes.'):
            base_conf['CC'] = str(generate_salt())
        json.dump(base_conf, JsonObject(open('./data/base_data.json', 'w')))
        base_conf = json.load(open('./data/base_data.json'))
        with open(f'./data/{base_conf["LOAD_NC"]}', 'w') as fl:
            d = base_conf['DATA_NC_CLEARED']
            fl.write(encrypt(d, eval(base_conf['CC'])))
        dat = SNConfig(decrypt(open(f'./data/{base_conf["LOAD_NC"]}', 'r').read(), eval(base_conf['CC'])))
        data_ = dat.load()
        cnf = SConfig(data_['[LOADER_CONFIG]'])
        versions = cnf['CC_VERSIONS'].split('$%')
        vers = cnf['CC_VERSIONS'].split('$%')[0]
    else:
        sys.exit()
loader.destroy()
# check LL_Update in RUNT_ACTION
if base_conf['RUNT_ACTION'] == 'LL_Update' and cnf['CC_ALLOW_GH_UPDATE'] == 'True':
    with open('./msgr.py', 'r') as fl:
        with open('./data/code_backup.py', 'w'):
            pass
        open('./data/code_backup.py', 'w').write(fl.read())
    if open('./data/code_backup.py', 'r').read() == open('./msgr.py', 'r').read():
        with open('./msgr.py', 'w'):
            pass
        with open('./msgr.py', 'w') as fl:
            def download_from_github(url, save_path):
                if 'github.com' in url and 'raw.githubusercontent.com' not in url:
                    url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')

                response = requests.get(url)
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                else:
                    print(f"update error: {response.status_code}")
            github_url = "https://raw.githubusercontent.com/zcveo5/msgr-qw/main/msgr.py"
            download_from_github(github_url, "msgr_upd.py")
            base_conf['RUNT_ACTION'] = 'LL_F_Update'
    else:
        print('[loader][error][update] failed to backup code')
# checking LL_F_Update in RUNT_ACTION
if base_conf['RUNT_ACTION'] == 'LL_F_Update' and cnf['CC_ALLOW_LLF_UPDATE'] == 'True':
    print('[loader] updating from file')
    try:
        open('./msgr_upd.py')
        with open('./msgr.py', 'r') as fl:
            with open('./data/code_backup.py', 'w'):
                pass
            open('./data/code_backup.py', 'w').write(fl.read())
        if open('./data/code_backup.py', 'r').read() == open('./msgr.py', 'r').read():
            with open('./msgr.py', 'w'):
                pass
            with open('./msgr.py', 'w') as _fl:
                _fl.write(open('./msgr_upd.py', 'r').read())
        print('[loader] updated')
        base_conf['RUNT_ACTION'] = ''
    except FileNotFoundError:
        print('[loader][error] cant find update file. must be in main directory (near with msgr.py) and named msgr_upd.py')
# Loader:AllFilesAreExec argv
if 'Loader:AllFilesAreExec' in sys.argv:
    tmp = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if '__pycache__' not in os.path.join(root, file):
                tmp.append(os.path.join(root, file).replace('\\', '/'))
    versions = []
    for i in tmp:
        if '.py' in i and i != 'run.pyw':
            versions.append(i)
    sys.argv.append('VerSelect')
# VerSelect argv
if 'VerSelect' in sys.argv:
    def ver_sel(event):
        global vers
        print(event)
        vers = ver_s.get()
        win.quit()
        win.destroy()
    win = Tk()
    win.geometry('200x200')
    Label(win, text='select ver').pack()
    ver_s = ttk.Combobox(win, values=versions, state='readonly')
    ver_s.bind('<<ComboboxSelected>>', ver_sel)
    ver_s.pack()

    win.mainloop()
# file check
if not os.path.exists(f'{vers}'):
    showerror('Error', f'{vers} is not exists')
    sys.exit()
# dpi from screen settings
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(eval(data_['[SETTINGS]'])['USER_SETTINGS']['SCREEN_SETTINGS'][1])
except (FileNotFoundError, AttributeError):
    pass
json.dump(base_conf, JsonObject(open('./data/base_data.json', 'w')))
path = convert_path_to_module(vers)
sys.argv.insert(1, path)
# execute
try:
    print(' - ~ * PROGRAM * ~ - ')
    app = __import__(path, globals(), locals())
    print('k')
    base_conf = json.load(open('./data/base_data.json', 'r'))
except Exception as __ex:
    exc = f'{type(__ex)}:{__ex}'
    print(f'[loader][error] {__ex}')
    print(f'[loader][traceback]\n{traceback.format_exc()}')
    print(exc)
    if exc not in base_conf['EXC_DATA']:
        get_win(exc_with_traceback=traceback.format_exc(), program_title='msgr qw')
    else:
        get_win(exc_with_traceback=base_conf['EXC_DATA'][exc], program_title='msgr qw')

print('ok loader kr')

cons_shut = False
if len(threading.enumerate()) > 1:
    print('some threads are exists, destroying')
    c = 0
    l_enum = len(threading.enumerate())
    for thread in threading.enumerate():
        print(f'{c}/{l_enum}')
        if thread != threading.current_thread():
            print(f'joined {thread.name}')
            thread.join()
        else:
            print('cur, passed')
        c += 1
print('exiting...')
