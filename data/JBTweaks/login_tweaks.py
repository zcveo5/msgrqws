import hashlib
import random
import tkinter


def tweaks(after=None):
    def login(legacy=False):
        def login():
            global username, password
            username = _username.get()
            if legacy:
                password = _password.get()
            else:
                hs = hashlib.new(hash_method)
                hs.update(_password.get().encode())
                password = hs.hexdigest()
            user_local_settings['USER_SETTINGS']['PASSWORD'] = password
            user_local_settings['USER_SETTINGS']['USERNAME'] = username
            dump_data_nc()
            reload_data_nc()
            win.destroy()
            if callable(after):
                after()

        _username = Entry(win)
        _password = Entry(win)
        _username.pack()
        _password.pack()
        Button(win, text='Login', command=login).pack()

    def temp():
        global username, password
        username = str(random.randint(100000000, 9999999999))
        password = str(random.randint(100000000, 9999999999))
        win.destroy()
        if callable(after):
            after()

    win = Tk()
    win.title('Login Tweaks')
    Button(win, text='Login normally', command=lambda: login(False)).pack()
    Button(win, text='Login without password encrypt (Legacy Login)', command=lambda: login(True)).pack()
    Button(win, text='Login with Temporary Account', command=temp).pack()



Button(text='Login Tweaks', command=tweaks).place(x=500, y=400, anchor='se')

_oth = Other

class OtherMod(_oth):
    @staticmethod
    def exit_acc():
        user_local_settings['USER_SETTINGS']['USERNAME'] = ''
        user_local_settings['USER_SETTINGS']['PASSWORD'] = ''
        dump_data_nc()
        reload_data_nc()
        for w in main.winfo_children():
            try:
                w.place_forget()
                w.pack_forget()
            except:
                pass
        Button(text='Login Tweaks', command=tweaks).place(x=500, y=400, anchor='se')
        tweaks(after=reinit_ui)

Other = OtherMod
other_cl = Other()