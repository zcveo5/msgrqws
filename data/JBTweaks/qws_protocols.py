import ast
import json
import os.path
import queue
import threading
import time
import tkinter.messagebox
import sys
try:
    from data.qws_data.qwsproto import *
except ModuleNotFoundError as _ex:
    if _ex.name != 'websocket':
        tkinter.messagebox.showwarning('Error', f'Failed to load data.qws_data\n\nDebug info:\n{sys.path}\n{os.path.isdir('./data/qws_data/qwsproto')}')
        exit(1)
    else:
        tkinter.messagebox.showwarning('Error',
                                       f'websocket-client library not found')
        exit(1)


def chat_win_private_ref_custom(to):
    try:
        globals()['main'].his['chat_window_private'].tk.delete("0.0", 'end')
        scr = len(to) - 24 -  globals()['main']
        scr_to = len(to) -  globals()['main']
        if scr < 0:
            scr = 0
        if scr_to < 25:
            scr_to = 24
        _to = to[scr:scr_to]
        globals()['main'].his['chat_window_private'].tk.insert('end', '\n'.join(_to))
    except (KeyError, tkinter.TclError):
        pass


def get_chat_hist():
    globals()['QWS_queue_updating'] = False
    client = globals()['QWSServer']
    _need = client.communicate({'type': 'need_update_hist'})
    if _need is not None:
        if _need['ans'] == 'True':
            _a = client.recv_split_request({'type': 'get_chat_hist'})
        else:
            _a = globals()['QWSChats']
        globals()['QWS_queue_updating'] = True
        return _a
    globals()['QWS_queue_updating'] = True
    return {}


def wrapper_gda(*args, **kwargs):
    print('[warn] passed GDA!')
    return {'answer': ''}


def update_personal_conf_passer(*args, **kwargs):
    print('[warn] passed UPC!')
    raise KeyError('UPCP: QWS PROTO')


def _connect():
    global connected, con_ex
    try:
        sock.recreate_sock()
        print('connect')
        sock.connect()
        print('auth')
        sock.auth()
        connected = True
    except Exception as _ex:
        con_ex = _ex
        connected = None

connected = False
con_ex = None

def connect():
    threading.Thread(target=_connect, name='QWSConnect', daemon=True).start()
    root.his['load_lbl']['text'] = 'QWS Connecting...'
    root.update()
    while not connected:
        if connected is None:
            if tkinter.messagebox.askretrycancel('qwsProto',
                                                 f'failed to connect to the QWS Server:\n{con_ex.__class__.__name__}: {con_ex}\n\naddr {datas} ws:// forget?\n\nError 1x1 spec\nAccount creating only on web\nlogin creds used from data.nc!'):
                threading.Thread(target=_connect, name='QWSConnect', daemon=True).start()
            else:
                exit()
        time.sleep(0.1)
        root.update()
    root.his['load_lbl']['text'] = ''
    print('fin')



def download_and_load(_chat):
    print(f'load_chat: downloading {_chat} data')
    a = sock.recv_split_request({'type': 'get_chat_data', 'c': _chat})
    print(f'load_chat: downloaded {_chat}')
    return a


def send_message_wrapper(*args, **kwargs):
    send_message_mod(globals()['send_entry'].get("0.0", 'end'))


def send_message_mod(text):
    _msg = {'type': 'msg',
           'text': text,
           'to_cl': globals()['chat_selected'],
           'from': globals()['user_local_settings']['USER_SETTINGS']['USERNAME'],
           'time': '00:00:00'}
    globals()['QWSChats'][_msg['to_cl']].append(f'{_msg.get('from', 'NoAuthor')}: {_msg['text']}')
    _sock = globals()['QWSServer']
    _sock.send(msg)



def get_queue():
    queue_updating = globals()['QWS_queue_updating']
    client: QWProtoCommunicator = globals()['QWSServer']
    if queue_updating:
        try:
            i = client.queue.get_nowait()
        except queue.Empty:
            i = {'type': 'pass'}

        if i['type'] == 'new_chat':
            globals()['QWSChats'][i['link']] = i
        elif i['type'] == 'remove_chat':
            globals()['QWSChats'].pop(i['link'])
        elif i['type'] == 'msg':
            _copy = i.copy()
            if i['to_cl'] not in globals()['QWSChats']:
                globals()['QWSChats'][i['to_cl']] = client.recv_split_request({'type': 'get_chat_data', 'c': 'm_qws_notifications'})
            globals()['QWSChats'][i['to_cl']].append(f'{i.get('from', 'NoAuthor')}: {i['text']}')
        elif i['type'] == 'force_chat_hist_update':
            globals()['QWSChats'] = get_chat_hist()

if 'QWS_SERVER' not in globals()['user_local_settings']['USER_SETTINGS']:
    tkinter.messagebox.showwarning('Error', 'QWS_SERVER not defined in data.nc')
    print(f'exiting {threading.enumerate()}')
    main.destroy()
    exit()

datas = globals()['user_local_settings']['USER_SETTINGS']['QWS_SERVER']
globals()['QWSChats'] = {}
sock = globals()['QWSServer'] = QWProtoCommunicator(datas,
                                                    globals()['user_local_settings']['USER_SETTINGS']['USERNAME'],
                                                    globals()['user_local_settings']['USER_SETTINGS']['PASSWORD'],
                                                    output=True)

connect()

print('refresh chat hist')
dct = json.loads(get_chat_hist()['h'])
dct_update = {}
for link, data in dct.items():
    if 'do_load' not in data:
        dct_update[link] = data
    else:
        dct_update[link] = download_and_load(link)
dct = dct_update
dct_formated = {}
for link, chat_data in dct.items():
    print(f'{link}: {chat_data}')
    dct_formated[link] = []
    for msg in chat_data['msgs']:
        if isinstance(msg, dict):
            dct_formated[link].append(f'{msg.get('from', 'NoAuthor')}: {msg.get('text', 'NoText')}')

globals()['QWSChats'] = dct_formated

globals()['count_unread'] = lambda: None
globals()['chat_lib'].private_msgs = lambda: globals()['QWSChats']
globals()['chat_lib'].Chat.connect = lambda *_: None
globals()['auth'].User.get_data = wrapper_gda
globals()['auth'].update_personal_conf = update_personal_conf_passer
globals()['auth'].connect = lambda *_: None
globals()['send_message'] = send_message_wrapper

globals()['main'].tk_thread(get_queue, 200)

