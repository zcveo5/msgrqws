import threading

import Application
from data.lib.ui import *


def _updated_stats(self):
    log_inf_bool = False

    def toggle_log_infile():
        nonlocal log_inf_bool
        if log_inf_bool:
            log_inf.configure(text='log_any_change_in_file:F')
        else:
            log_inf.configure(text='log_any_change_in_file:T')
        log_inf_bool = not log_inf_bool

    win = Win()
    print(threading.current_thread())
    win.title(f'Statistics t:{threading.enumerate().index(threading.current_thread())}')
    win.resizable(False, False)
    info = Label(win, text='', justify='left')
    log_inf = Button(win, text='log_any_change_in_file:F', command=toggle_log_infile)
    log_inf.pack(anchor='nw')
    info.pack(anchor='nw')
    last_inf = ''

    def tk_thread():
        nonlocal last_inf

        last_inf = ('==Fixed&OverrideDebugStats==\n'
                    'Threads (all):\n{0}\n').format('\n'.join([i.name for i in threading.enumerate()]))

        info['text'] = last_inf

        Application.main.after(100, tk_thread)

    Application.main.after(100, tk_thread)

Application.Debug.stats = _updated_stats