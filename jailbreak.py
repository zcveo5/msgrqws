import io
import json
import os.path
import socket
import subprocess
import sys
import threading
import time
import tkinter
from tkinter import Button
from tkinter.messagebox import showinfo
try:
    from data.lib import ui
except (ModuleNotFoundError, ImportError):
    print('$ Using legacy (data.btaeui instead data.lib.ui) ui format;')
    try:
        from data import btaeui as ui
        if not hasattr(ui, 'Win'):
            print('$ Using very (data.btaeui hasnt Win) legacy ui format; Errors may appear')
            ui.Win = tkinter.Tk
    except (ModuleNotFoundError, ImportError):
        print('$ Using very-very (no data.btaeui) legacy ui format; Errors GRANTED')
        class _a:
            pass
        ui = _a()
        ui.Win = tkinter.Tk

except Exception as _import_x:
    input(f'unk {_import_x}')

files = {'legacy_script': r"""import threading
from tkinter import Label, Button, Frame
from jailbreak import ModWin

def reinit_ui_mod(*args, **kwargs):
    main.wm_geometry('900x500')
    orig_reinit_ui(*args, **kwargs)


class __OBJ__FUCK_YOOU:
    def __getattribute__(self, item):
        print(f'[*] $JBLS emulating {item}')
        return self

    def __call__(self, *args, **kwargs):
        ...

def quit():
    global work
    work = True
    main.quit()

orig_reinit_ui = reinit_ui
reinit_ui = reinit_ui_mod

main.quit() ; main.destroy()
main = ModWin()
main.wm_geometry('900x500')
main.adv = 'Legacy'
#main.resizable(False, False)
buttons = Frame()
buttons.pack_propagate(True)
buttons.place(relx=1.0, y=0, anchor='ne')
load_lbl = Label(justify='left')
load_lbl.place(x=0, y=30)
exit_button = Button(buttons, text='exit', command=exit)
exit_button.pack(anchor='sw')
action_load = Button(buttons, text='action not set')
action_load.pack(anchor='sw')
try:
    Button(buttons, text='debug', command=Debug().debugtools).pack(anchor='sw')
except: pass
pb = __OBJ__FUCK_YOOU()
try:
    Button(buttons, text='Continue', command=quit).pack(anchor='sw')
except: pass
bt_server_data = (True, {'password': '123123123'})
receive_thread = __OBJ__FUCK_YOOU()
exec(open('./jailbreak_exec_tweaks.py', 'r').read())""",
         "jailbreak_exec_tweaks": r"""import json
import os
import traceback
from json import JSONDecodeError


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

globals()['__JB_jb_print_exception__'] = cool_exception_print

print(f'$ JAIL LIB \n $ # $ # $ # $ # $ # $ # $ # $ #\nGlobals (for optimizing, only keys):\n{', '.join(globals().keys())}\nLocals (for optimizing, only keys):\n{', '.join(locals().keys())}\n$ # $ # $ # $ # $ # $ # $ # $ # ')

if not os.path.exists('./data/JBTweaks'):
    os.mkdir('./data/JBTweaks')

print('$JB Loading Tweaks...')
print(f'$JB Running as {__name__}')
tweaks_files = []
globals()['__JailBreakTweaks__'] = []

class Dict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        try:
            refresh_shared()
        except NameError: pass

try:
    globals()['__jb_shared_data__'] = Dict(json.load(open('./data/tweaks_settings.json')))
except (JSONDecodeError, FileNotFoundError):
    json.dump({}, open('./data/tweaks_settings.json', 'w'))
    globals()['__jb_shared_data__'] = Dict(json.load(open('./data/tweaks_settings.json')))

def refresh_shared():
    json.dump(globals()['__jb_shared_data__'], open('./data/tweaks_settings.json', 'w'))
    globals()['__jb_shared_data__'] = Dict(json.load(open('./data/tweaks_settings.json')))
    

for file in os.listdir('./data/JBTweaks'):
    if file not in ['tweaks.json', 'configure.py', '__pycache__']:
        print(f'$JB Detected {file}')
        tweaks_files.append(file)
if not os.path.exists('./data/JBTweaks/tweaks.json'):
    with open('./data/JBTweaks/tweaks.json', 'w') as fl:
        fl.write('{}')
_setts = json.load(open('./data/JBTweaks/tweaks.json', 'r'))
print('====== EXECUTING ======')
for file in tweaks_files:
    adv = ''
    if file not in _setts:
        adv = '(!)'
        _setts.update({file: {'state': 'True'}})
    if _setts[file]['state']:
        print(f'$JB Executing {file} {adv}')
        globals()['__JailBreakTweaks__'].append(f'{file}')
        namespace = globals()
        if file not in globals()['__jb_shared_data__']:
            globals()['__jb_shared_data__'][file] = {}
        namespace[f'__my_jb_shared_data__{file}'] = globals()['__jb_shared_data__'][file]
        try:
            exec(compile(open(f'./data/JBTweaks/{file}', 'r', errors='replace').read(), f'./data/JBTweaks/{file}', 'exec'), namespace)
        except Exception as _ex:
            globals()['__JB_jb_print_exception__'](_ex.__class__, _ex, _ex.__traceback__)

json.dump(globals()['__jb_shared_data__'], open('./data/tweaks_settings.json', 'w'))

print('$JB Tweaks Loaded!')

"""}


