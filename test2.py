from tkinter import *


def edit_dictionary(master, dct, on_save):
    fr = Frame(master)

    _entries = Frame(fr)

    def _edit_var(var, callback, *args):
        def wrapper(*_):
            callback(var.get(), *args)
        return wrapper

    def _val(val, key):
        print(key, val)
        dct[key] = val

    def ask_key(callback):
        def _ret(_):
            callback(e.get())
            e.destroy()
        e = Entry(_entries)
        e.bind('<Return>', _ret)
        e.pack()

    def create_fr(_k, _v):
        _w = Frame(_entries)

        entry_key = Label(_w, text=_k)
        entry_key.pack(side='left')

        _value_var = StringVar(value=f'{_v}')
        _value_var.trace_add('write', _edit_var(_value_var, _val, k))
        entry_value = Entry(_w, textvariable=_value_var)
        entry_value.variable = _value_var
        entry_value.value_type = type(_v)
        entry_value.pack(side='left')

        _w.pack(fill='x')

    _entries.pack()

    for k, v in dct.items():
        create_fr(k, v)

    Button(fr, text='Save', command=lambda: on_save(dct)).pack()
    Button(fr, text='Add', command=lambda: ask_key(lambda _k: create_fr(_k, ''))).pack()

    return fr


root = Tk()

w = edit_dictionary(root, {'hello': 'world'}, lambda d: print(d))
w.pack()

root.mainloop()