import json
import os
import traceback

if not os.path.exists('./data/JBTweaks'):
    os.mkdir('./data/JBTweaks')

print('$JB Loading Tweaks...')
print(f'$JB Running as {__name__}')
tweaks_files = []
globals()['__JailBreakTweaks__'] = []
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
        try:
            exec(open(f'./data/JBTweaks/{file}', 'r', errors='replace').read(), globals(), locals())
        except Exception as _ex:
            tb = _ex.__traceback__
            line = tb.tb_next.tb_lineno
            code = open(f'./data/JBTweaks/{file}', 'r', errors='replace').read().split('\n')
            show_lines = 7
            prev = '\n'.join(code[line-show_lines:line-1])
            cur_line = f'\033[31m{code[line-1]} <--- Here: {_ex}\033[0m'
            cont = '\n'.join(code[line+1:line+show_lines])
            code = f'...\n{prev}\n{cur_line}\n{cont}\n...'
            print(f'===== {file} Traceback =====\n{code}\n===== END =====')
            #print(f'============================== TWEAK ERROR {str(_ex.__class__).upper()} ==============================\n\nError in {file}:\n{code}\n\n{_ex}')

print('$JB Tweaks Loaded!')
