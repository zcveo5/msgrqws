import ast
import json
import os
import socket
import threading
import traceback
from threading import Thread
from typing import Literal

server_work = True

clients = {}
send_queue = {}
# clients: {addr: {username: None | str, class: ClientClass}}
data_raw = json.load(open('./data.json', 'r'))

class Client:
    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.ip = self.sock.getpeername()
        self.alive = True
        print(f'[*] Client Connected {self.ip}')

    def handle(self):
        data_user = data_raw['users']
        last_rcv = ''

        c = 0
        while server_work and self.alive:
            if not self.alive:
                break
            try:
                message = self.sock.recv(1024)
            except ConnectionResetError:
                break
            if message == b'':
                break
            try:
                msg_eval = ast.literal_eval(message.decode('utf-8'))
            except Exception as _ex:
                print(_ex)

            if msg_eval != last_rcv:
                if c > 0:
                    adv = '[A]'
                    if 'text' in last_rcv or 'action_for_chat_server' in last_rcv:
                        adv = '[C]'
                    print(f'[*]{adv} {last_rcv} Repeated x{c}')
                c = 0
                adv = '[A]'
                if 'text' in msg_eval or 'action_for_chat_server' in msg_eval:
                    adv = '[C]'
                print(f'[*]{adv} Received: {msg_eval}')
            else:
                c += 1

            last_rcv = msg_eval

            if msg_eval != last_rcv:
                print(f'Received {msg_eval}')

            if 'text' in msg_eval or 'action_for_chat_server' in msg_eval:
                name = f'{self.ip[0]}:{self.ip[1]}'

                if 'action_for_chat_server' not in msg_eval:
                    if msg_eval.get('_show_ip') == 'False':
                        name = msg_eval.get('name', name)

                    if msg_eval.get('to') == 'public':
                        for client in clients.values():
                            if client['class'].sock != self.sock:
                                client['class'].sock.send(f"{name}: {msg_eval['text']}".encode('utf-8'))

                    elif msg_eval.get('to') == 'private':
                        to_cl = msg_eval.get('to_cl')
                        sender_name = name

                        try:
                            recipient_sock = get_client_data('username', to_cl)['class'].sock
                            recipient_sock.send(f"PRIVATE: {sender_name}: {msg_eval['text']}".encode('utf-8'))
                        except Exception:
                            print('[*] adding to queue (recipient not found)')
                            if to_cl not in send_queue:
                                send_queue[to_cl] = []
                            send_queue[to_cl].append(f"PRIVATE: {sender_name}: {msg_eval['text']}")

                else:
                    action = msg_eval.get('action_for_chat_server')
                    username = msg_eval.get('username')
                    user_client = get_client_data('class', self)

                    if action == 'MyUSER' and username:
                        if user_client:
                            clients[user_client['class'].ip]['username'] = username

                    elif action == 'ReadyToQ' and username in send_queue:
                        for msg in send_queue[username]:
                            self.sock.send(msg.encode('utf-8'))
                        send_queue.pop(username)

                    elif action == 'OnlineList':
                        online_users = [u for u in (client.get('username') for client in clients.values()) if u]
                        self.sock.send(
                            str({'type': 'online_list', 'answer': ['Online:'] + online_users}).encode('utf-8'))
            else:
                data_recv = msg_eval
                print(data_recv.__class__)
                ans = {}
                if 'username' in data_recv and 'password' in data_recv:
                    if data_recv['username'] not in data_user:
                        data_user.update({data_recv['username']: {'password': data_recv['password'], 'global_block': 'False'}})
                        ans = {'status': 'ok', 'answer': data_user[data_recv['username']]}
                        print(f"[*] New user in database {data_recv['username']}")
                    else:
                        if data_user[data_recv['username']]['global_block'] == 'True':
                            ans = {'status': 'ok', 'answer': 'blocked'}
                            self.alive = False
                        if data_user[data_recv['username']]['password'] != data_recv['password']:
                            ans = {'status': 'ok', 'answer': 'incorrect password'}
                            self.alive = False
                if 'action' in data_recv:
                    if data_recv['action'].split(':')[0] == 'update_data':
                        if data_recv['action'].split(':')[1] not in data_user[data_recv['username']]:
                            if data_recv['action'].split(':')[1] != 'global_block':
                                data_user[data_recv['username']].update(
                                    {data_recv['action'].split(':')[1]: data_recv['action'].split(':')[2]})
                        else:
                            if data_recv['action'].split(':')[1] in ['_show_ip']:
                                data_user[data_recv['username']][data_recv['action'].split(':')[1]] = data_recv['action'].split(':')[2]
                    if data_recv['action'].split(':')[0] == '_in_db':
                        ans = {'status': 'ok', 'answer': data_recv['username'] in data_user}
                    if data_recv['action'] == 'modlist':
                        mods = list(data_raw["modlist"].keys())
                        while len(str(mods)) > 900:
                            mods.pop(len(mods) - 1)
                        ans = {'status': 'ok', 'answer': f'{mods}'}
                    if data_recv['action'].split(':')[0] == 'get_mod':
                        ans = {'status': 'ok', 'answer': f'{data_raw["modlist"][data_recv['action'].split(':')[1]]}'}
                    if data_recv['action'] == 'upload_mod':
                        data_raw["modlist"].update({data_recv['MOD_NAME']: data_recv['PLUG_CODE']})
                        ans = {'status': 'ok', 'answer': 'uploaded'}
                    if data_recv['action'] == 'update':
                        ans = {'status': 'ok', 'answer': f"{open('./msgr.py', 'r').read()}"}
                    if data_recv['action'] == 'my_ip':
                        ans = {'status': 'ok', 'answer': self.ip}
                if ans == {}:
                    ans = {'status': 'ok', 'answer': data_user[data_recv['username']]}

                self.sock.send(f'{ans}'.encode('utf-8'))
                json.dump(data_raw, open('./data.json', 'w'))


        print(f'[*] Finishing connection with {self.ip}')
        clients.pop(self.ip)
        print(f'[*] {self.ip} thread finished')
        return


