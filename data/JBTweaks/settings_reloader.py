import tkinter

setts_orig = Settings

class SettingsReloaded(setts_orig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._base_widgets.append(Button(self._o, text='JailBreak Tweak Reloader',
                                                command=_main, bg=default_bg,
                                                fg=default_fg, font=font_theme))


Settings = SettingsReloaded


def _main():
    def reload(event):
        try:
            name = event.widget.get(event.widget.curselection())
        except tkinter.TclError:
            return
        if name in ['', ' ']:
            return
        if name == '- Close -':
            w.place_forget()
            return
        try:
            exec(open(f'./data/JBTweaks/{name}', 'r', errors='replace').read(), globals(), locals())
        except (FileNotFoundError, OSError):
            pass
        w.place_forget()
    w = tkinter.Listbox(width=50, height=30, bg=default_bg, fg=default_fg)
    for i in ['Click on tweak you want to reload:'] + globals()['__JailBreakTweaks__'] + ['- Close -']:
        w.insert('end', i)
    w.place(x=0, y=0)
    w.bind('<<ListboxSelect>>', reload)


