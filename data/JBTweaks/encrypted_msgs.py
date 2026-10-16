from data.lib.encrypting import *

print('# Thanks for use JBEM #')

key = {'\n': '#', 'q': 'K', 'w': '4', 'e': 'G', 'r': '2', 't': 'O', 'y': '9', 'u': 'D', 'i': 'q', 'o': 'z', 'p': 'C', 'a': ')', 's': "'", 'd': '{', 'f': 'J', 'g': '$', 'h': 'd', 'j': 'M', 'k': '|', 'l': 'v', 'z': 'n', 'x': ' ', 'c': '(', 'v': '\n', 'b': '~', 'n': '*', 'm': '.', 'Q': 'l', 'W': 'm', 'E': ',', 'R': 'Z', 'T': 'H', 'Y': '[', 'U': ':', 'I': 'f', 'O': 'r', 'P': 'P', 'A': 'A', 'S': '8', 'D': 'F', 'F': 'Q', 'G': 'x', 'H': 'L', 'J': '_', 'K': '^', 'L': 'Y', 'Z': 'N', 'X': '+', 'C': '%', 'V': 'B', 'B': '/', 'N': 'p', 'M': ']', '1': '<', '2': 'w', '3': '&', '4': '3', '5': 'g', '6': 'h', '7': 'e', '8': 'y', '9': 'V', '0': 'R', '~': ';', '!': 'W', '@': '5', '#': 'E', '$': 'i', '%': 'c', '^': '?', '&': '}', '*': '@', '(': 'U', ')': 'j', '_': '6', '+': 'b', '-': '=', '=': 'S', '?': '!', '>': 'X', '<': '>', ',': 'I', '.': '7', '/': '-', '|': 'T', '"': 'o', "'": '"', '[': 't', ']': '0', '{': 'a', '}': '1', ':': 's', ';': 'u', ' ': 'k'}

def send_message_jb_em(event=None, is_private=False, **kw):
    pprint(event)
    try:
        to_send = {'text': encrypt('$JBEM$-' + send_entry.get("0.0", "end"), key), '_show_ip': bt_server_data[1]['answer']['_show_ip'], 'name': username}
    except KeyError:
        show('Error', 'Not connected to Auth connect')
        return
    if is_private:
        to_send.update({'to': 'private', 'to_cl': kw['private_addr']})
    else:
        to_send.update({'to': 'public'})
    message = to_send
    my_message.set("")
    try:
        chat.send(message)
    except OSError:
        showerror('Error', 'SOCK_DISCONNECTED')
        to_send['text'] += ' (!) SOCK_DISCONNECTED'
    if is_private:
        read[kw['private_addr']] = chat_lib.private_msgs()[kw['private_addr']]
    else:
        read['General'] = chat_lib.msgs()
    send_entry.delete("0", tk.END)


def complete_recv_jb_em():
    try:
        chat_lib.cl.send({'action_for_chat_server': 'OnlineList'})
        update_online_list(chat_lib.online_list)
        temp = chat_lib.msgs()
        tmp = []
        for i in temp:
            if '$JBEM$-' in i or 'i_/,]i=' in i:
                _tm2 = i.split(': ')
                i = _tm2[0] + ': ' + decrypt(_tm2[1], key)
            tmp.append(i)
        chat_win_ref(tmp)
        if chat_selected not in ['General', '']:
            temp = chat_lib.private_msgs()[chat_selected]
            tmp = []
            for i in temp:
                if '$JBEM$-' in i or 'i_/,]i=' in i:
                    _tm2 = i.split(': ')
                    i = _tm2[0] + ': ' + decrypt(_tm2[1], key)
                tmp.append(i)
            chat_win_private_ref(tmp)
    except Exception as _cr_ex:
        showerror('complete_recv error', f'{_cr_ex.__class__}:\n{traceback.format_exc()}')


send_message = send_message_jb_em
complete_recv = complete_recv_jb_em