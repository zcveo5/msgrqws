# METADATA
# {"req": ["LibTweaksInfo", "LibSettings"]}
import tkinter

import Application
import LibTweaksInfo
from LibSettings import SettingsAPI
from data.lib import ui



def view_log(log: LibTweaksInfo.Log):
    def wrp():
        pop = ui.Win()
        print(pop.__class__)
        pop.option_add('*Background', Application.default_bg)
        pop.option_add('*Foreground', Application.default_fg)
        pop.title(f'log view {log.name}')
        pop.minsize(600, 400)
        lb = ui.Listbox(pop)
        lb.delete(0, 'end')
        for i in log.content.split('\n'):
            lb.insert('end', i)

        _id = log.on_content(lambda s: lb.insert('end', s))

        def _lp():
            try:
                if not pop.winfo_exists():
                    log.on_content.rm(_id)
                pop.after(100, _lp)
            except tkinter.TclError:
                log.on_content.rm(_id)

        _lp()

        lb.pack(fill='both', expand=True)

    return wrp


def show():
    pop = ui.Popup()
    for _log in LibTweaksInfo.LOGGERS:
        ui.Button(pop, text=_log.name, command=view_log(_log)).pack()



SettingsAPI.create_widget('ROOT', 'Button', text='Tweaks logs UI', command=show)