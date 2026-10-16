import os
import subprocess
import sys
import threading
import time
import traceback
from tkinter import Tk, TclError
from tkinter.messagebox import showerror
import data.lib.connect.auth_alt
import data.lib.connect.chat_alt
from data.lib import ui
from data.lib.ui import Win, Label, Button, tkinter, Entry, Popup
from tkinter.scrolledtext import ScrolledText

server: subprocess.Popen | None

def custom_exc_handler(exc_type, exc_value=None, exc_traceback=None):
    tb_lines = list(traceback.format_exception(exc_type, exc_value, exc_traceback))
    tb_text = "".join(tb_lines)
    print('===== TRACEBACK =====\n' + tb_text + f'\n===== END =====')
    showerror(f'Error: {exc_type.__class__}', tb_text)

sys.excepthook = custom_exc_handler
#sys.stdout = StringIO(' - ~ * $ Root Client $ * ~ - ')
work = True
server = None
log = [' ~ $ Server Not Started $ ~ ']

def read_logs():
    while work:
        for line in server.stdout:
            if line not in log:
                log.append(line)
                if 'WinError' in line:
                    if '10048' in line:
                        showerror('WinError', 'Server addr is already bound to something')
                        break
                print(f'[SERVER] {line}')
        for line in server.stderr:
            if line not in log:
                log.append(line)
                print(f'[SERVER_STDERR] {line}')
        time.sleep(0.5)


def read_logs_ui():
    scrolled = 0
    def update_logs():
        logs_text.delete("0.0", "end")
        for i in log[scrolled:scrolled+20]:
            logs_text.insert("end", i)
        win.after(100, update_logs)
    def scroll(event):
        nonlocal scrolled
        temp = scrolled + event.delta // 120
        if 0 < temp < len(log):
            scrolled = temp
    win = Popup(title='Win')
    logs_text = ScrolledText(win)
    logs_text.pack()
    logs_text.bind('<<MouseWheel>>', scroll)
    win.resizable(False, False)
    update_logs()


def start_server():
    global server, log
    log = [' ~ $ Starting Server $ ~ \n']
    try:
        server = subprocess.Popen(
        [sys.executable, serv_to_start],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1)
    except Exception as _ex:
        showerror('Error', f'Error starting server: {_ex.__class__}\n\n{traceback.format_exc()}')

    threading.Thread(target=read_logs, daemon=True).start()
    root.create('StartClient', Button, recreate_if_exists=True, text='Start Root Client!', command=start_root_client).build('pack', anchor='nw')


def tk_input_blocking(prompt="") -> str:
    result = ''

    def on_submit():
        nonlocal result
        result = entry.get()
        ask.destroy()

    ask = Tk()
    Label(ask, text=prompt).pack(padx=20, pady=5)

    entry = Entry(ask, width=30)
    entry.pack(padx=20, pady=5)
    entry.focus_set()
    entry.bind("<Return>", lambda e: on_submit())

    Button(ask, text="OK", command=on_submit).pack(pady=10)

    ask.mainloop()
    return result


def start_root_client():
    def start(event):
        win.destroy()
        try:
            try:
                temp = log[2].split(':')
                print(temp)
                ip = f'{temp[0].split()[-1::][0]}:{temp[1]}'
            except Exception as get_addr_exception:
                ip = tk_input_blocking(f'ip addr server (get_addr_exception: {get_addr_exception})')
            RootClient(username.get(), password.get(), ip)
        except Exception as root_client_error:
            showerror(f'{root_client_error.__class__}', traceback.format_exc())
            print(traceback.format_exc())
    win = Popup()
    win.title('auth')
    win.resizable(False, False)
    Label(win, text='account').pack()
    username = Entry(win)
    username.pack()
    username.bind('<Return>', start)
    password = Entry(win)
    password.pack()
    password.bind('<Return>', start)


