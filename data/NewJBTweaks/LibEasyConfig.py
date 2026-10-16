#meta
# {"req": ["LibSettings"]}
import itertools
import sys
import tkinter
import traceback
from collections.abc import MutableMapping

from LibSettings import SettingsAPI

_own_globals = globals()   # globals самого LibEasyConfig
_cache = {}                # rfp -> EasyConfigData
_flags = {}                # rfp -> {key: bool}, одноразовые флаги кнопок (только в памяти)
_headers = set()           # rfp твиков, для которых уже создан заголовок на странице
_name_counter = itertools.count()

PAGE = 'EasyConfig'


class EasyConfigData(MutableMapping):
    """Живое представление хранилища твика: запись сразу попадает в jaildata-словарь."""

    def __init__(self, tapi):
        self.tapi = tapi

    @property
    def _store(self):
        return self.tapi.GetTweakStorage()

    @property
    def _btn(self):
        return _flags.setdefault(self.tapi.rfp, {})

    def __getitem__(self, k):
        if k in self._btn:
            return self._btn[k]
        return self._store[k]

    def __setitem__(self, k, v):
        if k in self._btn:
            self._btn[k] = bool(v)
        else:
            self._store[k] = v

    def __delitem__(self, k):
        del self._store[k]

    def __iter__(self):
        yield from self._btn
        yield from self._store

    def __len__(self):
        return len(self._btn) + len(self._store)

    def __repr__(self):
        return f'<EasyConfigData {self.tapi.name} {self.to_dict()}>'

    def save(self):
        self.tapi.SaveTweakStorage()

    def to_dict(self):
        return dict(self)


def _caller_tapi():
    f = sys._getframe(1)
    try:
        while f is not None:
            g = f.f_globals
            if g is not _own_globals:          # пропускаем свои же фреймы
                tapi = g.get('__twkapi__')
                if tapi is not None:
                    return tapi
            f = f.f_back
    finally:
        del f
    raise RuntimeError('вызвано вне твика')


def _cfg_for(tapi):
    cfg = _cache.get(tapi.rfp)
    if cfg is None:
        cfg = _cache[tapi.rfp] = EasyConfigData(tapi)
    return cfg


def get_cfg(as_dict=False):
    cfg = _cfg_for(_caller_tapi())
    return cfg.to_dict() if as_dict else cfg


def _safe_call(cb, *args):
    if cb is None:
        return
    try:
        cb(*args)
    except Exception:
        traceback.print_exc()


def create(wtype, text, key, callback=None, default=None):
    """Создаёт настройку на странице EasyConfig для вызывающего твика.

    wtype: 'checkbox' | 'entry' | 'button'
      checkbox / entry - значение хранится в jaildata, callback(value)
      button - одноразовый флаг, только в памяти, после рестарта False, callback(True)
    Значение потом читается через get_cfg()[key].
    """
    wtype = wtype.lower()
    if wtype not in ('checkbox', 'entry', 'button'):
        raise ValueError(f'Unknown wtype {wtype!r}')

    tapi = _caller_tapi()          # захватываем сейчас: в момент отрисовки стека твика уже нет
    cfg = _cfg_for(tapi)

    if wtype == 'button':
        _flags.setdefault(tapi.rfp, {})[key] = False
    else:
        if default is None:
            default = False if wtype == 'checkbox' else ''
        cfg._store.setdefault(key, default)

    if tapi.rfp not in _headers:
        _headers.add(tapi.rfp)
        SettingsAPI.create_widget(PAGE, 'Label', text=f'--- {tapi.name[4:]} ---')

    def secreate(win):
        name = f'setts-runtime-ec{next(_name_counter)}'   # префикс нужен для очистки при ребилде

        if wtype == 'checkbox':
            var = tkinter.BooleanVar(master=win, value=bool(cfg._store.get(key, default)))

            def toggled():
                v = var.get()
                cfg[key] = v
                cfg.save()
                _safe_call(callback, v)

            w = tkinter.Checkbutton(win, name=name, text=text, variable=var,
                                    command=toggled, anchor='w')
            w._var = var   # держим ссылку, иначе tk-переменную соберёт GC

        elif wtype == 'entry':
            w = tkinter.Frame(win, name=name)
            tkinter.Label(w, text=text).pack(side='left')
            var = tkinter.StringVar(master=w, value=str(cfg._store.get(key, default)))
            ent = tkinter.Entry(w, textvariable=var)
            ent.pack(side='left', fill='x', expand=True)

            def commit(e=None):
                v = var.get()
                if cfg._store.get(key) == v:
                    return
                cfg[key] = v
                cfg.save()
                _safe_call(callback, v)

            ent.bind('<Return>', commit)
            ent.bind('<FocusOut>', commit)
            w._var = var

        else:  # button
            def label():
                return f'{text} [✓]' if cfg[key] else text

            def clicked():
                cfg[key] = True
                w.config(text=label())
                _safe_call(callback, True)

            w = tkinter.Button(win, name=name, text=label(), command=clicked)

        for x in (w, *w.winfo_children()):
            x.bind('<MouseWheel>', win._set_offset)   # прокрутка страницы колесом
        return w

    # secreate пробрасывается через **kwargs в SettsElement
    SettingsAPI.create_widget(PAGE, 'ECWidget', secreate=secreate)


SettingsAPI.create_page(PAGE)