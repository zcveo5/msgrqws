import subprocess
import sys
import tkinter.messagebox

try:
    import skia
    from someui import tk_window, widget, widget_extensions, abstract
except ModuleNotFoundError:
    if tkinter.messagebox.askyesno('Error', 'RewritedMsgView Libraries (skia-python, win32more) failed to import, autoinstall it with pip?'):
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'skia-python', 'win32more'])
        tkinter.messagebox.showinfo('OK', 'Please restart! Injection on current session will not be executed')
    raise Exception('JFlagSkipTweak')


import J
import Application

font_mgr = skia.FontMgr.RefDefault()


class Offsetable(widget_extensions.RelativePlaceWidget):
    def __init__(self, parent, offset_class):
        super().__init__(parent)
        self.offset_class = offset_class

    @property
    def global_x(self):
        return self.offset_class.x + super().global_x

    @property
    def global_y(self):
        return self.offset_class.y + super().global_y


class Label(Offsetable):
    typeface = font_mgr.matchFamilyStyle(
        "Segoe UI",
        skia.FontStyle.Normal(),
    )
    def __init__(self, parent, text):
        super().__init__(parent, parent.offset_class)

        self.font = skia.Font(self.typeface, 12)
        self._text = text
        self._tox = 0
        self._toy = 0
        self._blob: skia.TextBlob | None = None
        self.recreate_blob()
        self.text_paint = skia.Paint(0xffffffff)
        self._clr = '#ffffff'
        self.dirty_text = False

    def recreate_blob(self):
        self._blob = skia.TextBlob(self._text, self.font)
        r: skia.Rect = self._blob.bounds()
        _w, _h = r.width(), r.height()

        self._toy = _h
        self._tox = 5

    def size_hint(self):
        r: skia.Rect = self._blob.bounds()
        return r.width(), r.height()

    def draw_self(self, ctx: skia.Canvas):
        if self._clr != Application.default_fg:
            self._clr = widget_extensions.hex_str_to_int(Application.default_fg)
            self.text_paint.setColor(self._clr)

        super().draw_self(ctx)
        if self.dirty_text:
            self.recreate_blob()

        tx, ty = self.global_x + self._tox, self.global_y + self._toy
        ctx.drawTextBlob(self._blob, tx, ty, self.text_paint)

current_window: 'BufferedWnd | None' = None

@J.API.on_ready_window
def _w():
    Application.root.mainloop = run_mainloop

_load_chat_o = Application.load_chat
last_general_msgs = []
snaph = None

def lchat(e):
    global last_general_msgs, snaph
    _load_chat_o(e)
    if Application.chat_selected == 'General':
        if not current_window:
            return


def chat_win_ref(to):
    global last_general_msgs
    to = Application.chat_lib.msgs()
    if current_window:
        for c in current_window.children.copy().values():
            c.destroy()

        y = 0

        if to != last_general_msgs or snaph is None:
            last_general_msgs = to

            for i in to:
                l = Label(current_window, f'{i}')
                l.set_position(0, y)
                l.set_size(*l.size_hint())
                y += l.height

        current_window.update()

def wrapper(*args, **kwargs):
    send_message(*args, **kwargs)
    chat_win_ref(last_general_msgs)

Application.load_chat = lchat
Application.chat_win_ref = chat_win_ref
send_message = Application.send_message
Application.send_message = wrapper

class Offsetclass:
    def __init__(self):
        self.x = 0
        self.y = 0

class BufferedWnd(tk_window.TkinterWindow):
    def __init__(self, w):
        self.offset_class = Offsetclass()
        super().__init__(w)
        self.last_frame = None
        self.bg = None
        self.on_scroll(self._scrl)

    def _scrl(self, d, x, y):
        if d > 0:
            if self.offset_class.y + d > 0:
                print('Too up')
                return
        if d < 0:
            if -self.offset_class.y + d > self.children_height - self.height:
                print('Too down')
                return
        self.offset_class.y += d
        print(self.offset_class.y, d)
        self.update()

    def update(self, use_cached=False):
        if Application.default_bg != self.bg:
            self.bg = Application.default_bg
            self.window_background = widget_extensions.hex_str_to_int(Application.default_bg)

        if not use_cached or self.last_frame is None:
            super().update()
            self.last_frame = self._surface.makeImageSnapshot()
        elif self.last_frame is not None:
            canvas = self.get_canvas()
            if canvas is None:
                return

            canvas.clear(self.window_background)
            canvas.drawImage(self.last_frame, 0, 0)
            self.swap_buffers()
            self.dirty = False

def run_mainloop():
    global current_window
    try:
        Application.chat_window
    except KeyError:
        print('Non-final ML')
        return

    Application.chat_window.destroy = lambda: None
    current_window = BufferedWnd(Application.chat_window)
    current_window.offset_class = Offsetclass()
    abstract.mainloop()