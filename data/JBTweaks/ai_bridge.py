import json
import queue
import socket
import threading
import traceback

if 'local_AiBridge_sockCache' in globals():
    local_ai_bridge_sock = globals()['local_AiBridge_sockCache']
else:
    print('new socket')
    local_ai_bridge_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_ai_bridge_sock.bind(('127.0.0.1', 65502))
    local_ai_bridge_sock.listen(1)

client_sock = None

def response_loop_thread():
    global client_sock
    client_sock, addr = local_ai_bridge_sock.accept()

    print(f'got sock {client_sock}')

    while True:
        re = client_sock.recv(1024).decode('utf-8')
        try:
            js = json.loads(re)
            q.put(js)

        except json.JSONDecodeError:
            pass

q = queue.Queue()

def in_tk_loop():
    try:
        q_seg = q.get_nowait()

        print(f'got {q_seg}')
        try:
            exec(q_seg['code'], globals(), locals())
        except Exception as _ex:
            if client_sock:
                client_sock.send(''.join(traceback.format_exception(_ex)).encode('utf-8'))

    except queue.Empty:
        pass


root.tk_thread(in_tk_loop, 300)


threading.Thread(target=response_loop_thread, daemon=True).start()