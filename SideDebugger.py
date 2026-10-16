import asyncio
import hashlib
import json
import random
import socket
import threading
import time
import tkinter.messagebox
import traceback
from tkinter import Tk, Text, Toplevel, Listbox
from tkinter.ttk import *


class ASock:
    def __init__(self):
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._task: asyncio.Task | None = None
        self._fut = {}

    @property
    def is_open(self):
        return self._writer is not None

    async def _extract_task(self):
        while self._writer:
            try:
                payload = await self._reader.readline()
            except ConnectionResetError:
                self._task = None
                return

            if not payload:
                self._task = None
                return

            j = json.loads(payload)

            print(f'[Sock] recv {j}')

            if 'req_id' in j:
                req_id = j['req_id']
                if req_id in self._fut:
                    self._fut[req_id].set_result(j)

    async def connect(self, host, port):
        self._reader, self._writer = await asyncio.open_connection(host, port)
        self._task = asyncio.create_task(self._extract_task())

    async def close(self):
        try:
            self._writer.close()
            await self._writer.wait_closed()
        except ConnectionResetError:
            pass
        self._reader, self._writer = None, None
        if self._task is not None:
            await self._task

    async def send(self, payload: str | dict):
        if isinstance(payload, dict):
            payload = json.dumps(payload)

        if not payload.endswith('\n'):
            payload = f'{payload}\n'
        self._writer.write(payload.encode('utf-8'))
        await self._writer.drain()

    async def ask(self, payload):
        rid = 0
        while rid in self._fut:
            rid = random.randint(0, 0xffff)

        loop = asyncio.get_event_loop()

        fut = self._fut[rid] = loop.create_future()
        payload['req_id'] = rid

        await self.send(json.dumps(payload))

        return await fut


async def connect(port, password):
    if sock.is_open:
        await sock.close()
    try:
        await sock.connect('127.0.0.1', port)
    except ConnectionRefusedError:
        return False, 'Connection Refused'
    auth_result = await sock.ask({'type': 'auth', 'hash': hashlib.sha256(password.encode('utf-8')).hexdigest()})
    if auth_result['status'] == 'ER':
        return False, 'Auth failure'
    return True, None


debugable = {}


def broadcast_listener():
    PORT = 37020

    # 1. Create a UDP socket
    # socket.AF_INET specifies IPv4, socket.SOCK_DGRAM specifies UDP
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 2. Bind the socket to all interfaces and the specific port
    server.bind(("", PORT))
    server.settimeout(0.5)
    print(f"Listening for broadcasts on port {PORT}...")

    try:
        while True:
            to_remove = []
            for k, v in debugable.items():
                if v['time'] < time.time() - 5:
                    print(f'[Broadcast] removed {k}')
                    to_remove.append(k)

            for i in to_remove:
                del debugable[i]

            try:
                data, addr = server.recvfrom(1024)
            except TimeoutError:
                continue
            if addr not in debugable:
                debugable[addr] = {'time': time.time(), 'addr': data.decode('utf-8')}
                print(f'[Broadcast] add {addr}')
    except KeyboardInterrupt:
        print("\nReceiver shutting down.")
    finally:
        server.close()


threading.Thread(target=broadcast_listener, daemon=True).start()


