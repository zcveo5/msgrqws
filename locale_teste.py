import json
import os
import sys
import traceback
from json import JSONDecodeError


def locale_finder(unique=False):
    def find_str_contains(data):
        _str_c = 0
        for _str in d.split('\n'):
            if data in _str:
                return True, _str_c
            _str_c += 1
        return False, _str_c

    d = open('./msgr.py', 'r', errors='replace').read()
    d_spl = d.split('locale[')
    ans = {}
    for raw_str in d_spl:
        obj = raw_str[:50:]
        obj_ready = ''
        for symbol in obj:
            if symbol == ']':
                obj_ready = obj_ready.replace("'", '').replace('"', '')
                if not unique or obj_ready not in ans:
                    ans.update({obj_ready: find_str_contains(obj_ready)})
                break
            obj_ready += symbol
    return ans

def decode_locale(lang):
    if isinstance(lang, dict):
        return lang
    try:
        return json.load(open(f'./data/locale/{lang}/locale.cfg', 'r')), 'JSON'
    except UnicodeError:
        try:
            return json.load(open(f'./data/locale/{lang}/locale.cfg', 'r', encoding='windows-1251')), 'JSON'
        except (UnicodeError, JSONDecodeError):
            pass
    except JSONDecodeError:
        pass
    try:
        _d = open(f'./data/locale/{lang}/locale.cfg', 'r').read()
    except UnicodeError:
        try:
            _d = open(f'./data/locale/{lang}/locale.cfg', 'r', encoding='windows-1251').read()
        except UnicodeError:
            raise TypeError('Unk Enc')
    data = {}
    for elem in _d.split('\n'):
        spl = elem.split(':')
        if len(spl) == 2:
            data.update({spl[0]: spl[1]})
    return data, 'LEGACY'


print('debug thing for msgr 0.3.4')
cmd = input('mode: ')
if cmd == 'locale-test':
    lng = input('locale to find: ')
    in_code_used = locale_finder(True)
    lc = decode_locale(lng)
    locale_keys = lc[0].keys()
    used_not_exists = []
    for i in in_code_used:
        if i not in locale_keys:
            used_not_exists.append(i)

    raz = 0
    for i in locale_keys:
        if i in in_code_used:
            raz += 1
    raz = len(in_code_used) - raz

    print(f'===== LOCALE {lng.upper()} =====\nFormat: {lc[1]}')

    def get(item, from_d):
        if item in from_d:
            return f'found on str {from_d[item][1]}'
        else:
            return 'not found'

    def get_sec(item, from_d):
        if item < len(from_d):
            return list(from_d)[item]
        else:
            return 'not exists'


    print('-' * 20)
    for index in range(len(locale_keys) + raz):
        i = get_sec(index, locale_keys)
        _d = 'not '
        if i in in_code_used.keys():
            _d = 'used'
        elif i == 'not exists':
            _d = 'add '
            i = used_not_exists[index - len(locale_keys)]
        sp = ''
        for _ in range(30 - len(i)):
            sp += ' '
        tmp = get(i, in_code_used)
        print(f'{i}{sp}{_d}{" "*10}{tmp}')
    print('-'*20)
    print('recommended to delete keys:\n')
    c = 0
    for i in locale_keys:
        if i not in in_code_used.keys():
            c += 1
            print(i)
    print(f'\n   / {c} elements')
    print('-' * 20)
    print('recommended to add keys:\n')
    c = 0
    for i in in_code_used.keys():
        if i not in locale_keys:
            c += 1
            print(i)
    print(f'\n   / {c} elements')
elif cmd == 'locale-keys':
    in_code_used = locale_finder(True)
    print('\n'.join(in_code_used))
elif cmd == 'find-configs':
    configs = []
    for root, folders, files in os.walk('./'):
        if '.venv' not in root:
            for file in files:
                if len(file.split('.')) == 1:
                    print(f'[!] No extension for {file}')
                elif file.split('.')[1] in ['json', 'conf', 'cfg']:
                    print(f'[*] Found {file}')
                    configs.append(os.path.join(root, file).replace(r'\\'[1::], '/').replace('./', ''))
                else:
                    print(f'[!] Invalid extension for {file}')
    print(' '*31+'PATH'+' '*35+'EXT'+' '*7+'CONV')
    for conf in configs:
        ext = os.path.basename(conf).split('.')[1]
        if ext != 'json':
            conv = True
        else:
            conv = False
        print(conf + ' ' * (70 - len(conf)) + ext + ' '*(10-len(ext)) + str(conv))
elif cmd == 'convert-locale':
    lng = input('Locale name: ')
    d = open(f'./data/locale/{lng}/locale.cfg', 'rb')
    try:
        lc = json.load(d)
        print('Locale already formated as json')
    except (JSONDecodeError, UnicodeError):
        print('Formating locale...')
        lc_formated = decode_locale(lng)[0]
        print('Writing')
        with open(f'./data/locale/{lng}/locale_legacy.cfg', 'wb') as fl:
            fl.write(d.read())
        try:
            json.dump(lc_formated, open(f'./data/locale/{lng}/locale.cfg', 'w'))
        except TypeError:
            print(traceback.format_exc())
            print(lc_formated)
        print('Completed!')
elif cmd == 'count-strings':
    files_py = []
    all_c = 0
    for root, folders, files in os.walk('./'):
        if '.venv' not in root:
            for file in files:
                if len(file.split('.')) == 1:
                    print(f'[!] No extension for {file}')
                elif file.split('.')[1] in ['py']:
                    print(f'[*] Found {file}')
                    files_py.append(os.path.join(root, file).replace(r'\\'[1::], '/').replace('./', ''))
                else:
                    print(f'[!] Invalid extension for {file}')

    for _file in files_py:
        c = len(open(_file, 'r', errors='replace').read().split('\n'))
        all_c += c
        print(f'{_file}{' '*(70-len(_file))}{c}')

    print(f'\n{' '*10} \ {all_c}')
elif cmd == 'get-sargv':
    fl = open(input('name: '), encoding='utf-8').read()
    for i in fl.split('\n'):
        if ' in sys.argv' in i and 'for' not in i:
            _a = i[i.find("'")+1:i.rfind("'")]
            print(f'{_a}')

else:
    print('Unknown command')