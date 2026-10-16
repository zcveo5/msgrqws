import os.path

def cool_exception_print(exc_type, exc_value, tb):
    tb = tb
    line = tb.tb_lineno
    _file = tb.tb_frame.f_code.co_filename
    code = open(f'{_file}', 'r', errors='replace').read().split('\n')
    show_lines = 10

    all_levels_exceptions = []

    def rec(master):
        if master is not None:
            all_levels_exceptions.append(master)
            rec(master.tb_next)
    rec(tb)

    rev = all_levels_exceptions.copy()
    rev.reverse()

    for _exc in rev:
        lineno = _exc.tb_lineno
        string = code[lineno-1]
        additions = ''
        if lineno == line:
            additions = 'Final '
        elif lineno == rev[0].tb_lineno:
            additions = 'Most deep '
        code[lineno-1] = f'\033[31m{string} <-- {additions}{exc_type.__name__}: "{exc_value}"\033[0m'

    for _str in range(0, len(code)):
        code[_str] = f'{_str + 1}: {code[_str]}'

    with_show_lines = code[line - show_lines:line + show_lines]

    code = f'0-{line-show_lines} ...\n{'\n'.join(with_show_lines)}\n'
    print(f'===== {os.path.basename(_file)} Traceback =====\n{code}\n===== END =====')


sys.excepthook = cool_exception_print