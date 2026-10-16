# METADATA
# {"req": ["LibSettings.py"]}


import io
import sys
import time
import tkinter as tk
import traceback
from tkinter import scrolledtext

import J
from data.lib.ui import Popup


class PyTerminalFrame(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.env_globals = {"__builtins__": __builtins__, 'J': J}
        self._input_buffer = None
        self._waiting_for_input = False

        self.configure(bg="#1e1e1e")

        # --- 1. ФРЕЙМ ВВОДА (Упаковываем СНИЗУ первым!) ---
        input_frame = tk.Frame(self, bg="#1e1e1e")
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        # Поле ввода (input_entry)
        self.input_entry = tk.Entry(
            input_frame,
            bg="#252526",
            fg="#d4d4d4",
            insertbackground="white",
            font=("Consolas", 10),
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", lambda event: self.on_enter_pressed())

        # Кнопка выполнить
        self.btn_run = tk.Button(
            input_frame,
            text="Run",
            command=self.on_enter_pressed,
            bg="#0e639c",
            fg="white",
            relief=tk.FLAT,
        )
        self.btn_run.pack(side=tk.RIGHT)

        # --- 2. ОБЛАСТЬ ВЫВОДА (Занимает всё ОСТАВШЕЕСЯ место) ---
        self.output_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            font=("Consolas", 10),
        )
        self.output_area.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=(5, 0)
        )
        self.output_area.insert(
            tk.END, "--- Embedded Python Terminal ---\nВводи код ниже.\n\n"
        )
        self.output_area.config(state=tk.DISABLED)

    def write_to_terminal(self, text):
        """Запись текста в консоль"""
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def custom_input(self, prompt=""):
        """Перехват штатного input() в Python"""
        if prompt:
            self.write_to_terminal(str(prompt))

        self._waiting_for_input = True
        self._input_buffer = None

        while self._input_buffer is None:
            self.update()
            time.sleep(0.1)

        self._waiting_for_input = False
        res = self._input_buffer
        self._input_buffer = None
        return res

    def on_enter_pressed(self):
        """Обработка ввода"""
        text = self.input_entry.get()

        if self._waiting_for_input:
            self.write_to_terminal(f"{text}\n")
            self.input_entry.delete(0, tk.END)
            self._input_buffer = text
            return

        if not text.strip():
            return

        self.write_to_terminal(f">>> {text}\n")
        self.input_entry.delete(0, tk.END)

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        old_stdin = sys.stdin

        self.env_globals["input"] = self.custom_input

        redirected_output = sys.stdout = io.StringIO()
        redirected_error = sys.stderr = io.StringIO()

        try:
            exec(text, self.env_globals)
        except Exception as e:
            redirected_error.write(f'{''.join(traceback.format_exception(e))}')

        sys.stdout = old_stdout
        sys.stderr = old_stderr
        sys.stdin = old_stdin

        output_str = redirected_output.getvalue()
        error_str = redirected_error.getvalue()

        if output_str:
            self.write_to_terminal(output_str)
        if error_str:
            self.write_to_terminal(f"[ERROR] {error_str}")


@J.API.on_ready_window
def add():
    pop = Popup(size=(400, 300))
    pop.close_btn.configure(command=pop.root_frame.place_forget)
    pop.root_frame.destroy = lambda: None
    PyTerminalFrame(pop).pack(fill='both')
    def t():
        pop.root_frame.place(x=0, y=0)
    J.SharedMemory['SettingsAPI'].create_widget('ROOT', 'Button', text='Term', command=t)