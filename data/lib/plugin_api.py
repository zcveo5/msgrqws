"""Plugin Api"""

import json
import os.path
import time
import traceback


def print_adv(v):
    pass


def exec_plugs(_plugs):
    for key, value in _plugs.items():
        cur_mod = key
        try:
            print_adv(f'[info] loading mod {key}')
            st_time = time.time()
            value['plugin'].execute()
            fin_time = time.time()
            print_adv(f"[info] completed in {str(fin_time - st_time).split('.')[0]}sec")
        except Exception as _ex:
            print_adv(f'[error] {cur_mod} loaded with error. skip '
                          f'(error details: {_ex})')
            with open('./data/logs/plugin-api.log', 'a') as fl:
                fl.write(f'``````````````load err {cur_mod}\n{traceback.format_exc()}')


def get_plugs(main_module):
    print_adv('[info] compiling plugins')
    if not os.path.exists('./plugins'):
        print('[error] no plugins folder. skipping plugins loading')
        return {}
    compiled_plugins = {}
    for name in os.listdir("./plugins"):
        if os.path.isdir(os.path.join("./plugins", name)):
            try:
                open(f"./plugins/{name}/metadata.json")
                with open(f"./plugins/{name}/metadata.json") as f:
                    plugin_data = json.load(f)
                    if plugin_data['state'] == 'True':
                        imported = __import__(f"plugins.{name}.{plugin_data['file']}")
                        compiled_plugins[plugin_data['name']] = {"plugin": (getattr(getattr(getattr(imported, name), plugin_data['file']), plugin_data['class']))(), "metadata": plugin_data}
                print_adv(f'[info] compiled plugin {name}')
            except Exception as _ex:
                print_adv(f'[error] invalid plugin {name}, skip ({_ex})')
                with open('./data/logs/core.log', 'a') as fl:
                    fl.write(f'{name} error\n{traceback.format_exc()}')
    print_adv('[info] pre-loading plugins')
    mod = __import__(main_module)
    for key, value in compiled_plugins.items():
        try:
            value['plugin'].give_data(mod)
            print_adv(f'[info] {key} pre-loaded')
        except AttributeError as preload_ex:
            print_adv(f'[error] invalid pluginMainClass {key}. details: {preload_ex}')
        except Exception:
            print_adv(f'[error] invalid give_data call {key}')
    print_adv('[info] completed')
    return compiled_plugins