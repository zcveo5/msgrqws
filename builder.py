import os
import random
import shutil

def get_files() -> list:
    _d = open('./launcher.pyw', 'r').read()
    tmp = _d[_d.find('files = [')::]
    tmp = tmp[tmp.find('[')::]
    return eval(tmp[:tmp.find(']')] + ']')

def get_libs() -> list:
    _d = open('./launcher.pyw', 'r').read()
    tmp = _d[_d.find('libs = [')::]
    tmp = tmp[tmp.find('[')::]
    return eval(tmp[:tmp.find(']')] + ']') + ['./data/lib/fs_store.py']

def build(dirn = f'build{random.randint(1000000, 9999999)}'):
    print(f'[*] Build in {dirn}')
    print(f'[*] We are in {os.getcwd()}')

    os.makedirs(dirn, exist_ok=True)
    file_list = get_files() + get_libs() + ['./launcher.pyw']
    for file in file_list:
        file = file.replace('./', '')
        path = './' + dirn + '/' + file
        file = './' + file
        if os.path.isfile(file):
            print(f'[*][File] Copying {file} into {path}')
            shutil.copy2(file, path)
        else:
            print(f'[*][Fold] Creating {path} folder')
            os.makedirs(path, exist_ok=True)
    print('[*] Completed!')
    return dirn

if __name__ == '__main__':
    build()