class RootClient:
    def __init__(self, username, password, addr):
        global client
        client = self
        self._user = username
        self._addr = addr
        self._theme = './data/themes/hh.theme'
        self.win = root
        self.win.title(f'ROOT:MSGR-QW AS {username} AT {addr}')
        self.win.resizable(False, False)
        Label(self.win, text='Authenticating...').pack(anchor='nw')
        print(addr)
        self.auth = data.lib.connect.auth_alt.User(username, password, addr.split(':')[0], int(addr.split(':')[1]))
        self.chat = data.lib.connect.chat_alt.Chat(addr.split(':')[0], int(addr.split(':')[1]), username)
        self.chat.send({'action_for_chat_server': 'MyUSER', 'username': username})
        self.chat.connect()

        self.online_list = ui.Listbox(self.win)
        self.online_list.bind('<<ListboxSelect>>', self.view_user_messages)
        self.online_list.pack(anchor='ne')

        #Button(self.win, text='View Messages', command=self.view_user_messages).pack(anchor='ne')

        root.tk_thread(self.update_info, 1000)
        threading.Thread(target=self.chat.async_recv, daemon=True).start()
        self.user_data = self.auth.get_data()
        Label(self.win, text=self.user_data).pack(anchor='nw')
        Button(self.win, text='Refresh', command=self.update_info).pack(anchor='ne')

    def view_user_messages(self, _event):
        print('Ping')
        selected_user = self.online_list.get(self.online_list.curselection())
        if selected_user:
            def show_category(_event):
                popup = Popup()
                try:
                    popup.title(f'~{selected_user}/{_event.widget.get(_event.widget.curselection())}/')
                except TclError:
                    popup.destroy()
                    return

                popup_text = ui.Listbox(popup)
                popup_text.pack(fill='both', expand=True)
                popup_text.bind('<<ListboxSelect>>', lambda x: True)
                second = _event.widget.get(_event.widget.curselection())

                parsed = []
                if second not in ['public', 'other']:
                    for _line in log:
                        if 'to_cl' in _line and 'text' in _line:
                            try:
                                evald = eval(_line.split('Received: ')[1])
                            except IndexError:
                                showerror('Error', f'Failed to parse line:\n{_line}')
                                evald = {'name': '', 'text': ''}
                            if evald['name'] in [selected_user, second]:
                                parsed.append(f'{evald["name"]}: {evald["text"]}')
                else:
                    for _i in messages[second]:
                        parsed.append(_i)

                for _msg in parsed:
                    popup_text.insert('end', _msg)

            messages_window = Popup()
            messages_window.title(f"~{selected_user}/")

            messages_text = ui.Listbox(messages_window)
            messages_text.pack(fill='both', expand=True)
            messages_text.bind('<<ListboxSelect>>', show_category)

            messages = {'public': [], 'other': []}
            for line in log:
                if 'Received' in line and selected_user in line and 'text' not in line:
                    messages['other'].append(line)
                elif 'text' in line and selected_user in line:
                    msg_decoded = eval(line.split('eceived: ')[1])
                    if msg_decoded['to'] == 'public':
                        messages['public'].append(msg_decoded['text'])
                    else:
                        if msg_decoded['to_cl'] not in messages:
                            messages[msg_decoded['to_cl']] = []
                        messages[msg_decoded['to_cl']].append(msg_decoded['text'])
            for msg in messages.keys():
                messages_text.insert('end', f"{msg}")

            Button(messages_window, text="Close", command=messages_window.destroy).pack()

    def update_info(self):
        self.chat.send({'action_for_chat_server': 'OnlineList'})
        self.online_list.delete(0, 'end')
        for i in self.chat.online_list():
            self.online_list.insert("end", i)

    def ui(self):
        self.win.destroy_all_in()
        Button(self.win, text='Refresh', command=self.ui).pack(anchor='ne')
        self.online_list = ui.Listbox(self.win)
        self.online_list.bind('<<ListboxSelect>>', self.view_user_messages)
        self.online_list.pack(anchor='ne')
        #Button(self.win, text='View Messages', command=self.view_user_messages).pack(anchor='ne')


servers = []
for file in os.listdir('./'):
    if 'server' in file and '.py' in file:
        print(f'[!] Founded server file {file}')
        servers.append(file)
if len(servers) == 1:
    serv_to_start = servers[0]
else:
    print(f'[?] Please, select number of server file:\n{", ".join(servers)}')
    serv_to_start = servers[int(input('[?] ')) - 1]



client: RootClient | None
client = None
root = Win()
root.option_add('background', 'black')
root.option_add('foreground', 'green')
root.option_add('font', ['Consolas', 9])
root.option_add('highlightcolor', 'green')
root.report_callback_exception = custom_exc_handler
root.geometry([900, 500])
root.deiconify()
root.resizable(False, False)
root.create('WelcomeLbl', Label, text='Welcome to Root Client!').build('pack', anchor='nw')
root.create('StartServer', Button, text='Start Server', command=start_server).build('pack', anchor='nw')
root.create('ReadLogs', Button, text='Read Server Logs', command=read_logs_ui).build('pack', anchor='nw')
#root.create('ReadRootLogs', Button, text='Read Program Logs', command=read_logs_root_ui).build('pack', anchor='nw')
root.mainloop()

