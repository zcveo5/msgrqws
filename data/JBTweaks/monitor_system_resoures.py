# build8621175/data/JBTweaks/system_monitor.py
import os
import sys
import tkinter as tk
from tkinter import ttk
import psutil
import time
import threading


def create_process_monitor():
    # Создаем окно мониторинга
    monitor = tk.Toplevel()
    monitor.title("Process Resource Monitor")
    monitor.geometry("450x300")
    monitor.resizable(False, False)

    # Получаем текущий процесс
    current_pid = os.getpid()
    current_process = psutil.Process(current_pid)
    process_name = current_process.name()

    # Заголовок с именем процесса и PID
    title_label = tk.Label(
        monitor,
        text=f"Monitoring: {process_name} (PID: {current_pid})",
        font=("Arial", 10, "bold")
    )
    title_label.pack(pady=10)

    # Стили для виджетов
    style = ttk.Style()
    style.configure("TProgressbar", thickness=20)

    # Переменные для обновления данных
    cpu_var = tk.StringVar()
    mem_var = tk.StringVar()
    threads_var = tk.StringVar()
    disk_io_var = tk.StringVar()

    # Фрейм для CPU
    cpu_frame = tk.LabelFrame(monitor, text="CPU Usage")
    cpu_frame.pack(fill="x", padx=10, pady=5)

    cpu_label = tk.Label(cpu_frame, textvariable=cpu_var, font=("Arial", 9))
    cpu_label.pack(pady=3)

    cpu_bar = ttk.Progressbar(cpu_frame, orient="horizontal", length=400, mode="determinate")
    cpu_bar.pack(pady=5, padx=10)

    # Фрейм для памяти
    mem_frame = tk.LabelFrame(monitor, text="Memory Usage")
    mem_frame.pack(fill="x", padx=10, pady=5)

    mem_label = tk.Label(mem_frame, textvariable=mem_var, font=("Arial", 9))
    mem_label.pack(pady=3)

    mem_bar = ttk.Progressbar(mem_frame, orient="horizontal", length=400, mode="determinate")
    mem_bar.pack(pady=5, padx=10)

    # Фрейм для потоков и дисковых операций
    stats_frame = tk.Frame(monitor)
    stats_frame.pack(fill="x", padx=10, pady=5)

    threads_frame = tk.LabelFrame(stats_frame, text="Threads")
    threads_frame.pack(side="left", padx=5, fill="both", expand=True)

    threads_label = tk.Label(threads_frame, textvariable=threads_var, font=("Arial", 9))
    threads_label.pack(pady=3)

    disk_frame = tk.LabelFrame(stats_frame, text="Disk I/O")
    disk_frame.pack(side="right", padx=5, fill="both", expand=True)

    disk_label = tk.Label(disk_frame, textvariable=disk_io_var, font=("Arial", 9))
    disk_label.pack(pady=3)

    # Переменные для отслеживания предыдущих значений
    prev_io_read = 0
    prev_io_write = 0
    prev_time = time.time()

    # Функция обновления данных
    def update_stats():
        nonlocal prev_io_read, prev_io_write, prev_time

        while monitor.winfo_exists():
            try:
                # Обновляем процесс (на случай перезапуска)
                current_process = psutil.Process(os.getpid())

                # Получение данных CPU
                cpu_percent = current_process.cpu_percent(interval=0.5)
                cpu_var.set(f"CPU: {cpu_percent:.1f}%")
                cpu_bar["value"] = cpu_percent

                # Получение данных памяти
                mem_info = current_process.memory_info()
                mem_percent = current_process.memory_percent()
                mem_rss = mem_info.rss / (1024 ** 2)  # в M
                mem_var.set(f"Memory: {mem_percent:.1f}% ({mem_rss:.1f} MB)")
                mem_bar["value"] = mem_percent

                # Получение информации о потоках
                threads_count = current_process.num_threads()
                threads_var.set(f"Threads: {threads_count}")

                # Получение данных дисковых операций
                current_time = time.time()
                io_counters = current_process.io_counters()

                if prev_time > 0:
                    time_diff = current_time - prev_time
                    read_speed = (io_counters.read_bytes - prev_io_read) / time_diff
                    write_speed = (io_counters.write_bytes - prev_io_write) / time_diff

                    # Форматируем скорость в удобочитаемом виде
                    def format_speed(speed):
                        if speed < 1024:
                            return f"{speed:.1f} B/s"
                        elif speed < 1024 ** 2:
                            return f"{speed / 1024:.1f} KB/s"
                        else:
                            return f"{speed / (1024 ** 2):.1f} MB/s"

                    disk_io_var.set(f"Read: {format_speed(read_speed)}\nWrite: {format_speed(write_speed)}")

                # Сохраняем текущие значения для следующего обновления
                prev_io_read = io_counters.read_bytes
                prev_io_write = io_counters.write_bytes
                prev_time = current_time

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Процесс завершился или недоступен
                cpu_var.set("Process terminated")
                mem_var.set("Process terminated")
                threads_var.set("Threads: 0")
                disk_io_var.set("Read: 0 B/s\nWrite: 0 B/s")
                break

            time.sleep(1)

    # Запуск потока для обновления данных
    monitor.thread = threading.Thread(target=update_stats, daemon=True)
    monitor.thread.start()

    # Обработчик закрытия окна
    monitor.protocol("WM_DELETE_WINDOW", lambda: monitor.destroy())


# Добавляем кнопку мониторинга в главный интерфейс
class SettingsSysMon(Settings):
    def __init__(self):
        super().__init__()
        self._base_widgets.append(tk.Button(self, text='Sysmon', command=create_process_monitor))

Settings = SettingsSysMon