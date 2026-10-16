import argparse
import subprocess
import os
import sys
import ast
import importlib.util
import inspect
import json
import pathlib
import random
import textwrap
import threading
import time
import tkinter.messagebox
import traceback
import types
from typing import Any

from collections import defaultdict

from data.lib import ui


threads_alive = True


class Event:
    def __init__(self, name):
        self.name = name
        self._functions = []

    def __call__(self, fnc):
        self._functions.append(fnc)
        return fnc

    def fire(self):
        [i() for i in self._functions]

    def clear(self):
        self._functions.clear()


def jailinf(s):
    print(f'\x1b[35;1m[Jailbreak] {s}\x1b[0m'.replace('] [', ']['))


def twkinf(s, clr):
    print(f'\x1b[{clr}m[Tweak] {s}\x1b[0m'.replace('] [', ']['))


def gettwkinf(name, clr):
    return lambda *s: twkinf(f'[{name}] {' '.join(str(i) for i in s)}', clr)


class JSONTweakData:
    def __init__(self, fp):
        self.fp = fp
        try:
            with open(fp, 'r', encoding='utf-8') as fl:
                self._json = json.load(fl)
        except (FileNotFoundError, json.JSONDecodeError):
            self._json = {"TweakSettings": {}}
            self.commit()

    def get_tweak(self, twk):
        if twk not in self._json['TweakSettings']:
            self._json['TweakSettings'][twk] = {}
        return self._json['TweakSettings'][twk]

    def set_tweak_pairs(self, twk, *pairs):
        if twk not in self._json['TweakSettings']:
            self._json['TweakSettings'][twk] = {}
        t = self._json['TweakSettings'][twk]
        for k, v in pairs:
            t[k] = v

    def commit(self):
        with open(self.fp, 'w', encoding='utf-8') as fl:
            jailinf('Saved jaildata')
            json.dump(self._json, fl, indent=2, ensure_ascii=False)


class TweakAPI:
    _created_apis = []

    def __init__(self, fp, rfp, name, mod):
        if fp in self._created_apis:
            raise ValueError(f'Loaded already loaded {fp}')
        self._created_apis.append(fp)
        self.fp = fp
        self.rfp = rfp
        self.name = name
        self.module: types.ModuleType = mod

    def __repr__(self):
        return f'<TweakAPI {self.name} ({self.fp})>'

    def GetTweakMemory(self):
        return JModule.ByTweakMemory[self.name]

    def GetTweakStorage(self):
        return tweak_settings.get_tweak(self.rfp)

    @staticmethod
    def SaveTweakStorage():
        tweak_settings.commit()


def make_tweak_import(tapi, tweak_dir):
    orig_import = __builtins__.__import__ if isinstance(__builtins__, types.ModuleType) else __builtins__['__import__'] # noqa

    def custom_import(name: str, globals=None, locals=None, fromlist=(), level=0):
        if name == 'TweakAPI':
            return tapi

        if name in tweaks:
            return tweaks[name].module

        path_added = False
        if tweak_dir not in sys.path:
            sys.path.insert(0, tweak_dir)
            path_added = True

        try:
            mod = orig_import(name, globals, locals, fromlist, level)
            fp = getattr(mod, '__file__', None)
            if fp:
                pth = pathlib.Path(fp)
                if pth.parent.name == 'NewJBTweaks':
                    raise ValueError('Cannot import tweak as module, write it in req field in meta')

            return mod
        finally:
            if path_added and tweak_dir in sys.path:
                sys.path.remove(tweak_dir)

    return custom_import


