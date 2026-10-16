# encoding: utf-8
import json
import os
import sys
import tkinter as tk
from tkinter.messagebox import showerror
from data.lib.encrypting import *
from data.lib.utils2 import JsonObject

base_conf = json.load(open('./data/base_data.json', 'r'))
try:
    data_nc_addr = 'DATA.NC'
    data = open('./data/DATA.NC', 'r', encoding='utf-8').read()
except FileNotFoundError:
    data_nc_addr = base_conf['LOAD_NC']
    data = open(f'./data/{data_nc_addr}', 'r', encoding='utf-8').read()
try:
    print(decrypt(data, eval(base_conf['CC'])))
except Exception as e:
    print(f'damaged {e}')
d = ''
while d != 'exit':
    try:
        d = 'gui' #input('c: ')
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt')
        sys.exit()
    if d == 'y':
        datas = r"""#$#$SER[SETTINGS]
{'ADV_ATA': {}, 'USER_SETTINGS': {'TELEMETRY_ENABLED': 'True', 'SERVER': '192.168.88.24:8176', 'SEL_LOCALE': 'ru', 'FIRST_BOOT': 'False', 'THEME': 'hh', 'USERNAME': 'gg', 'BTAEML': 'True', 'BT_SERV': '192.168.88.24:8176', 'PASSWORD': 'cbd3cfb9b9f51bbbfbf08759e243f5b3519cbf6ecc219ee95fe7c667e32c0a8d', 'HASHING_METHOD': 'sha256', 'DEBUG_ACTIONS': {}, 'SCREEN_SETTINGS': [1.4, 1], 'EXC_DATA': {"<class 'UnicodeDecodeError'>:'charmap' codec can't decode byte 0x81 in position 1078536: character maps to <undefined>": 'Chat History failed to load. (Contains unsupported symbols).\nPlease delete file in ./plugins/btac/chatHistory.json'}}}
#$#$SER[LOADER_CONFIG]
CC_VERSIONS:msgr.py$%msgr_up.py

"""
        open('./data/DATA.NC', 'w', encoding='utf-8').write(encrypt(datas, eval(base_conf['CC'])))
    elif d == 'cc':
        base_conf['CC'] = str(generate_salt())
        json.dump(base_conf, JsonObject(open('./data/base_data.json', 'w')))
    elif d == 'pcc':
        print(base_conf['CC'])
    elif d == 'yc':
        open('./data/DATA.NC', 'w').write(encrypt(base_conf['DATA_NC_CLEARED'], eval(base_conf['CC'])))
    elif d == 'rnc':
        os.system('cls')
        try:
            print(decrypt(data, eval(base_conf['CC'])))
        except Exception as e:
            print(f'damaged {e}')
    elif d == 'gui':
        def data_nc_editor():
            def save():
                with open(f'./data/{data_nc_addr}', 'w', encoding='utf-8') as nc_file:
                    nc_file.write(encrypt(txt.get("0.0", tk.END), eval(cc)))
                open(f'./data/{data_nc_addr}', 'w', encoding='utf-8').write(encrypt(txt.get("0.0", tk.END), eval(base_conf['CC'])))

            def load_data_nc():
                txt.delete("0.0", tk.END)
                txt.insert("0.0", decrypt(open(f'./data/{data_nc_addr}', 'r', encoding='utf-8').read(), eval(cc)))

            def raw():
                txt.delete("0.0", tk.END)
                txt.insert("0.0", open(f'./data/{data_nc_addr}', 'r').read())

            def codec():
                txt.delete("0.0", tk.END)
                txt.insert("0.0", base_conf['CC'])
            try:
                cc = base_conf['CC']
                editor_win = tk.Tk()
                txt = tk.Text(editor_win)
                txt.grid(column=0, row=0, columnspan=4)
                tk.Button(editor_win, text='Save', command=save).grid(column=0, row=1)
                tk.Button(editor_win, text='Load', command=load_data_nc).grid(column=1, row=1)
                tk.Button(editor_win, text='raw', command=raw).grid(column=2, row=1)
                tk.Button(editor_win, text='codec', command=codec).grid(column=3, row=1)
                editor_win.mainloop()
            except Exception as editor_open_err:
                showerror('Error', f'Editor open error. {type(editor_open_err)}')


        data_nc_editor()
        exit()