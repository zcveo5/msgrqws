# METADATA
# {"disabled": true}
import Application

executor = r"""import json
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
"""


Application.sys.argv.append(f'BootUpAction$=%{executor}')