def _execute(fp, rfp, internal_name, code_text, metadata):
    abs_rfp = os.path.abspath(rfp)
    tweak_dir = os.path.dirname(abs_rfp) if os.path.isfile(abs_rfp) else abs_rfp

    # Добавляем директорию твика в sys.path для корректной работы обычных импортов
    if tweak_dir not in sys.path:
        sys.path.insert(0, tweak_dir)

    mod_name = f'tweak_{internal_name}'
    mod = types.ModuleType(mod_name)

    tapi = TweakAPI(fp.replace('.py', ''), rfp, internal_name, mod)

    # Создаем виртуальный модуль

    mod.__file__ = abs_rfp
    mod.__package__ = ''
    mod.__doc__ = None

    real_builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
    tweak_builtins = real_builtins.copy() # noqa
    tweak_builtins['__import__'] = make_tweak_import(tapi, tweak_dir)

    mod.__dict__['__builtins__'] = tweak_builtins
    mod.__dict__['__twkapi__'] = tapi
    mod.__dict__['TweakMemory'] = mod.__dict__

    if metadata.get('reprint', True):
        mod.__dict__['print'] = gettwkinf(internal_name, metadata.get('printcolor', 32))

    JModule.ByTweakMemory[internal_name] = mod.__dict__

    cpl = compile(code_text, abs_rfp, 'exec')
    jailinf(f'[Tweaker] executing {fp} ({internal_name})')
    exec(cpl, mod.__dict__)

    return tapi


def execute_universal(fp, rq=None):
    clean_fp = fp[:-3] if fp.endswith('.py') else fp
    rfp = f'./data/NewJBTweaks/{clean_fp}'

    if not os.path.exists(rfp) and not os.path.exists(rfp + '.py'):
        raise Exception(f'Cannot resolve tweak/requirement {rfp}{f" required by {rq}" if rq is not None else ''}')

    if rfp in ignore:
        raise Exception(f'Cannot load {rfp} because of LoadIgnore{f" required by {rq}" if rq is not None else ''}')

    try:
        if os.path.isdir(rfp):
            return execute_bundle(clean_fp)
        else:
            return execute_file(clean_fp + '.py')
    except Exception as _ex:
         if _ex.args[0] == 'JFlagSkipTweak':
             jailinf(f'{clean_fp} Skip - JFlagSkipTweak')
         else:
             raise _ex


def execute_bundle(fp):
    clean_key = fp.replace('.py', '')
    if clean_key in loaded_tweaks:
        return tweaks.get(clean_key)

    rfp = f'./data/NewJBTweaks/{fp}'
    meta_path = f'{rfp}/metadata.json'

    if not os.path.exists(meta_path):
        return None

    with open(meta_path, 'r', encoding='utf-8') as fl:
        metadata = json.load(fl)

    if metadata.get('disabled', False):
        return None

    loaded_tweaks.append(fp)
    internal_name = f'{hex(random.randint(0, 0xffff))[2:].zfill(4)}{fp}'

    # Загружаем зависимости
    for _req in metadata.get('req', []):
        r_tapi = execute_universal(_req, clean_key)
        if r_tapi is not None:
            tweaks[_req] = r_tapi

    main_filename = metadata.get('main_file', 'main.py')
    with open(f'{rfp}/{main_filename}', 'r', encoding='utf-8') as fl:
        code_text = fl.read()

    tapi = _execute(fp, f'{rfp}/{main_filename}', internal_name, code_text, metadata)
    tweaks[fp] = tapi
    return tapi


