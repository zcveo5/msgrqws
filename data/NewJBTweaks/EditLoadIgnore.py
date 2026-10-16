#meta
# {"req": ["LibSettings"]}
import os
import tkinter
from LibSettings import SettingsAPI
from data.lib import ui


def get_spl():
    with open('./data/NewJBTweaks/LoadIgnore.1') as fl:
        return [i[:-1] for i in fl.readlines()]


def set_spl(spl):
    with open('./data/NewJBTweaks/LoadIgnore.1', 'w') as fl:
        for i in spl:
            if i.endswith('\n'): i = i[:-1]
            fl.write(f'{i}\n')


def set_twk(e):
    n = e.widget.name
    new_spl = get_spl()
    print(new_spl)
    if not e.widget.var.get():
        new_spl.append(n)
    else:
        try:
            new_spl.remove(n)
        except ValueError:
            pass
    print(new_spl)
    set_spl(new_spl)



def manage():
    pop = ui.Popup()
    pop.pack_propagate(True)
    pop.root_frame.pack_propagate(True)
    spl = get_spl()
    for i in os.listdir('./data/NewJBTweaks'):
        i = '.'.join(i.split('.')[0:-1])
        var = tkinter.BooleanVar()
        w = tkinter.Checkbutton(pop, text=i, variable=var)
        if i in spl:
            w.select()
        w.var = var
        w.name = i
        w.bind('<ButtonRelease-1>', set_twk)
        w.pack()


SettingsAPI.create_widget('ROOT', 'Button', text='LoadIgnore Manage', command=manage)