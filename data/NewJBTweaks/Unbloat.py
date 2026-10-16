from LibSettings import SettingsAPI
import Application


def _modify(**kws):
    def _wrapper(w):
        w.kw.update(kws)
        return w
    return _wrapper

SettingsAPI.add_base_widget_hook(4, lambda w: None)

def _sub_f_debug(self):
    #pop = Popup(title='Unbloated debug')
    #pop.pack_propagate(True)
    #pop.root_frame.pack_propagate(True)
    #Button(pop, text='Debugtools', command=Application.Debug().debugtools).pack()
    Application.Debug().debugtools()

Application._Settings.original_sub_f_debug = Application._Settings.sub_f_debug
Application._Settings.sub_f_debug = _sub_f_debug