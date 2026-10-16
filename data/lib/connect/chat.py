# downloaded from msgr-patches!

import json
import socket
from typing import Any
import os
import data.lib.utils
from data.lib.utils2 import JsonObject


class DctPlus(dict):
    """Advanced dict"""
    def __getitem__(self, item):
        if item not in self.keys():
            self.update({item: []})
            return []
        else:
            return super().__getitem__(item)

    def __setitem__(self, key, value):
        if key != '':
            super().__setitem__(key, value)


def print_adv(v):
    print(f'[{os.path.basename(__file__)}]{v}')

chat_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
online_list = []
cl = None
username_local = None
data.lib.utils.glb = globals()

if not os.path.exists('./data/chatHistory.json'):
    _msgs = []
    _private_msgs = DctPlus()
    loaded_msgs = []
    loaded_private_msgs = {}
try:
    datas = json.load(open('./data/chatHistory.json'))
except json.JSONDecodeError:
    datas = {}
except FileNotFoundError:
    with open('./data/chatHistory.json', 'w'):
        pass
    datas = {}



def msgs():
    """Returns copy of msgs variable"""
    return _msgs.copy()


def new_chat(name):
    """Creates chat with 'name'"""
    _private_msgs.update({name: []})


def private_msgs():
    """Returns copy of private_msgs variable"""
    try:
        return DctPlus(_private_msgs.copy())
    except NameError:
        return {}


def _auth():
    """Loads ChatHistory. Dont call it manually"""
    global _msgs, _private_msgs, loaded_msgs, loaded_private_msgs
    try:
        hist = json.load(open('./data/chatHistory.json'))[username_local]
        if hist == {}:
            hist = {'msgs': [], 'private_msgs': {}}
    except (json.JSONDecodeError, KeyError):
        hist = {'msgs': [], 'private_msgs': {}}
    _msgs = hist['msgs'].copy()
    _private_msgs = DctPlus(hist['private_msgs'].copy())
    loaded_msgs = hist['msgs'].copy()
    loaded_private_msgs = hist['private_msgs'].copy()


class Chat:
    def __init__(self, addr: str, port: int, username: str):
        """Main part of module. Chat client
        :param addr - address, like 127.0.0.1
        :param port - port, like 8080
        :param username - username"""
        global cl, username_local
        self.ip = (addr, port)
        cl = self
        username_local = username
        if username_local not in datas:
            datas[username_local] = {}
        _auth()

    def connect(self):
        """connects to server"""
        chat_sock.connect(self.ip)

    def send(self, _data: Any):
        """Sends Info on server"""
        if isinstance(_data, dict):
            if 'text' in _data:
                if 'to_cl' not in _data:
                    _msgs.append(f'You: {_data["text"]}')
                else:
                    if _data["to_cl"] not in _private_msgs:
                        _private_msgs.update({_data["to_cl"]: [f'You: {_data["text"]}']})
                    else:
                        _private_msgs[_data["to_cl"]].append(f'You: {_data["text"]}')
        self.backup()
        try:
            chat_sock.send(f'{_data}'.encode('utf-8'))
        except OSError:
            pass

    def async_recv(self, show_in_log=False):
        """Receives & updates info. Need to start by thread"""
        while True:
            global online_list
            try:
                recv = chat_sock.recv(1024).decode('utf-8')
            except (ConnectionError, OSError):
                recv = None
                break
            if show_in_log:
                print(f'recived: {recv}')
            try:
                recv_eval = eval(recv)
                if recv_eval['type'] == 'online_list':
                    online_list = recv_eval['answer']
            except (NameError, SyntaxError):
                print(f'Received MSG {recv}')
                if 'PRIVATE: ' not in recv:
                    _msgs.append(recv)
                if 'PRIVATE: ' in recv:
                    tmp = recv.replace('PRIVATE: ', '')
                    if tmp.split(': ')[0] not in _private_msgs:
                        _private_msgs.update({tmp.split(': ')[0]: [tmp.split(': ')[0] + ': ' + tmp.split(': ')[1]]})
                    else:
                        _private_msgs[tmp.split(': ')[0]].append(tmp.split(': ')[0] + ': ' + tmp.split(': ')[1])
                self.backup()
        return

    @staticmethod
    def shutdown(how):
        """Copy of chat_sock.shutdown. Shutdowns socket"""
        try:
            chat_sock.shutdown(how)
        except OSError:
            pass


    @staticmethod
    def close():
        """Copy if chat_sock.close. Closes connection"""
        chat_sock.close()

    @staticmethod
    def backup():
        """Backups chats in file"""
        backup_path = './data/chatHistory.json'
        with open(backup_path, 'w'):
            pass
        datas[username_local] = {'msgs': _msgs, 'private_msgs': _private_msgs}
        json.dump(datas, JsonObject(open(backup_path, 'w')))

    @staticmethod
    def msgs():
        """Copy of msgs()"""
        return msgs()

    @staticmethod
    def private_msgs():
        """Copy of private_msgs()"""
        return private_msgs()

    @staticmethod
    def online_list():
        """Copy of online_list.copy()"""
        return online_list.copy()


