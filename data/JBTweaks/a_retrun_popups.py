import os.path
import sys
import tkinter


# USE Tk OR POPUP
use_tk = False



class _Obj:
    def __init__(self, v):
        self.v = v.replace(' ', '_')
        print(f'[{self.v}] init emulation for {self.v}')

    def __getattribute__(self, item):
        if item == 'v':
            return super().__getattribute__(item)
        print(f'[{self.v}] emulating {item}')
        return _Obj(f'{self.v}.{item}')

    def __call__(self, *args, **kwargs):
        print(f'[{self.v}] {args, kwargs}')

class Popup(tkinter.Frame):
    def __init__(self, master: tkinter.Tk = None, x: int = -1, y: int = -1, size=None,
                 style=None, title: str = 'Popup', map_on_init=True):
        #if master is None:
        #    raise TypeError(f'Master win is not provided: {app_root_window}')
        if size is None:
            size = [300, 300]
        if master is None:
            master = None
        self.style = style
        self.size = size

        self.root_frame = tkinter.Frame(master, width=size[0], height=size[1], highlightthickness=2)
        #self.root_frame.pack_propagate(False)

        self.close_btn = tkinter.Button(self.root_frame, text='X', command=self.root_frame.place_forget)
        self.close_btn.pack(anchor='ne')
        self.title_lbl = tkinter.Label(self.root_frame, text=title)
        self.title_lbl.place(x=0, y=0)

        super().__init__(self.root_frame, width=size[0], height=size[1], highlightthickness=2)
        self.pack_propagate(True)



        if style is not None:
            self.configure(bg=style[0], highlightcolor=style[1])
            self.root_frame.configure(bg=style[0], highlightcolor=style[1])
            self.close_btn.configure(bg=style[0], fg=style[1], font=style[2])
            self.title_lbl.configure(bg=style[0], fg=style[1], font=style[2])

        self.root_frame.bind('<Button-1>', self._start_move)
        self.root_frame.bind('<B1-Motion>', self._move)

        self._start_x = 0
        self._start_y = 0
        if map_on_init:
            self.root_frame.place(x=0, y=0)
            self.pack()

    def destroy(self):
        self.root_frame.place_forget()

    def update_idletasks(self):
        super().update_idletasks()
        self.root_frame.update_idletasks()
        self.size = [self.root_frame.winfo_width(), self.root_frame.winfo_height()]
        print(self.size)

    def geometry(self, s):
        if '+' in s:
            s = s.split('+')[0].split('x')
        else:
            s = s.split('x')
        self.configure(width=s[0], height=s[1])


    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return _Obj(f'Popup"{self.title_lbl['text']}"ItemEmulate:{item}')


    def lift(self):
        self.root_frame.lift()

    def _start_move(self, event=None):
        self.root_frame.lift()
        if hasattr(event, 'x') and hasattr(event, 'y'):
            self._start_x = event.x
            self._start_y = event.y

    def _move(self, event):
        x = self.root_frame.winfo_x() + (event.x - self._start_x)
        y = self.root_frame.winfo_y() + (event.y - self._start_y)
        #self.title_lbl['text'] = f'{self.root_frame.winfo_x()}/{self.root_frame.master.winfo_width() - self.root_frame.winfo_width()} {self.root_frame.winfo_y()}/{self.root_frame.master.winfo_height() - self.root_frame.winfo_height()}'
        if 0 <= x <= self.root_frame.master.winfo_width() - self.root_frame.winfo_width():
            self.root_frame.place(x=x)
        if 0 <= y <= self.root_frame.master.winfo_height() - self.root_frame.winfo_height():
            self.root_frame.place(y=y)

    def update_info(self):
        self._start_x = 0
        self._start_y = 0
        self.update_idletasks()

    def resizable(self, x, y):
        if x or y:
            self.pack_propagate(True)
        else:
            self.pack_propagate(True)

    def title(self, t):
        self.title_lbl['text'] = t

    def protocol(self, prot, callback):
        if prot == 'WM_DELETE_WINDOW':
            self.close_btn['command'] = callback

if not use_tk:
    Tk = Popup
    sys.modules['tkinter'].Tk = Popup
else:
    class ModTK(tkinter.Tk):
        def __init__(self, *args, **kwargs):
            super().__init__()
        def __getattribute__(self, item):
            try:
                return super().__getattribute__(item)
            except AttributeError:
                return _Obj(f'ModTKEmulate:{item}')
    Popup = ModTK
    Tk = tkinter.Tk