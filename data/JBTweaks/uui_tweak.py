import queue
import threading
import traceback
import tkinter
from tkinter import TclError

import time

from uui.backend.win32 import Win32WindowThreaded
from uui.backend.win32 import user32
from uui.core import EventProc

def th_exh(args: threading.ExceptHookArgs):
    print(f'[er] TRACE TREAD:\n{args.thread}\n{'\n'.join(traceback.format_exception(args.exc_type, tb=args.exc_traceback, value=args.exc_value))}')


threading.excepthook = th_exh

event_pr = EventProc()


OFFSET_Y = 30
OFFSET_X = 7

r_main: tkinter.Tk = globals()['main']
wnd = Win32WindowThreaded('TEST', r_main.winfo_x()+OFFSET_X, r_main.winfo_y() + OFFSET_Y, r_main.winfo_width(), r_main.winfo_height(), True, lambda w, e: event_pr.process(e), None)
wnd.start()

tk_hwnd = r_main.winfo_id()

render = wnd._w.render

q = queue.Queue()

def recall_in_tk_loop():
    while not q.empty():
        fnc, args, kw = q.get()
        fnc(*args, **kw)

    r_main.after(50, recall_in_tk_loop)

def recall_in_tk(fnc):
    def wrapper(*args, **kwargs):
        q.put((fnc, args, kwargs))
    return wrapper

recall_in_tk_loop()


@event_pr.dec('LMBClick')
def mouse_down(e):
    simulate_click(e.x, e.y)

@event_pr.dec('LMBRelease')
def mouse_up(e):
    simulate_click(e.x, e.y)


@recall_in_tk
def simulate_click(x, y):
    global clickable
    # Итерируемся по списку. Первый, в кого попали — тот и съел клик
    for item in clickable:
        w_x, w_y, w_w, w_h, wid = item['x'], item['y'], item['w'], item['h'], item['widget']
        actual_y = w_y + OFFSET_Y
        w_x += OFFSET_X
        if w_x <= x <= w_x + w_w and actual_y <= y <= actual_y + w_h:
            if wid.cget('state') != 'disabled':
                wid.invoke()
            return  # Сразу выходим, клик обработан верхним элементом!


r_main: tkinter.Tk = globals()['main']

def _thread():
    while globals().get('work', True):
        time.sleep(0.1)
    print('SHUTDOWN UUI')
    wnd.shutdown()
    wnd.finish_event.wait()
    print('OK')

render.prepare_brushes(['#ff000022', '#00ff0022'])

has_brushes = {'#ff000022', '#00ff0022'}

rot = 0

clickable = []


def get_z_ordered_widgets(parent: tkinter.Tk) -> list[tkinter.Widget]:
    try:
        # wm stackorder возвращает список путей виджетов (например, ['.!button', '.!frame.!button2'])
        # в порядке их наложения на экране (снизу вверх)
        raw_paths = parent.tk.call('wm', 'stackorder', parent)

        # Переводим строковые пути Tcl обратно в объекты Python-виджетов
        ordered_widgets = []
        for path in raw_paths:
            # Находим Python-объект виджета по его Tcl-пути
            try:
                widget = parent.nametowidget(path)
            except TclError:
                print(f'[warn] failed to load widget at {path!r}')
                continue
            ordered_widgets.append(widget)

        return ordered_widgets
    except tkinter.TclError:
        # Если окон еще нет на экране или они не смаплены, wm stackorder может выкинуть ошибку
        return []


