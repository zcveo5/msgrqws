s_var, g_var = None, None

def update_var(set_func, get_func):
    global s_var, g_var
    s_var, g_var = set_func, get_func

def start(namespace):
    pop_class = namespace['pop_class']
    ui = namespace['lib.ui']
    pop = pop_class(title='Hello!')
    ui.Label(pop, text='8===D').pack()