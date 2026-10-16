from tkinter import TclError
try:
    from data.lib.ui import Popup
except ModuleNotFoundError:
    print(Popup)
import tkinter as __tk__

orig_reinit = reinit_ui
cur_taskbar = None
cur_taskbar : None | Popup
taskbar_state = True


class EventEmulator:
    def __init__(self, **cnf):
        for _k, _v in cnf.items():
            exec(f'self.{_k} = _v', {'_v': _v, 'self': self})


def reinit_ui_mod(no_reinit_theme=False):
    update()
    orig_reinit(no_reinit_theme)
reinit_ui = reinit_ui_mod

def update():
    def reopen(event):
        _w = ui._widgets['popups'][event]
        _w.update_info()
        _w.pack()
        _w.lift()
        show('Info', f'Taskbar winfo:\n{_w.winfo_x()}, {_w.winfo_y()}\nFRom:')
    popups.delete('0', 'end')
    popups.add_command(label='Update', command=update)
    popups.add_separator()
    try:
        for _name, _w in ui._widgets['popups'].items():
            print(_name)
            try:
                if _w.winfo_exists():
                    exec(f'popups.add_command(label="{_name}", command=lambda: reopen("{_name}"))', {'reopen': reopen, 'popups': popups})
                else:
                    exec(f'popups.add_command(label="NotExists / Failed to add {_name}")',{'reopen': reopen, 'popups': popups})
            except TclError:
                exec(f'popups.add_command(label="TclError / Failed to add {_name}")', {'reopen': reopen, 'popups': popups})

    except AttributeError:
        print('[taskbar] Failed to fetch popups')

top_menu = __tk__.Menu(main)
popups = __tk__.Menu(tearoff=0)
popups.add_command(label='Update', command=update)

top_menu.add_cascade(label='Taskbar', menu=popups)
main.config(menu=top_menu)