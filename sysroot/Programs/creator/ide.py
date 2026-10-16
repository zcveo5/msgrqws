s_var, g_var = None, None
status = None
ide_win = None

def update_var(set_func, get_func):
    global s_var, g_var
    s_var, g_var = set_func, get_func


def new():
    if ide_win is None or status is None:
        g_var('show')('Error', 'None at ide_win or status')
        return
    ide_win.destroy_children()



def start(namespace):
    global status, ide_win
    pop_class = namespace['Popup']
    ui = namespace['lib.ui']
    ide_win = pop_class(title='pOS Program Creator')
    status = 'Main'
    ui.Label(ide_win, text='Select action:', justify='left').place(relx=0.45, rely=0.45, anchor='center')
    ui.Button(ide_win, text='Create new', command=new).place(relx=0.45, rely=0.55, anchor='center')