def execute_file(fp):
    clean_key = fp.replace('.py', '')
    if clean_key in loaded_tweaks:
        return tweaks.get(clean_key)
    if clean_key in ignore:
        raise Exception(f'Cannot load {clean_key} because of LoadIgnore')

    rfp = f'./data/NewJBTweaks/{fp}'
    if not os.path.exists(rfp):
        return None

    with open(rfp, 'r', encoding='utf-8') as fl:
        lines = fl.readlines()

    metadata = {}
    for idx, line in enumerate(lines):
        candidate = line.lower().replace(' ', '').strip()
        if candidate in ['#m', '#meta', '#metadata']:
            if idx + 1 < len(lines):
                meta_line = lines[idx + 1]
                try:
                    _json = meta_line[meta_line.find('{'):meta_line.rfind('}') + 1]
                    metadata = json.loads(_json)
                except Exception:
                    pass
            break

    if metadata.get('disabled', False):
        return None

    loaded_tweaks.append(clean_key)
    internal_name = f'{hex(random.randint(0, 0xffff))[2:].zfill(4)}{clean_key}'

    # Загружаем зависимости
    for _req in metadata.get('req', []):
        r_tapi = execute_universal(_req, clean_key)
        if r_tapi is not None:
            tweaks[_req] = r_tapi

    code_text = ''.join(lines)
    tapi = _execute(fp, rfp, internal_name, code_text, metadata)
    tweaks[clean_key] = tapi
    return tapi


parser = argparse.ArgumentParser(description="Менеджер запусков")

parser.add_argument('--load-ignore', nargs='+', help='Список элементов для игнорирования', default=[])
parser.add_argument('--load-only', nargs='+', help='Список элементов только для загрузки', default=None)
parser.add_argument('--skip-non-load-only', action='store_true', help='Пропускать то что не в load-only')
parser.add_argument('--app-flags', nargs='+', help='Флаги для приложения', default=[])

args = vars(parser.parse_args())

print(args)

ignore = args['load_ignore']
load_only = args['load_only'] or None
skip_non_load_only = args['skip_non_load_only']
app_flags = args['app_flags']


def load_tweaks():
    global stage, ignore
    stage = 'TweakLoading'
    os.makedirs('./data/NewJBTweaks', exist_ok=True)

    if not os.path.exists('./data/NewJBTweaks/LoadIgnore.1'):
        with open('./data/NewJBTweaks/LoadIgnore.1', 'w'): pass

    with open('./data/NewJBTweaks/LoadIgnore.1') as fl:
        ignore.extend(fl.read().split('\n'))

    if not os.path.exists('./data/NewJBTweaks'):
        return

    for _i in os.listdir('./data/NewJBTweaks'):
        clean_name = _i.replace('.py', '')

        if clean_name in ignore:
            jailinf(f'Skip {clean_name} LoadIgnore')
            continue

        if load_only:
            if clean_name not in load_only:
                jailinf(f'Skip {clean_name} LoadOnly')
                continue

        tapi = execute_universal(_i)
        if tapi is not None:
            tweaks[clean_name] = tapi

    stage = '...'


class KeyRegisterNotifier:
    def __init__(self, dct):
        self._dct = dct
        # self._thread = threading.Thread(target=self._spyer, daemon=True)
        self._hooks = {}
        self._has_hooks_event = threading.Event()
        # self._thread.start()

    def hook(self, key, callback):
        self._hooks[random.randint(0, 0xffff)] = {'key': key, 'func': callback}
        if not self._has_hooks_event.is_set():
            self._has_hooks_event.set()

    def _spyer(self):
        while threads_alive:
            if not self._hooks:
                self._has_hooks_event.wait()
                self._has_hooks_event.clear()

            to_rm = []

            for _k, _v in self._hooks.items():
                if _v['key'] in self._dct:
                    _v['func'](_v['key'])
                    to_rm.append(_k)

            for _i in to_rm: del self._hooks[_i]

            time.sleep(0.5)


class JailbreakApi:
    on_mainloop = Event('on_mainloop')
    p_mainloop_check = Event('p_mainloop_check')
    on_init = Event('on_init')
    on_early_init = Event('on_early_init')
    on_ready_window = Event('on_ready_window')
    on_exit = Event('on_exit')
    on_final_mainloop = Event('on_final_mainloop')

    _tweaks_loaded = False

    @classmethod
    def GetCallingFromTweak(cls, stack=None):
        f_tweak = 'UNKNOWN'
        for _i in traceback.extract_stack() if stack is None else stack:
            if 'NewJBTweaks' in _i.filename:
                f_tweak = _i.filename
                break
        return f_tweak

    @classmethod
    def ExecuteInGlobalNamespace(cls, code):
        exec(code, glb)


