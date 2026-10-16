import ast
import json
import random
import threading
import time
import traceback
from queue import Queue
import websocket
from ._logging import get_logger


def refresh_log():
    pass


VERSION = 'QProto1'
CAN = 'QWProto1;AsyncQueue;TCrypt'


class Event:
    def __init__(self):
        self._e = []

    def __add__(self, other):
        if not callable(other):
            raise ValueError(f'not callable {other}')
        self._e += other

    def __call__(self, *args, **kwargs):
        [_f() for _f in self._e]


#class Transport:
#    def __init__(self, sock):
#        self.is_tcp = isinstance(sock, socket.socket)
#        self.sock = sock
#
#    def send(self, data):
#        if self.is_tcp:
#            self.sock.send(f'{data}')
#        else:
#            sock: websocket.WebSocket = self.sock
#
#            sock.send(json.dumps(data))
#
#    def recv(self):
#        if self.is_tcp:
#            return self.sock.recv(1024)
#        else:
#            sock: websocket.WebSocket = self.sock
#            return sock.recv()


class Server:
    """вспомогательный класс для сообщения между сервером и клиентом"""

    def __init__(self, host, port, username, password, default_waiting_actions=None, show_error=None, use_rr_mode=True,
                 enable_debug_log=False):
        if default_waiting_actions is None:
            default_waiting_actions = lambda: None
        if default_waiting_actions is not tuple:
            default_waiting_actions = (default_waiting_actions,)

        sock_log = get_logger(__name__)
        self._debug_state = enable_debug_log
        if enable_debug_log:
            self.debug = sock_log.debug
            self.info = sock_log.info
            self.warn = sock_log.warning
            self.error = sock_log.error
        else:
            self.debug = lambda s: None
            self.info =   lambda s: None
            self.warn =   lambda s: None
            self.error =  lambda s: None

        if show_error is None:
            show_error = self.error

        self.ip = f'wss://msgrqws.ru/ws'
        self.sock = websocket.WebSocket()
        self.dwa = default_waiting_actions
        self._request_response_mode = use_rr_mode
        self._show_error = show_error
        self._work = False
        self._work_async_recv = True
        self._async_recv_th = None
        self._async_recv_fail = False
        self.queue = Queue()

        self.on_connection_reset: Event = Event()

        self.usr = username
        self.passw = password

        self.username = username
        self.password = password

        self._codec = None  # ключ шифрования (модуль crypt)
        self.req_id = 0  # Счетчик идентификаторов запросов
        self._lock = threading.Lock()  # Блокировка для безопасного увеличения счетчика

        self._unk_req = {}

    def recreate_sock(self):
        #self._work = False
        #self.warn('recreate sock')
        #self.sock.close()
        #self.sock = websocket.WebSocket()
        pass

    def close(self):
        self.sock.close()

    def connect(self):
        """Подключение к серверу"""
        self._work = True
        self._work_async_recv = True
        self._codec = None
        self.sock.connect(self.ip)
        # self.sock.send(f'ConnectionKey$:${self._codec}'.encode('utf-8'))
        self.info('connected')
        if not self._request_response_mode:
            self._async_recv_th = threading.Thread(target=self.async_recv, daemon=True,
                                                   name=f'ThreadReceive{self.ip[0]}:{self.ip[1]}')
            self._async_recv_th.start()

    def stop_threads(self):
        self._async_recv_th.join()

    def auth(self):
        while 'server_hello' not in self._unk_req:
            time.sleep(0.1)

        server_hello = self._unk_req.pop('server_hello')
        self.debug(f'Server hello: {server_hello}')

        client_can = server_hello['can'].split(';')
        for act in CAN.split(';'):
            if act not in client_can:
                self.close()
                raise Exception(f'ClientHelloUnsupported:{act}')

        self.debug('client hello')

        self.send({'type': 'client_hello', 'can': CAN})

        while 'client_hello_ans' not in self._unk_req:
            time.sleep(0.1)

        supported = self._unk_req.pop('client_hello_ans')
        if 'desc' in supported:
            self.close()
            raise Exception(supported['desc'])

        self.debug(f'server hello: {supported}')

        auth_req = {'username': self.usr, 'password': self.passw, 'type': 'auth'}

        self.debug(f'Login query: {auth_req}, sending')
        login_result = self.communicate(auth_req)  # отправляет запрос на логин
        if login_result is None or login_result['status'] != 'ok':
            self._work = False
            self._work_async_recv = False
            self.recreate_sock()
            self.debug('raising exception, login failed')
            raise Exception(f'Login failed: {login_result if 'desc' not in login_result else login_result['desc']}')
        self.info(f'Login result: {login_result}')
        return login_result

    def async_recv(self, limit=1024):
        work = True
        self.info('async-recv: start')
        while work:
            _response = ''
            if not self._work_async_recv:
                break
            try:
                _response = self._recv(limit=limit)
                if _response == '':
                    raise ConnectionResetError('Reset')
                self.debug(f'async-recv: tp: {type(_response)} recv {_response}')
                if isinstance(_response, str):
                    self.warn('async-recv: string received')
                    continue

                if 'type' not in _response:
                    _response['type'] = ''
                if _response['type'] == 'queue':
                    if _response['q'] != '':
                        self.queue.put_nowait(_response['q'])
                elif _response['req_id'] == 'ServerSideErrorDetails':
                    self.error(f'async-recv: ServerSide Error:\n{_response['err']}')
                    self._show_error(_response['err'])
                    raise Exception('ServerSideError')
                elif _response['req_id'] != 'ServerSideErrorDetails':
                    self._unk_req[_response['req_id']] = _response
                else:
                    self.warn(f'async-recv: invalid response: {_response}')
            except ConnectionResetError:
                self.warn('connection lost')
                self.close()
                self.recreate_sock()
                self.on_connection_reset()
                return
            except Exception as e:
                self.error(f'async-recv error: {e.__class__.__name__}: {e} at #{_response}#\n\n{''.join(traceback.format_exception(e))}')
                work = False
                self._work = False
                if isinstance(_response, dict):
                    k = _response.get('req_id', 'no-id')
                else:
                    k = _response
                self._async_recv_fail = f'parsing {k} {e.__class__.__name__}: {e}'
                break
        else:
            self.info('async-recv: loop end')

    def send(self, d):
        """шифрует и отправляет запрос"""
        if not self._work:
            self.error('Send: _work false')
            raise ConnectionError('_work False')
        self.debug(f'Send: {d}')
        self.sock.send(str(d)) # SSL
        return None

    def _recv(self, limit=1024) -> str | None | dict:
        """расшифровывает ответ сервера и пытается конвертировать в словарь"""
        if not self._work:
            self.error('Recv: _work false')
            raise ConnectionError('_work False')
        _no_decrypt = self.sock.recv()
        self.debug(f'no decrypt recv: {_no_decrypt}')
        _no_dct = _no_decrypt # crypt.decrypt(_no_decrypt, self._codec) | SSL now using
        try:
            return ast.literal_eval(_no_dct)
        except (SyntaxError, ValueError):
            return json.loads(_no_dct)

    def communicate(self, send_data, limit=1024, waiting_action=None, timeout=15) -> dict | None:
        """система запрос - ответ с использованием ID запросов"""
        with self._lock:
            current_id = self.req_id
            self.req_id += 1

        self.info(f'ServerCom{current_id}: Started')

        if not callable(waiting_action) and waiting_action is not None:
            self.warn(f'ServerCom{current_id}: waiting_action ({waiting_action}) not callable')

        # Добавляем ID к данным запроса
        if isinstance(send_data, dict):
            send_data_with_id = send_data.copy()
            send_data_with_id['req_id'] = current_id
        else:
            send_data_with_id = {'req_id': current_id, 'msg': send_data}

        ans = None
        exc = None

        def wrp(_s, _l):
            nonlocal ans, exc
            bad_ans_c = 0
            self.debug(f'ServerCom{current_id}: sending {_s}')
            try:
                self.send(_s)
            except (ConnectionResetError, OSError):
                self.error('Connection with server has been reset')
                ans = {}
            while ans is None and self._work:
                if bad_ans_c > 10:
                    break
                try:
                    if current_id in self._unk_req:
                        ans = self._unk_req.pop(current_id)
                        self.debug(f'ServerCom{current_id}: answer is {ans}')
                        break

                    if self._request_response_mode:
                        response = self._recv(_l)
                        self.debug(f'ServerCom{current_id}: received {response}')
                        if isinstance(response, str):
                            response = {'msg': response}
                        if isinstance(response, dict) and response.get('req_id') == current_id:
                            self.debug(f'ServerCom{current_id}: answer is: {response}')
                            ans = response
                            break
                        else:
                            other_id = response.get('req_id', -1)
                            self._unk_req[other_id] = response
                            bad_ans_c += 1
                    time.sleep(0.1)
                except Exception as _send_ex:
                    exc = _send_ex
                    break
            else:
                if self._async_recv_fail:
                    raise Exception(self._async_recv_fail)
                else:
                    raise Exception('Unknown Error')

        com_th = threading.Thread(target=wrp, args=(send_data_with_id, limit), daemon=True,
                                  name=f'Communicate{current_id}recvWrp')
        com_th.start()
        _timeout = 0
        while ans is None:
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                self.error(f'ServerCom{current_id}: KeyboardInterrupt at waiting response')
            if waiting_action is not None and callable(waiting_action):
                waiting_action()
            for i in self.dwa:
                if callable(i):
                    i()
                else:
                    self.warn(f'ServerCom{current_id}: {i} waiting action not callable')
            _timeout += 0.01
            if _timeout >= timeout:
                break
        if ans is None:
            self.debug(f'ServerCom{current_id}: timed out')

            def join_w():
                com_th.join(timeout=1.0)
                self.debug(f'ServerCom{current_id}: thread closed')

            threading.Thread(target=join_w, daemon=True).start()
        self.info(f'ServerCom{current_id}: completed')
        if exc is not None:
            raise exc
        return ans

    def get_unknown_request(self, req_id):
        """Получить сохраненный ответ по ID запроса"""
        a = None
        while a is None:
            a = self._unk_req.pop(req_id, None)
        return a

    def recv_split_request(self, start_req):
        self.debug(f'ssr {start_req['type']}: started')
        with self._lock:
            current_id = self.req_id
            self.req_id = random.randint(1000000000, 9999999999)
        buffer = []
        start_req.update({'req_id': current_id})
        self.send(start_req)
        while '!!$%&END' not in buffer:
            for i in self.dwa:
                if not callable(i):
                    self.warn(f'ssr {start_req['type']}: w_a {i} not callable')
                else:
                    i()
            if self._request_response_mode:
                part = self._recv()
            else:
                part = self.get_unknown_request(current_id)
            self.debug(f'ssr {start_req["type"]}: {part}')
            part = part['h']
            if part is None:
                break
            buffer.append(part)
            current_id += 1
            time.sleep(0.1)
        string_buffer = ''
        for _i in buffer[0:-1]:
            string_buffer += str(_i)
        string_buffer = string_buffer
        self.debug(f'ssr {start_req["type"]}: result {string_buffer.__class__}')
        if isinstance(string_buffer, dict):
            return string_buffer
        try:
            return ast.literal_eval(string_buffer)
        except SyntaxError:
            self.debug(f'ssr {start_req['type']}: SyntaxError at decode result')
            return string_buffer
