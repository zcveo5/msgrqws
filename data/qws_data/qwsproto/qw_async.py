import asyncio
import json
import random

from .qwproto2 import QWProtoCommunicator


async def _wait_for_sync(func, *args, **kwargs):
    _task = asyncio.to_thread(func, *args, **kwargs)
    res = await _task
    return res


class AsyncQWProto:
    def __init__(self, addr, username, password, output=False):
        self._addr = addr
        self._sync = QWProtoCommunicator(addr, username, password, output)
        self._sync.connect()
        self._sync.auth()

    @property
    def username(self):
        return self._sync.username

    def disconnect(self):
        self._sync.close()

    async def ask(self, data):
        data['req_id'] = random.randint(100000, 999999)
        self._sync.send(data)
        res = await _wait_for_sync(self._sync.wait_for, data['req_id'], 10)
        return res

    async def _ask_type(self, _type, data=None):
        _dt = {'type': _type}

        if data:
            _dt.update(data)

        res = await self.ask(_dt)
        return res

    async def remove_auth(self):
        res = await self._ask_type('remove_auth')
        return res

    async def client_hello(self, can):
        res = await self._ask_type('client_hello', {'can': can})
        return res

    async def register(self, invite, username, password):
        res = await self._ask_type('register', {'invite': invite, 'username': username, 'password': password})
        return res

    async def register_email(self, email):
        res = await self._ask_type('register_email', {'email': email})
        return res

    async def register_ecode(self, code):
        res = await self._ask_type('register_ecode', {'code': code})
        return res

    async def auth(self, username, token, password):
        res = await self._ask_type('auth', {'username': username, 'token': token, 'password': password})
        return res

    async def get_server_creator_data(self, pswd):
        res = await self._ask_type('get_server_creator_data', {'pswd': pswd})
        return res

    async def server_do(self, name, desc, pswd, do):
        res = await self._ask_type('server_do', {'name': name, 'desc': desc, 'pswd': pswd, 'do': do})
        return res

    async def msg(self, _from, to_cl, text, time):
        res = await self._ask_type('msg', {'from': _from, 'to_cl': to_cl, 'text': text, 'time': time})
        return res

    async def create_chat(self, is_public, is_channel, name, users, public_id):
        res = await self._ask_type('create_chat',
                                   {'is_public': is_public, 'is_channel': is_channel, 'name': name, 'users': users,
                                    'public_id': public_id})
        return res

    async def get_contacts(self):
        res = await self._ask_type('get_contacts')
        return res

    async def get_chat_hist(self):
        res = await self._ask_type('get_chat_hist')
        return json.loads(res['h'])

    async def get_chat_data(self, c, lazy_from, lazy_to):
        res = await self._ask_type('get_chat_data', {'c': c, 'lazy_from': lazy_from, 'lazy_to': lazy_to})
        return res

    async def queue_finish(self):
        res = await self._ask_type('queue_finish')
        return res

    async def add_to_contacts(self, u):
        res = await self._ask_type('add_to_contacts', {'u': u})
        return res

    async def join(self, u):
        res = await self._ask_type('join', {'u': u})
        return res

    async def quit(self, u):
        res = await self._ask_type('quit', {'u': u})
        return res

    async def need_update_hist(self):
        res = await self._ask_type('need_update_hist')
        return res

    async def get_public_chats_all(self):
        res = await self._ask_type('get_public_chats_all')
        return res

    async def edit_data(self, key, value):
        res = await self._ask_type('edit_data', {'key': key, 'value': value})
        return res

    async def delete_chat(self, c):
        res = await self._ask_type('delete_chat', {'c': c})
        return res

    async def create_direct(self, u):
        res = await self._ask_type('create_direct', {'u': u})
        return res

    async def get_queue(self):
        res = await self._ask_type('get_queue')
        return res

    async def chat_manage_get_my_actions(self, chat):
        res = await self._ask_type('chat_manage_get_my_actions', {'chat': chat})
        return res

    async def add_users(self, c, chat):
        res = await self._ask_type('add_users', {'c': c, 'chat': chat})
        return res

    async def delete_user(self, delete_user, chat):
        res = await self._ask_type('delete_user', {'delete_user': delete_user, 'chat': chat})
        return res

    async def add_admin(self, chat, add_admin):
        res = await self._ask_type('add_admin', {'chat': chat, 'add_admin': add_admin})
        return res

    async def remove_admin(self, remove_admin, chat):
        res = await self._ask_type('remove_admin', {'remove_admin': remove_admin, 'chat': chat})
        return res