def connect_wm():
    async def connect_wrapper(c):
        nonlocal state
        b.config(state='disabled')
        state = False

        try:
            ad = int(addr.get())
        except (TypeError, ValueError):
            b.config(state='normal')
            state = True
            return

        st, desc = await connect(ad, password.get())
        if st:
            c.destroy()
        else:
            tkinter.messagebox.showerror('Error', f'{st}\n{desc}')
            b.config(state='normal')
            state = True

    connector = Toplevel()
    connector.wm_minsize(200, 200)

    Label(connector, text='Port').pack()

    addr = Entry(connector)
    addr.pack()

    Label(connector, text='Password').pack()

    password = Entry(connector)
    password.pack()

    loop = asyncio.get_event_loop()

    b = Button(connector, text='Try', command=lambda: loop.create_task(connect_wrapper(connector)))
    b.pack()

    state = True

    Label(connector, text='OR\nSelect a broadcasted').pack()

    lb = Listbox(connector)
    lb.pack()

    def write_entries(e):
        if not state:
            return
        a = lb.get(lb.curselection())
        addr.delete('0', 'end')
        addr.insert('end', a.split(':')[1])
        password.delete('0', 'end')
        password.insert('end', 'TestDebugPassword')
        loop.create_task(connect_wrapper(connector))

    def refr():
        lb.delete('0', 'end')
        lb.insert('end', *[v['addr'] for v in debugable.values()])
        lb.after(100, refr)

    refr()

    lb.bind('<<ListboxSelect>>', write_entries)



sock: ASock | None = None
command: Text | None = None


async def _ask(data):
    try:
        res = await sock.ask({'type': 'exec', 'data': data})
    except ConnectionResetError:
        tkinter.messagebox.showerror('', 'ConnectionReset')
        return
    if res['status'] == 'ER':
        tkinter.messagebox.showerror('', 'ER')

async def send_command():
    if not sock.is_open:
        tkinter.messagebox.showerror('', 'Not Connected')
    else:
        await _ask(repr(command.get('0.0', 'end')))

async def recovery_screen():
    if not sock.is_open:
        tkinter.messagebox.showerror('', 'Not Connected')
    else:
        await _ask("""
import tkinter

FuckassRecovery = tkinter.Frame(Application.main)
tkinter.Label(FuckassRecovery, text='SideDebug Recovery. Please wait to debugger do it work.').pack()

def lp():
    FuckassRecovery.lift()
    FuckassRecovery.place(relwidth=1.0, relheight=1.0)
    FuckassRecovery.after(100, lp)
    
lp()""")



async def recovery_screen_disable():
    if not sock.is_open:
        tkinter.messagebox.showerror('', 'Not Connected')
    else:
        await _ask("""
FuckassRecovery.destroy()
Application.reinit_ui()""")

async def recovery_screen_debug():
    if not sock.is_open:
        tkinter.messagebox.showerror('', 'Not Connected')
    else:
        await _ask("""
def get_debug():
    return ''

def lpp():
    FuckassRecovery.children[list(FuckassRecovery.children.keys())[0]]['text'] = get_debug()
    FuckassRecovery.after(100, lpp)
lpp()""")

async def recovery_screen_write():
    if not sock.is_open:
        tkinter.messagebox.showerror('', 'Not Connected')
    else:
        await _ask(f"""
try:
    FuckassRecovery.children[list(FuckassRecovery.children.keys())[0]]['text'] += {repr(command.get('0.0', 'end'))}
except: pass""")

async def main():
    global sock, command
    sock = ASock()

    root = Tk()
    root.wm_minsize(200, 200)

    Button(root, text='Connect', command=connect_wm).pack(anchor='nw')
    Button(root, text='Send', command=lambda: asyncio.create_task(send_command())).pack(anchor='nw')
    Button(root, text='Scr', command=lambda: asyncio.create_task(recovery_screen())).pack(anchor='nw')
    Button(root, text='Scr Disable', command=lambda: asyncio.create_task(recovery_screen_disable())).pack(
        anchor='nw')
    Button(root, text='Debug information', command=lambda: asyncio.create_task(recovery_screen_debug())).pack(
        anchor='nw')
    Button(root, text='Printin FuckassRecovery label', command=lambda: asyncio.create_task(recovery_screen_write())).pack(
        anchor='nw')

    command = Text(root)
    command.pack()

    window_alive = True

    def set_flag():
        nonlocal window_alive
        window_alive = False
        root.destroy()

    root.protocol('WM_DELETE_WINDOW', set_flag)

    async def refr():
        while window_alive:
            root.update()
            await asyncio.sleep(0.05)

    await asyncio.create_task(refr())


asyncio.run(main())