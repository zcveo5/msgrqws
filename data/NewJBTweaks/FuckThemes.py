import Application

Application.main.option_add = lambda *a, **kw: None
Application.main.option_clear()
Application.commit_theme = lambda *a, **kw: None