JailbreakApi.on_init(load_tweaks)


class LineHookTransformer(ast.NodeTransformer):
    """
    Трансформер AST, который находит тело функции и оборачивает
    каждое выражение/присваивание в вызов хука.
    """

    def __init__(self, hook_func_name, active_lineno):
        self.hook_func_name = hook_func_name
        self.active_lineno = active_lineno

    def visit_FunctionDef(self, node):
        # Обходим дочерние узлы
        self.generic_visit(node)

        new_body = []
        for stmt in node.body:
            # Получаем номер строки исходника
            lineno = getattr(stmt, 'lineno', None)

            if lineno is not None and lineno in self.active_lineno:
                # Генерируем AST-узел: _hook_func(lineno, locals())
                hook_call = ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id=self.hook_func_name, ctx=ast.Load()),
                        args=[
                            ast.Constant(value=lineno),
                            ast.Call(
                                func=ast.Name(id='locals', ctx=ast.Load()),
                                args=[],
                                keywords=[]
                            )
                        ],
                        keywords=[]
                    )
                )
                ast.copy_location(hook_call, stmt)

                new_body.append(stmt)
                new_body.append(hook_call)
            else:
                new_body.append(stmt)

        node.body = new_body
        return node


class HookedFunction:
    def __init__(self, fnc):
        self._orig_f = fnc
        self._f = fnc
        self._line_hooks = defaultdict(list)
        self._recompiled = False
        self.after_func = []

    def after_hook(self, fnc):
        self.after_func.append(fnc)
        return fnc

    def line_hook(self, lineno):
        def decorator(fnc):
            self._line_hooks[lineno].append(fnc)
            self._recompiled = False
            return fnc
        return decorator

    def _dispatch_hook(self, lineno, local_vars):
        for h in self._line_hooks[lineno]:
            h(local_vars)

    def _recompile(self):
        stime = time.time()
        src = inspect.getsource(self._orig_f)
        src = textwrap.dedent(src)

        tree = ast.parse(src)

        transformer = LineHookTransformer(hook_func_name='__line_hook__', active_lineno=self._line_hooks.keys())
        tree = transformer.visit(tree)
        ast.fix_missing_locations(tree)

        compiled_code = compile(tree, filename=inspect.getfile(self._orig_f), mode='exec')

        func_code = None
        for const in compiled_code.co_consts:
            if isinstance(const, type(self._orig_f.__code__)) and const.co_name == self._orig_f.__name__:
                func_code = const
                break

        if func_code is None:
            raise RuntimeError("Не удалось извлечь скомпилированный байткод функции")

        new_globals = self._orig_f.__globals__.copy()
        new_globals['__line_hook__'] = self._dispatch_hook

        self._f = type(self._orig_f)(
            func_code,
            new_globals,
            self._orig_f.__name__,
            self._orig_f.__defaults__,
            self._orig_f.__closure__
        )
        self._recompiled = True
        print(f'[HookedFunction {self._f.__name__}] Recompiled {round(time.time() - stime, 4)}s')

    def __call__(self, *args, **kwargs):
        if not self._recompiled:
            self._recompile()
        try:
            return self._f(*args, **kwargs)
        except Exception as _ex:
            _ex.add_note(f'HookedFunction {self._orig_f.__name__} failed')
            raise _ex
        finally:
            [i() for i in self.after_func]