def ref_lop():
    global has_brushes, rot, clickable
    rot += 3
    req_brushes = []

    display_list = []
    temp_clickable = []

    # 1. Получаем абсолютно точный Z-список виджетов от Tkinter
    z_ordered = get_z_ordered_widgets(r_main)

    # Чтобы быстро искать Z-индекс, сделаем словарь: {виджет: число_от_0_до_N}
    z_indices = {widget: index for index, widget in enumerate(z_ordered)}

    # 2. Твой обычный сбор геометрии
    def collect_widgets(_m: tkinter.Misc, ox, oy):
        for _w in _m.children.values():
            if not _w.winfo_exists() or not _w.winfo_ismapped():
                continue

            x, y = _w.winfo_x(), _w.winfo_y()
            w, h = _w.winfo_width(), _w.winfo_height()
            abs_x, abs_y = ox + x, oy + y

            # Получаем реальный Z-индекс.
            # Если виджета нет в списке wm stackorder (например, это невизуальный контейнер),
            # даем ему дефолтный 0
            z = z_indices.get(_w, 0)

            # Добавляем фон
            display_list.append((z, 'rect', {
                'x1': abs_x, 'y1': abs_y, 'x2': abs_x + w, 'y2': abs_y + h,
                'bg': _w['bg'], 'thick': _w['highlightthickness'], 'color': _w['highlightcolor']
            }))

            # Добавляем текст
            try:
                if _w['text']:
                    display_list.append((z, 'text', {
                        'x1': abs_x, 'y1': abs_y, 'x2': abs_x + w, 'y2': abs_y + h,
                        'text': _w['text'], 'fg': _w['fg']
                    }))
                    if _w['fg'] not in has_brushes:
                        req_brushes.append(_w['fg'])
            except tkinter.TclError:
                pass

            if _w['bg'] not in has_brushes:
                req_brushes.append(_w['bg'])

            # Запоминаем кнопку для кликов
            if isinstance(_w, tkinter.Button):
                temp_clickable.append({
                    'z': z, 'x': abs_x, 'y': abs_y, 'w': w, 'h': h, 'widget': _w
                })

            # Рекурсивный обход детей
            collect_widgets(_w, abs_x, abs_y)

    collect_widgets(r_main, 0, 0)

    # 3. Сортируем для отрисовки (по возрастанию Z)
    display_list.sort(key=lambda item: item[0])

    # 4. Рендеринг
    render.start_paint()
    for z, cmd_type, p in display_list:
        render.clip_region(*(p['x1'], p['y1'], p['x2'], p['y2']))
        if cmd_type == 'rect':
            render.draw_rectangle(p['x1'], p['y1'], p['x2'], p['y2'], p['bg'], p['thick'], p['color'])
        elif cmd_type == 'text':
            render.draw_text(p['x1'], p['y1'], p['x2'], p['y2'], p['text'], p['fg'], ['Inter', 13], 'center', 'center')
        render.remove_clip_region()
    render.end_paint()

    # 5. Сортируем для кликов (по убыванию Z — верхние первыми ловят клик)
    temp_clickable.sort(key=lambda c: c['z'], reverse=True)

    # Атомарно обновляем глобальный список
    clickable = temp_clickable

    if req_brushes:
        render.prepare_brushes(req_brushes)
        has_brushes.update(req_brushes)

threading.Thread(target=_thread, name='UUITweakWaiter', daemon=True).start()

GWL_STYLE = -16
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000

WS_POPUP = 0x80000000
WS_VISIBLE = 0x10000000

SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
SW_HIDE = 0
SW_SHOW = 5

def frame_loop():
    try:
        ref_lop()
    except Exception as _ex:
        print('[warn] ref lop failure, restart')
    r_main.after(33, frame_loop)


def make_overrideredirect(w):
    user32.SetWindowLongW(w.hwnd, GWL_STYLE, WS_POPUP | WS_VISIBLE)
    user32.SetWindowPos(w.hwnd, 0, 0, 0, 0, 0,
                        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_FRAMECHANGED)

    ex_style = user32.GetWindowLongW(w.hwnd, GWL_EXSTYLE)

    if ex_style is None:
        ex_style = 0

    ex_style = (ex_style & ~WS_EX_APPWINDOW) | WS_EX_TOOLWINDOW
    user32.SetWindowLongW(w.hwnd, GWL_EXSTYLE, ex_style)


wnd.call_win32(make_overrideredirect, (wnd,), {})


def on_configure(event: tkinter.Event):
    if event.widget == r_main:
        user32.SetWindowPos(wnd.hwnd, -1, event.x+OFFSET_X, event.y + OFFSET_Y, event.width, event.height, SWP_NOACTIVATE)
        render._resize(event.width, event.height)

def hide(e):
    if e.widget == r_main:
        user32.SetWindowPos(wnd.hwnd, -2, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

def show(e):
    if e.widget == r_main:
        user32.SetWindowPos(wnd.hwnd, -1, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

def unmap(e):
    if e.widget == r_main:
        user32.ShowWindow(wnd.hwnd, 0)

def _map(e):
    if e.widget == r_main:
        user32.ShowWindow(wnd.hwnd, 5)
        show(e)

r_main.bind('<Configure>', on_configure)

r_main.bind('<FocusOut>', hide)
r_main.bind('<FocusIn>', show)
r_main.bind('<Unmap>', unmap)
r_main.bind('<Map>', _map)

r_main.after(100, frame_loop)