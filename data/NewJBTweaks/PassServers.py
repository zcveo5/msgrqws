# METADATA
# {}

import J
import Application

skip = J.SharedMemory.get('PassServersEnabled', True)


class PP:
    def __init__(self):
        self.was = False

    def __call__(self, v, *args, **kwargs):
        if v == '[info] main thread started':
            self.was = True
        Application.origpprint(v, *args, **kwargs)


def raiser(exc):
    def w(*args, **kwargs):
        raise exc
    return w


def patch():
    setattr(Application, 'origpprint', Application.pprint)
    Application.pprint = PP()
    if skip:
        Application.auth.connect = raiser(ConnectionRefusedError('[PassServers] connection "refused"'))
        Application.chat_lib.Chat.connect = raiser(ConnectionRefusedError('[PassServers] connection "refused"'))


def check_mainloop():
    if not Application.pprint.was:
        raise Exception('JFlagCancelMainloop')


J.API.on_init(patch)
J.API.p_mainloop_check(check_mainloop)