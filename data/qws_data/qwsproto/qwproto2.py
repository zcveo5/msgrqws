import json
import sys
import time
from .qwproto1 import Server


VERSION = 'QWProto2'
CAN = 'QWProto1;AsyncQueue;TCrypt'



class QWProtoCommunicator(Server):
    def __init__(self, addr, username, password, output=False):
        super().__init__(
            addr,
            None,
            username,
            password,
            show_error=self._sse,
            use_rr_mode=False,
            enable_debug_log=output
        )
        self.ip = addr

    def _sse(self, err):
        exc = Exception(f'Server-Side error on {self.ip}\n{err}')
        sys.excepthook(exc.__class__, exc, exc.__traceback__)

    def wait_for(self, req_id, timeout=5):
        self.debug(f'waiting for {req_id}...')
        _time = 0
        while req_id not in self._unk_req:
            if _time > timeout:
                self.warn(f'timeout {req_id}')
                raise Exception('Time is out')
            time.sleep(0.1)
            _time += 0.1
        self.debug(f'get {req_id}')
        return self._unk_req.pop(req_id)

    def connect(self):
        super().connect()
        self.debug(self._unk_req)

    def auth(self, timeout=15):
        auth_req = {'username': self.usr, 'password': self.passw, 'type': 'auth'}

        self.debug(f'Login query: {auth_req}, sending')
        login_result = self.communicate(auth_req, timeout=timeout)
        if login_result is None or login_result['status'] != 'ok':
            self._work = False
            self._work_async_recv = False
            self.recreate_sock()
            self.debug('raising exception, login failed')
            raise Exception(f'Login failed: {login_result if 'desc' not in login_result else login_result['desc']}')
        self.info(f'Login result: {login_result}')
        return login_result

    def send(self, d):
        self.sock.send(json.dumps(d))

    def recv_split_request(self, start_req):
        return self.communicate(start_req)

