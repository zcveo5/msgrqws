# METADATA
# {}
import hashlib
import json
import queue
import socket
import sys
import time
import traceback

import J
import Application
import asyncio
import threading


DEBUG_PASSWORD = 'TestDebugPassword'
dbg_hash = hashlib.sha256(DEBUG_PASSWORD.encode('utf-8')).hexdigest()

enable = False


class MessageHandler:
    def __init__(self):
        self.data = {'auth': False}

    def process(self, string) -> str | None:
        try:
            j = json.loads(string)
        except json.JSONDecodeError:
            return None

        fnc = getattr(self, f'the_{j['type']}')
        dt = fnc(j)
        if 'req_id' in j:
            dt['req_id'] = j['req_id']
        return dt

    def the_auth(self, dct):
        if dct['hash'] == dbg_hash:
            self.data['auth'] = True
            return {'status': 'OK'}
        return {'status': 'ER'}

    def the_exec(self, dct):
        if self.data['auth'] and enable:
            execs_queue.put((exec, (dct['data'], globals())))
            return {'status': 'OK'}
        return {'status': 'ER'}


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Asynchronously handles incoming client messages."""
    address = writer.get_extra_info('peername')
    proc = MessageHandler()

    try:
        while True:
            # Non-blocking read
            data = await reader.readline()
            if not data:
                break

            message = data.decode('utf-8')
            resp = proc.process(message)
            if resp:
                writer.write((json.dumps(resp) + '\n').encode('utf-8'))
                await writer.drain()  # Wait until the buffer is cleared


    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"\n[SERVER] Error with client {address}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


def run_async_loop(loop):
    """Target function for the background thread to run the loop indefinitely."""
    asyncio.set_event_loop(loop)
    loop.run_forever()

DEBUGGER_PORT = 12345


async def _create_server(cb, host, port):
    while True:
        try:
            return await asyncio.start_server(cb, host, port)
        except OSError as _ex:
            if _ex.errno == 10048:
                port += 1


def start_background_server():
    # 1. Create a brand new asyncio event loop
    loop = asyncio.new_event_loop()

    # 2. Start the TCP server inside that specific loop configuration
    # asyncio.start_server handles all socket binding and low-level select/epoll for you
    server_coro = _create_server(handle_client, '0.0.0.0', DEBUGGER_PORT,)
    server = loop.run_until_complete(server_coro)

    # 3. Spin up a background thread to keep the loop running forever
    bg_thread = threading.Thread(target=run_async_loop, args=(loop,), daemon=True)
    bg_thread.start()

    # Return the server object and loop so the main thread can shut them down later if needed
    return server, loop

DEST_PORT = 37020

def start_broadcast():

    # 1. Create a UDP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 2. Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # 3. Send a message every 2 seconds
    try:
        while True:
            message = f"127.0.0.1:{DEBUGGER_PORT}"

            # Send data to the broadcast address and destination port
            client.sendto(message.encode(), ('<broadcast>', DEST_PORT))

            time.sleep(2)
    finally:
        client.close()


server, server_loop = start_background_server()
execs_queue = queue.Queue()

threading.Thread(target=start_broadcast, daemon=True).start()

def proc_execs():
    while not execs_queue.empty():
        fnc, a = execs_queue.get()
        try:
            fnc(*a)
        except Exception as _ex:
            traceback.print_exception(_ex)


Application.main.tk_thread(proc_execs, 350)


def enable_side_debug():
    global enable
    enable = True

def disable_side_debug():
    global enable
    enable = False

def get_side_debug():
    return enable


J.SharedMemory['SideDebug'] = (enable_side_debug, disable_side_debug, get_side_debug, f'{DEBUG_PASSWORD}\n{DEBUGGER_PORT}')


@J.API.on_exit
def close():
    server.close()
    server_loop.call_soon_threadsafe(server_loop.stop)
    while server_loop.is_running():
        time.sleep(0.1)
        print('Waiting for server...')
    print('Exit')