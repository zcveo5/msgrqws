import json
import tkinter
import data.lib.ui


class BaseDataEditorDebug(Debug):
    def debugtools(self):
        super().debugtools()
        Button(self.debugger, text='base_data_editor', command=base_data_edit).grid(column=1, row=6)


Debug = BaseDataEditorDebug


def base_data_edit():
    def load():
        txt.delete("0.0", "END")
        with open('./data/base_data.json') as fl:
            txt.insert("0.0", str(json.load(fl)))

    def save():
        try:
            to_sv = json.dumps(txt.get("0.0", "END"))
            with open('./data/base_data.json', 'w') as fl:
                fl.write(to_sv)
        except json.JSONDecodeError:
            show('Json', 'SyntaxError somewhere')


    pop = data.lib.ui.Popup(title='BDE')

    txt = tkinter.Text(pop)
    txt.pack(fill='both')
    btns = tkinter.Frame(pop)
    btns.pack()

    data.lib.ui.Button(btns, text='save', command=save).pack(side='left')
    data.lib.ui.Button(btns, text='load', command=load).pack(side='left')