class JModule:
    API = JailbreakApi
    SharedMemory = {}
    ByTweakMemory: dict[str, dict[str, Any]] = {}
    Event = Event

    __file__ = '<J>'
    __name__ = 'JModule'

    @classmethod
    def SetRestartFlag(cls):
        global restart
        restart = True
        jailinf('Restart flag set')

    @classmethod
    def GetTweak(cls, fn):
        if fn not in tweaks:
            raise KeyError(fn, tweaks.keys())
        return tweaks[fn]

    @classmethod
    def get_hooked(cls, in_app_name):
        attr = getattr(app, in_app_name)
        if not isinstance(attr, HookedFunction):
            h = HookedFunction(attr)
            setattr(app, in_app_name, h)
            return h
        return attr

    @classmethod
    def hook(cls, in_app_name, line_no):
        def decorator(fnc):
            attr = getattr(app, in_app_name)
            if isinstance(attr, HookedFunction):
                attr.line_hook(line_no)(fnc)
            else:
                h = HookedFunction(attr)
                h.line_hook(line_no)(fnc)
                setattr(app, in_app_name, h)
            return fnc

        return decorator

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            raise AttributeError(f'{item!r} not exists in JModule runtime')

    @classmethod
    def _G(cls):
        return glb

JModule.rfp = os.path.abspath(__file__)


class JailModule:
    def __init__(self, d):
        self._d = d

    def __getattr__(self, item):
        try:
            return self._d[item]
        except KeyError:
            raise AttributeError(f'{item!r}, aval {list(self._d.keys())}')

    def __setattr__(self, key, value):
        if key == '_d':
            super().__setattr__(key, value)
        else:
            self._d[key] = value


def _f():
    pass

functype = _f.__class__


class Win(ui.Win):
    q = []

    def __init__(self, **kwargs):
        stack = traceback.extract_stack()

        lines = [i.line for i in stack]
        if 'main = Win()' in lines:
            glb['main'] = self
            JailbreakApi.on_early_init.fire()
            super().__init__(**kwargs)
            JailbreakApi.on_init.fire()
            jailinf(f'Window created successfully! Test (winfo_exists): {self.winfo_exists()}')
            self.after(100, self._cpl_recall)
            self._j = True
            self.__mainloop_afters = []
        else:
            super().__init__(**kwargs)
            self._j = False

    def _cpl_recall(self):
        for i, cb_res in self.q:
            try:
                res = i()
            except BaseException as _ex:
                res = _ex
            if cb_res:
                cb_res(res)
            else:
                if isinstance(res, BaseException):
                    raise res
        self.q.clear()
        self.after(100, self._cpl_recall)

    @property
    def report_callback_exception(self):
        return super().report_callback_exception

    @report_callback_exception.setter
    def report_callback_exception(self, value):
        if self._j:
            JailbreakApi.on_ready_window.fire()

    def mainloop(self, n=0):
        if self._j:
            try:
                JailbreakApi.p_mainloop_check.fire()
            except Exception as _ex:
                if _ex.args[0] == 'JFlagCancelMainloop':
                    jailinf('Mainloop canceled')
                    return
                else:
                    raise _ex
            JailbreakApi.on_mainloop.fire()
        for i in self.__mainloop_afters:
            try:
                i()
            except Exception as _ex:
                jailinf(f'ML After {i} failed: {_ex.__class__.__name__}: {_ex}')
        super().mainloop()

    def __setattr__(self, key, value):
        if key != 'mainloop':
            super().__setattr__(key, value)
            return

        if not hasattr(self, 'mainloop'):
            jailinf(f'Added First Mainloop {value}')
            super().__setattr__(key, value)
        elif isinstance(value, functype):
            self.__mainloop_afters.append(value)
            jailinf(f'Added MLAfter {value}')

    def quit(self):
        super().quit()

    @classmethod
    def getWin(cls) -> 'Win':
        return glb.get('main', None)

    @classmethod
    def recall(cls, fnc, cb_res=None):
        cls.q.append((fnc, cb_res))

