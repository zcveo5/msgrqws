# METADATA
# {"req": ["LibSettings.py"]}
import tkinter

import Application
import TweakAPI
import J


def toggle():
    storage = TweakAPI.GetTweakStorage()
    storage['PopupsAsWindows'] = not storage.get('PopupsAsWindows', False)
    TweakAPI.SaveTweakStorage()
    J.SharedMemory['SettingsAPI'].rebuild()
    replace_classes()


class PopupWin(tkinter.Tk):
    def __init__(self, master = None, x: int = -1, y: int = -1, size=None,
                 style=None, title: str = 'Popup', map_on_init=True):
        super().__init__()

        if size:
            self.geometry(f'{size[0]}x{size[1]}')

        self.title(title)

        self.pack_propagate(True)


@J.API.on_init
def setup_settings():
    sapi = J.SharedMemory['SettingsAPI']
    sapi.create_page('PopupConfig')
    sapi.create_widget('PopupConfig', 'Label', textfunc=lambda: f'{TweakAPI.GetTweakStorage().get('PopupsAsWindows', False)}')
    sapi.create_widget('PopupConfig', 'Button', text='Toggle behaviour', command=toggle)

@J.API.on_init
def replace_classes():
    Application._RealPopup = Application.Popup
    if TweakAPI.GetTweakStorage().get('PopupsAsWindows'):
        Application.Popup = PopupWin
    else:
        Application.Popup = Application._RealPopup