def get_client_data(_t: Literal['addr', 'username', 'class'], _o: str | Client):
    for addr, cl_data in clients.items():
        if _t == 'addr' and addr == _o:
            return cl_data
        elif _t == 'username' and cl_data['username'] == _o:
            return cl_data
        elif _t == 'class' and cl_data['class'] == _o:
            return cl_data
    return None



def start_server():
    global server_work
    server_work = True
    data = json.load(open("./conf.json", 'r'))
    host = data['HOST']
    port = data['PORT_CHAT']

    print(f'[*] starting server at {host}:{port}')

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((host, port))
    except OSError as _ex:
        print(_ex)
        return None

    server.listen(5)

    print(f'[*] Started server on {host}:{port}')

    def accept_wrapper():
        while server_work:
            try:
                sock, addr = server.accept()
            except KeyboardInterrupt:
                print('[!] KeyboardInterrupt')
                break
            except OSError:
                break

            clients.update({addr: {'username': None, 'class': Client(sock)}})
            Thread(target=clients[addr]['class'].handle).start()
        print('[*] Accept thread finished')

    Thread(target=accept_wrapper).start()
    cmd = ''
    while cmd != 'exit':
        cmd = input()
    return None



if __name__ == '__main__':
    print(r' - \ MSGR QW Server Ver.2 / - ')
    if not os.path.exists('./data.json'):
        print('[*] Creating data')
        with open('./data.json', 'w') as fl:
            fl.write('{}')
    start_server()
    server_work = False
    for thread in threading.enumerate():
        if thread != threading.current_thread():
            print(f'[*] Stopping {thread}...')
            thread.join()
    print('[*] Finished!')
    input('Press enter to close...')