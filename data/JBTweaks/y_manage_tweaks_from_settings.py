import json
import os
import tkinter
from tkinter import ttk


class ZManageTweaksFromSettingsClass(Settings):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._base_widgets.append(Button(self._o, text='Manage Tweaks', command=tweakmenu))

Settings = ZManageTweaksFromSettingsClass

def tweakmenu():
    try:
        w = Popup()
    except NameError:
        showinfo('Error', 'Failed to init Popup class. If you running version without Popups, install "a_return_popups.py" tweak')
        return
    w.resizable(False,False)
    json_path = './data/JBTweaks/tweaks.json'
    try:
        with open(json_path, 'r') as f:
            tweak_data = json.load(f)
    except:
        tweak_data = {}

    vars_dict = {}

    def manage(tweak_name, var):
        tweak_data[tweak_name]['state'] = var.get()

        with open(json_path, 'w') as f:
           json.dump(tweak_data, f, indent=4)
        print(f"Updated {tweak_name} to {var.get()}")

    for file_name in os.listdir('./data/JBTweaks'):
        if file_name not in ['tweaks.json', 'configure.py']:
            if file_name not in tweak_data:
                tweak_data[file_name] = {'state': True}

            vars_dict[file_name] = tkinter.BooleanVar(value=tweak_data[file_name]['state'])

            cb = tkinter.Checkbutton(w,
                text=file_name,
                variable=vars_dict[file_name],
                command=lambda fn=file_name: manage(fn, vars_dict[fn])
            )
            cb.pack(anchor='w', padx=10, pady=2)

    tkinter.Button(w, text='Reload Tweaks', command=lambda: exec(open('./jaillib.py', 'r').read(), globals(), locals())).pack(anchor='w')

    with open(json_path, 'w') as f:
       json.dump(tweak_data, f, indent=4)
