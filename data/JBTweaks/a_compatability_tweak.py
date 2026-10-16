orig_Settings = Settings
globals()['__HasCompatibilityTweak__'] = True

try:
    class _SidePanelMod(btaeui.SidePanel):
        def __init__(self, *args, **kwargs):
            cfg = ''
            for i in args:
                cfg += f'{i}, '
            for k, v in kwargs.items():
                cfg += f'{k}={repr(v)}, '
            print(f'# CT # creating SideSettings with {cfg[:-2]}')
            super().__init__(*args, **kwargs)


    SidePanel = _SidePanelMod
except NameError:

    print('Passing SideSettings mod')


class SideSettings(orig_Settings):
    def __init__(self):
        self._base_widgets = []
        super().__init__()
        if not hasattr(self, '_o'):
            print('Compatibility _o create')
            self._o = self.window
            self.window.geometry('200x400')

        if True:
            print('Compatibility _bw create')
            self._base_widgets = [Button(self._o, text=locale['setting_sub_f_INTERFASE'],
                           command=self.sub_f_ui, fg=default_fg,
                           bg=default_bg, font=font_theme), Button(self._o, text=locale['setting_sub_f_DEBUG'],
                           command=self.sub_f_debug, fg=default_fg,
                           bg=default_bg, font=font_theme),Button(self._o, text=locale['setting_sub_f_PROFILE'],
                           command=self.sub_f_profile, bg=default_bg,
                           fg=default_fg, font=font_theme),Button(self._o, text=locale['setting_sub_f_MODS_REPO'],
                           command=self.sub_f_mod_rep, bg=default_bg,
                           fg=default_fg, font=font_theme)]
        if hasattr(self, '_base_widgets'):
            self._base_widgets += [Button(self._o, text='close settings',
                           command=reinit_window, bg='black',
                           fg='red', font=font_theme)]

    @staticmethod
    def create(obj=None, *args, **kwargs):
        if obj is not None:
            if hasattr(obj, 'pack'):
                obj.pack(anchor='nw')
        if args or kwargs:
            print(f'What is args {args} kw {kwargs}')

    def _create_base(self, master=None, *args, **kwargs):
        self.create(Label(), x=-100, y=-100, name='loaded')
        y = 30
        for wid in self._base_widgets:
            self.create(self.create_copy(wid, master), 5, y, f'Settings_Element:{y // 30}', anchor='nw', fill='x')
            y += 30

    def build(self):
        print('Build')
        _s = Popup(title='JBCT Settings')
        print(f'Popup for settings created: {_s}')
        self._create_base(_s)

    def create_copy(self, wid, master=None):
        print(f'Creating copy of {wid} {'' if master is None else f'at {master}'}')
        if master is None:
            master = self._o
        wid_class = wid.__class__
        new_widget = wid_class(master)
        for _cfg_elem in wid.keys():
            new_widget.config({_cfg_elem: wid[_cfg_elem]})
        return new_widget


def reinit_window_mod(*args):
    global chat_window
    for i in main.winfo_children():
        i.place_forget()
        i.grid_forget()
        i.pack_forget()

    chat_window = Text(main, fg=default_fg, bg=default_bg, font=font_theme, width=110)
    chat_window.place(x=0, y=0)
    reinit_ui(*args)


reinit_window = reinit_window_mod
globals()['Settings'] = SideSettings
side_settings = globals()['Settings']
Settings = SideSettings
if hasattr(main, 'adv'):
    main.adv += ' # Compatibility Tweak #'

__orig_reinit123 = reinit_ui
def _reinit_ui(*args):
    print('# Compatibility Tweak UI Refresh #')
    __orig_reinit123(*args)
    #Button(text='SideSettings Emulator', command=side_settings).place(x=800, y=100)

reinit_ui = _reinit_ui