def sys_excepthook(exc_type, value, tb):
    ex = ''.join(traceback.format_exception(exc_type, value, tb))
    wn = Win.getWin()
    if wn:
        wn.recall(lambda: tkinter.messagebox.showerror(f'Error in MainThread', ex))
    wn_info = ''
    if wn.__class__ is not Win:
        wn_info = f'\nWindow MRO: {', '.join(f'{i}' for i in wn.__class__.__mro__)}'
    print(ex + f'\nJN Excepthook:\nWindow:\n{object.__repr__(wn)}{wn_info}', file=sys.stderr)
    try:
        input('Press any key to exit')
    except KeyboardInterrupt:
        pass

def t_excepthook(args: threading.ExceptHookArgs):
    ex = ''.join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
    wn = Win.getWin()
    if wn:
        wn.recall(lambda: tkinter.messagebox.showerror(f'Error in thread {args.thread.name}', ex))
    print(f'Exception in thread {args.thread.name}:\n{ex}' + f'\nJN Excepthook:\nWindow:\n{wn}', file=sys.stderr)

loaded_tweaks = []
tweaks: dict[str, TweakAPI] = {}
lib_tweaks = defaultdict(list)
tweak_settings = JSONTweakData('./data/jaildata.json')


def _finish_threads():
    global threads_alive
    threads_alive = False

    if len(threading.enumerate()) > 1:
        jailinf('Finishing threads')
        for i in threading.enumerate():
            if i != threading.main_thread():
                if i.is_alive() and not i.daemon:
                    i.join()


def _load_ct():
    os.makedirs('./data/NewCoreTweaks', exist_ok=True)

    for core_tweak in os.listdir('./data/NewCoreTweaks'):
        fp = f'./data/NewCoreTweaks/{core_tweak}'
        with open(fp) as c_fl:
            exec(compile(c_fl.read(), fp, 'exec'), globals())
        print(f'Core tweak {fp}')


glb: dict[str, Any] = {
    '__file__': 'msgr',
    '__name__': 'msgr',
    'sys': sys,
    'ui': ui,
}

stage = ''

class DictBoundModuleType(types.ModuleType):
    def __init__(self, name: str, dct: dict, doc: str):
        self.__dct__ = dct
        super().__init__(name, doc)

    @property
    def __dict__(self):
        return self.__dct__

    def __getattr__(self, item):
        return self.__dct__[item]

    def __setattr__(self, key, value):
        if key == '__dct__':
            object.__setattr__(self, key, value)
        else:
            self.__dct__[key] = value


app = sys.modules['Application'] = DictBoundModuleType('Application', glb, 'Dynamic application globals')
restart = False


def _launch():
    global stage
    with open('./msgr.py', 'r', encoding='utf-8') as main_fl:
        stime = time.time()
        content = main_fl.read().replace("if __name__ == '__main__':", 'if True:')
        cpl = compile(content, './msgr.py', 'exec')
        jailinf(f'Compile took {round(time.time() - stime, 4)}s')
        stage = 'Launched'
        exec(cpl, glb)
    JModule.API.on_exit.fire()


def _load():
    global restart, glb, stage

    sys.excepthook = sys_excepthook
    threading.excepthook = t_excepthook

    importlib.import_module('data.lib.plugin_api')
    sys.modules['data.lib.plugin_api'].get_plugs = lambda *a, **kw: {}
    sys.modules['data.lib.plugin_api'].exec_plugs = lambda *a, **kw: None

    sys.argv.clear()
    sys.argv.append('loader.py')
    sys.argv.append('--force-start')
    sys.argv.extend(app_flags)

    jailinf('MSGR Jailbreak V2')
    jailinf('!!! Warning: Jailbreak conflicts with BTAEML (plugin system), it will be automatically disabled !!!')

    JailbreakApi.globals_key_notifier = KeyRegisterNotifier(glb)
    sys.modules['J'] = JModule
    sys.modules['data.lib.ui'].Win = Win
    stage = 'CoreTweaks'
    _load_ct()
    _launch()
    if restart:
        return 2
    return 0


if __name__ == '__main__':
    s = _load()
    exit(s)