class ModWin(ui.Win):
    def __init__(self, **kwargs):
        self.__mainloop = False
        self.adv = ''
        super().__init__(**kwargs)
        self.title('msgr-qw')
        if not hasattr(self, 'his'):
            self.his = {}
        if not hasattr(self, 'tk_thread'):
            def _tk_thread(target, sleep_time, /, *args):
                def wrapper(*_args):
                    _ret = target(*_args)
                    if _ret != -1:
                        self.after(sleep_time, wrapper, *args)
                wrapper(*args)

            self.tk_thread = _tk_thread

        for i in self.winfo_children():
            i.place_forget()
            i.pack_forget()

        self.his['load_lbl'] = tkinter.Label(justify='left')
        self.his['load_lbl'].place(x=0, y=0)
        self.his['load_lbl_log'] = tkinter.Text(autoseparators=False, wrap="none")
        self.his['load_lbl_log'].place(x=0, y=30, relwidth=0.9)
        def _wrapper():
            try:
                temp = sys.stdout.read().split('\n')
            except (io.UnsupportedOperation, AttributeError):
                temp = ["Can't read logs :("]
            if len(temp) > 24:
                temp = temp[len(temp) - 24::]
            try:
                self.his['load_lbl']['text'] = ''
                if self.his['load_lbl_log'].get('0.0', 'end').split('\n') != temp:
                    self.his['load_lbl_log'].delete('0.0', 'end')
                    self.his['load_lbl_log'].insert('end', '\n'.join(temp))
                    self.his['load_lbl_log'].yview_scroll(100, 'units')
            except KeyError:
                new_print('Loaded!')
                return -1
        self.tk_thread(_wrapper, 100)
    def mainloop(self, n = 0):
        try:
            temp = sys.stdout.read()
        except (io.UnsupportedOperation, AttributeError):
            new_print('stdout read failed')
            temp = ['READY', '[msgr.py][info] BTAEML LOADED']
        Button(text='[ JAILBREAK ] quit this window cycle', command=self.quit).pack()
        try:
            bps = eval(os.environ['__JailBreak_CODE_CONFIG__'])['bypass_script']
        except KeyError:
            new_print('KeyError get bypass...')
            bps = 'non'
        if 'READY' in temp and bps == 'default' or 'Servers connection Completed' in temp and bps == 'srv' or bps == 'non':
            new_print('$JB Final mainloop')
            if not os.path.exists('./data/JBTweaks'):
                new_print('$JB Running setup...')
            super().mainloop(n)
        else:
            new_print('$JB Skipping non-final mainloop')
    def title(self, t=''):
        if t != '':
            super().title(f'{t} | JailBreak {self.adv}')
            return None
        else:
            return super().title()

    def orig_mainloop(self):
        super().mainloop()


new_print = lambda *s: print(f'\033[31m[Jailbreak] {' '.join([str(i) for i in s])}\033[0m')


class Server:
    def __init__(self, host, port, process, name='InternalServer'):
        self._addr = (host, port)
        self._name = name
        self._fprint = new_print
        self._process = process

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(self._addr)
        self._sock.listen(5)

        threading.Thread(target=self.accept_thread, daemon=True).start()

    def accept_thread(self):
        while True:
            sock, addr = self._sock.accept()
            self._fprint(f'new {addr}')
            threading.Thread(target=self.handle_thread, daemon=True, args=(sock,)).start()

    def handle_thread(self, sock: socket.socket):
        while True:
            msg = ''
            try:
                msg = sock.recv(1024).decode('utf-8')
            except ConnectionError:
                break

            if msg == '':
                break

            answer: str = self._process(msg)

            sock.send(answer.encode('utf-8'))


