from nicegui import ui

# Создаем элемент с CSS-стилями и Tailwind-классами прямо в Python
ui.label('Привет из NiceGUI!').classes('text-2xl font-bold text-primary')

ui.button('Кнопка', on_click=lambda: ui.notify('Нажали!')).style('background-color: #ff5722; color: white;')

ui.run(native=True)  # Запустится как десктопное приложение в окне