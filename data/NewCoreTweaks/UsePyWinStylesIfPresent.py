import sys


def _m():
    try:
        import pywinstyles
    except ModuleNotFoundError:
        print('no pywinstyles :(')
        return

    import pywinstyles

    class _PWS_Tk_Wrapper(Win):
        def __init__(self):
            self._last_bg = None
            self._last_fg = None

            super().__init__()
            self.update_idletasks()

            self._loop()

        def option_add(self, *args, **kwargs):
            super().option_add(*args, **kwargs)
            self._do_step()

        def _do_step(self):
            opt_bg = self.option_get('background', 'Background')
            opt_fg = self.option_get('foreground', 'Foreground')

            if opt_bg == '':
                opt_bg = 'black'
            if opt_fg == '':
                opt_fg = 'white'

            try:
                if opt_fg != self._last_fg:
                    pywinstyles.change_border_color(self, opt_fg)
                    pywinstyles.change_title_color(self, opt_fg)
                    self._last_fg = opt_fg
                    print(f'[PyWinStyles] Change fg for {self.title()!r} to {opt_fg}')

                if opt_bg != self._last_bg:
                    pywinstyles.change_header_color(self, opt_bg)
                    self._last_bg = opt_bg
                    print(f'[PyWinStyles] Change bg for {self.title()!r} to {opt_bg}')
            except ValueError:
                print(f'[PyWinStyles] Failed to commit colors {opt_fg} {opt_bg} so passing current step')

        def _loop(self):
            self._do_step()
            self.after(1000, self._loop)

    sys.modules['data.lib.ui'].Win = _PWS_Tk_Wrapper

_m()