def start():
    if config['legacy']:
        new_print('Legacy-boot, no core plugins support')
        subprocess.run([sys.executable,
                        config['file_to_load'],
                        "BootUpAction$=%exec(compile(open('./jailbreak_legacy_script.py', 'r').read(), './jailbreak_legacy_script.py', 'exec'))"] + sys.argv[
                                                                                                                                                    1::])
    else:
        subprocess.run([sys.executable,
                        config['file_to_load'],
                        f"""RunBeforeWin$=%from jailbreak import * ; Win = ModWin ; [exec(compile(open(i).read(), 'Driver:'+i, 'exec'), globals(), locals()) for i in {config['core_plugins']}]""",
                        "BootUpAction$=%exec(compile(open('./jailbreak_exec_tweaks.py', 'r').read(), './jailbreak_exec_tweaks.py', 'exec'))"] + sys.argv[
                                                                                                                                                1::])

ready_for_reload = True

if __name__ == '__main__':
    if not os.path.exists('./data/logs'):
        os.mkdir('./data/logs')

    with open('./jblog.log', 'w'):
        pass

    class Log:
        def __init__(self):
            self.buffer = io.StringIO()

        def write(self, s):
            sys.__stdout__.write(f'{s}')
            self.buffer.write(s)
            open('./jblog.log', 'a').write(f'{s}')

        def read(self):
            return self.buffer.read()

    sys.stdout = Log()
    new_print('* Jailbreak for msgr *')
    new_print('$ Internal server is starting...')

    def handler(msg):
        global ready_for_reload
        if msg == 'Reload':
            ready_for_reload = True
            new_print('Ready for reload')
            return 'Ready'
        else:
            return 'Unknown'

    server = Server('127.0.0.1', 65523, handler)

    if not os.path.exists('./jailbreak_exec_tweaks.py') or open('./jailbreak_exec_tweaks.py').read() != files['jailbreak_exec_tweaks']:
        new_print('Creating jailbreak_exec_tweaks')
        with open('./jailbreak_exec_tweaks.py', 'w') as fl:
            fl.write(files['jailbreak_exec_tweaks'])
    if not os.path.exists('./jailbreak_legacy_script.py') or open('./jailbreak_legacy_script.py').read() != files['legacy_script']:
        new_print('Creating legacy script')
        with open('./jailbreak_legacy_script.py', 'w') as fl:
            fl.write(files['legacy_script'])
    new_print('Files:')
    new_print(', '.join(os.listdir()))
    new_print('$JB Launcher Mode')
    if '--debug' not in sys.argv:
        if not os.path.exists('./jailbreak_data.json') or '--update-config' in sys.argv:
            with open('./jailbreak_data.json', 'w'):
                pass
            new_print('$ Analyzing source code...')
            _result = {}
            _code = open('./msgr.py', 'r', errors='Replace').read()
            if 'RunBeforeWin' not in _code:
                new_print('$ RunBeforeWin is not supported')
                _result['legacy'] = True
            else:
                new_print('$ RunBeforeWin is supported')
                _result['legacy'] = False
            new_print('$ Finding launcher...')
            if os.path.exists('./loader.py') and os.path.exists('./launcher.pyw'):
                new_print('$ Detected loader/launcher system')
                _result['file_to_load'] = 'loader.py'
            elif os.path.exists('./launcher.pyw'):
                new_print('$ Detected launcher')
                _result['file_to_load'] = 'launcher.pyw'
            elif os.path.exists('./run.pyw'):
                new_print('$ Detected run.pyw legacy system')
                _result['file_to_load'] = 'run.pyw'
            new_print('\n[*] servers - bypasses only servers connection\n[*] non final - bypasses all non final mainloop')
            ans = input('[?] Mainloop bypass script:')
            if ans == 'servers':
                _result['bypass_script'] = 'srv'
            elif ans == 'non final':
                _result['bypass_script'] = 'default'
            json.dump(_result, open('./jailbreak_data.json', 'w'))
            new_print(f'Analyzing completed:\nLegacy: {_result["legacy"]}\nExecutable: {_result["file_to_load"]}')
        config = json.load(open('./jailbreak_data.json', 'r'))

        if 'core_plugins' not in config:
            config['core_plugins'] = []

        os.environ['__JailBreak_CODE_CONFIG__'] = str(config)
        os.environ['__LOW_LAUNCHER'] = os.path.abspath('launcher.pyw')

        new_print('LAUNCH')
        sys.stdout = sys.__stdout__

        while ready_for_reload:
            ready_for_reload = False
            start()
            new_print('Reload')

    else:
        new_print('Debug mode:')
        while True:
            exec(input('>>>'))
