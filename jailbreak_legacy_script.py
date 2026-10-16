import threading
from tkinter import Label, Button, Frame
from jailbreak import ModWin

def reinit_ui_mod(*args, **kwargs):
    main.wm_geometry('900x500')
    orig_reinit_ui(*args, **kwargs)


class __OBJ__FUCK_YOOU:
    def __getattribute__(self, item):
        print(f'[*] $JBLS emulating {item}')
        return self

    def __call__(self, *args, **kwargs):
        ...

def quit():
    global work
    work = True
    main.quit()

orig_reinit_ui = reinit_ui
reinit_ui = reinit_ui_mod

main.quit() ; main.destroy()
main = ModWin()
main.wm_geometry('900x500')
main.adv = 'Legacy'
#main.resizable(False, False)
buttons = Frame()
buttons.pack_propagate(True)
buttons.place(relx=1.0, y=0, anchor='ne')
load_lbl = Label(justify='left')
load_lbl.place(x=0, y=30)
exit_button = Button(buttons, text='exit', command=exit)
exit_button.pack(anchor='sw')
action_load = Button(buttons, text='action not set')
action_load.pack(anchor='sw')
try:
    Button(buttons, text='debug', command=Debug().debugtools).pack(anchor='sw')
except: pass
pb = __OBJ__FUCK_YOOU()
try:
    Button(buttons, text='Continue', command=quit).pack(anchor='sw')
except: pass
bt_server_data = (True, {'password': '123123123'})
receive_thread = __OBJ__FUCK_YOOU()
exec(open('./jailbreak_exec_tweaks.py', 'r').read())