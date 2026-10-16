import Application
import J


def _on_theme_change():
    Application.main.option_add("*highlightBackground", Application.default_fg)  # Цвет рамки без фокуса
    Application.main.option_add("*highlightColor", Application.default_fg)

def _comtheme(*args):
    comtheme(*args)
    _on_theme_change()

comtheme = Application.commit_theme
Application.commit_theme = _comtheme