from tkinter import ttk
from tkinter import *
import psutil
from datetime import datetime
import sqlite3


# Функции для получения данных о системе
def get_cpu_usage():
    return psutil.cpu_percent(interval=0.1)


def get_memory_usage():
    memory = psutil.virtual_memory()
    return f'{memory.free / (1024 ** 3):.2f} ГБ / {memory.total / (1024 ** 3):.2f} ГБ'


def get_disk_usage():
    disk = psutil.disk_usage('/')
    return f'{disk.free / (1024 ** 3):.2f} ГБ / {disk.total / (1024 ** 3):.2f} ГБ'


# Функция для обновления меток
def update_labels():
    global recording
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    disk_usage = get_disk_usage()

    label_2.config(text=f"Загруженность ЦП: {cpu_usage} %")
    label_3.config(text=f"Загруженность ОЗУ: {memory_usage}")
    label_4.config(text=f"Загруженность ПЗУ: {disk_usage}")

    if recording:
        save_to_database(cpu_usage, memory_usage, disk_usage)

    root.after(500, update_labels)  # обновление каждую половину секунды


# Функция для создания базы данных
def create_database():
    conn = sqlite3.connect('system_usage.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpu_usage REAL,
            memory_usage TEXT,
            disk_usage TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Функция для записи данных в базу данных
def save_to_database(cpu_usage, memory_usage, disk_usage):
    conn = sqlite3.connect('system_usage.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usage_data (cpu_usage, memory_usage, disk_usage, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (cpu_usage, memory_usage, disk_usage, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


# Функция для обновления таймера
def update_timer():
    if recording:
        elapsed_time = datetime.now() - start_time
        timer_label.config(text=f"Прошло времени: {str(elapsed_time).split('.')[0]}")
        root.after(1000, update_timer)


# Функция для обработки нажатия на кнопку
def click_button():
    global recording, start_time
    recording = not recording
    if recording:
        btn["text"] = "Остановить запись"
        start_time = datetime.now()
        timer_label.config(text="Прошло времени: 0:00:00")
        update_timer()
    else:
        btn["text"] = "Начать запись"
        timer_label.config(text="")


# Функция для отображения статистики
def statistics():
    stats_window = Toplevel(root)
    stats_window.title("Статистика")
    stats_window.geometry("600x400")

    conn = sqlite3.connect('system_usage.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usage_data')
    rows = cursor.fetchall()

    stats_text = Text(stats_window, wrap=NONE)
    stats_text.pack(fill=BOTH, expand=True)

    stats_text.delete(1.0, END)  # Очищаем текстовое поле
    stats_text.insert(END, "Загрузка ЦП | Свободного ОЗУ | Свободного ПЗУ | Дата и время\n")
    stats_text.insert(END, "-" * 60 + "\n")
    for row in rows:
        stats_text.insert(END, f"{row[1]}% | {row[2]} | {row[3]} | {row[4]}\n")

    conn.close()


# Функция для очистки статистики
def clear_statistics():
    conn = sqlite3.connect('system_usage.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usage_data')  # Удаляем все записи из таблицы
    conn.commit()
    conn.close()


# Основное окно
root = Tk()
root.title("Уровень загруженности ПК")
root.geometry("1000x700")
root.resizable(False, False)

# Глобальные переменные
recording = False  # Флаг для отслеживания состояния записи
start_time = None  # Время начала записи

# Создаём базу данных и таблицу
create_database()

# Элементы интерфейса
label_1 = Label(text="Уровень загруженности:", font=("Arial", 15))
label_2 = Label(text=f"Загруженность ЦП: {get_cpu_usage()} %", font=("Arial", 13))
label_3 = Label(text=f"Загруженность ОЗУ: {get_memory_usage()}", font=("Arial", 13))
label_4 = Label(text=f"Загруженность ПЗУ: {get_disk_usage()}", font=("Arial", 13))

timer_label = Label(text="", font=("Arial", 12))
menu = ttk.Button(text="Статистика", command=statistics)
clear_button = ttk.Button(text="Очистить статистику", command=clear_statistics)
btn = ttk.Button(text="Начать запись", command=click_button)

# Размещение элементов
menu.place(relx=1.0, rely=0.0, anchor='ne', x=-100, y=10)
clear_button.place(relx=1.0, rely=0.0, anchor='se', x=-100, y=100)
label_1.pack(anchor='nw', padx=20, pady=40)
label_2.pack(anchor='nw', padx=20)
label_3.pack(anchor='nw', padx=20)
label_4.pack(anchor='nw', padx=20)
btn.pack(anchor='s', pady=50)
timer_label.pack(anchor='s', pady=10)

# Запуск обновления данных
update_labels()

root.mainloop()
