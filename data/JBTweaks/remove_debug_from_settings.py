import json
import os.path
try:
    from data.lib.ui import Popup
except ModuleNotFoundError:
    pass


if not os.path.exists('./data/settings_conf.json'):
    with open('./data/settings_conf.json', 'w') as fl:
        fl.write('{}')
conf = json.load(open('./data/settings_conf.json'))
_conf = conf.copy()

class RemoveDebugFromSettingMod(Settings):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.enabled_rdfsm = True
        self.temp = []

    def sub_f_ui(self):
        super().sub_f_ui()
        Button(self.window_locale, text='Manage What widgets shown on side panel', command=self.ui_custom, bg=default_bg, fg=default_fg, font=font_theme).pack(anchor='nw', padx=3)
        if not self.enabled_rdfsm:
            Label(self.window_locale, text='On _create_base creating failed').pack()

    def _create_base(self, master=None):
        if self.enabled_rdfsm:
            try:
                y = 0
                try:
                    locale.get_key('123')
                except AttributeError:
                    def _get_key(item):
                        if 'UNK:' in item:
                            return item.split(':')[1]
                        else:
                            try:
                                return list(locale.lc_dct.keys())[list(locale.lc_dct.values()).index(item)]
                            except ValueError:
                                return f'UNK:{item}'
                    locale.get_key = _get_key
                for wid in self._base_widgets:
                    if locale.get_key(wid['text']) not in conf:
                        conf.update({locale.get_key(wid['text']): True})
                    if conf[locale.get_key(wid['text'])]:
                        cp = self.create_copy(wid, master)
                        cp.place(anchor='nw', y=y, relwidth=1.0)
                        cp.update_idletasks()
                        y += cp.winfo_height()
            except Exception as _setts_custom_recreate_ex:
                self.enabled_rdfsm = False
                print(f'[Settings Remove] stop with {_setts_custom_recreate_ex}')
                self._create_base()
        else:
            super()._create_base()


    def ui_custom(self):
        def switch(event):
            _txt = event.widget['text'].split(' | ')[0]
            conf[_txt] = not conf[_txt]
            if conf != _conf:
                json.dump(conf, open('./data/settings_conf.json', 'w'))

        win = Popup(main, 450, 250, [300, 500], [default_bg, default_fg, font_theme], title='Settings UI Customization')
        for i in self._base_widgets:
            txt = locale.get_key(i['text'])
            if txt not in conf:
                conf.update({txt: True})
            b = Button(win, text=txt + ' | ' + str(' ' * (30 - len(txt))) +  ' | ' + str(conf[txt]), bg=default_bg, fg=default_fg, font=font_theme)
            b.pack(anchor='nw')
            b.bind('<ButtonPress-1>', switch)

        if conf != _conf:
            json.dump(conf, open('./data/settings_conf.json', 'w'))




Settings = RemoveDebugFromSettingMod
