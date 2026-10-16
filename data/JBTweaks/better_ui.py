from tkinter import TclError

orig_theme = theme
def _theme_mod(*args):
    orig_theme(*args)
    main.option_add('*Background', default_bg)
    main.option_add('*Foreground', default_fg)
    main.option_add('*Font', font_theme )
    def rec(master):
        for w in master.winfo_children():
            try:
                w.configure(bg=default_bg)
                w.configure(fg=default_fg)
                w.configure(font=font_theme)
            except TclError:
                print(f'[BetterUI] failed to apply theme to {w}')
            rec(w)
    rec(main)

theme = _theme_mod