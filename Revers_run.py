import ctypes
import sys
import os
import time
import threading
import customtkinter as ctk
from tkinter import messagebox

# ---------- Настройки внешнего вида ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ---------- Уникальный ID приложения (для иконки в панели задач) ----------
try:
    myappid = 'VladGames.ReversRun.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# ---------- Проверка прав администратора ----------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

# ---------- Глобальные переменные ----------
countdown_thread = None
countdown_stop = threading.Event()

# ---------- Функции ----------
def get_seconds():
    """Берёт часы, минуты, секунды и возвращает общее число секунд."""
    try:
        h = int(entry_h.get() or "0")
        m = int(entry_m.get() or "0")
        s = int(entry_s.get() or "0")
        if h < 0 or m < 0 or s < 0:
            raise ValueError
        total = h * 3600 + m * 60 + s
        if total <= 0:
            messagebox.showerror("Ошибка", "Введи время больше 0!")
            return None
        return total
    except ValueError:
        messagebox.showerror("Ошибка", "Введи целые числа в поля ч/м/с!")
        return None

def countdown(seconds, name):
    for remaining in range(seconds, -1, -1):
        if countdown_stop.is_set():
            return
        h, rem = divmod(remaining, 3600)
        m, s = divmod(rem, 60)
        status_label.configure(text=f"{name} через {h:02d}:{m:02d}:{s:02d}")
        progress.set((seconds - remaining) / seconds)
        if countdown_stop.wait(1):
            return
    status_label.configure(text="Готово!")
    progress.set(1)

def do_action(action, name):
    global countdown_thread
    seconds = get_seconds()
    if seconds is None:
        return

    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    time_str = f"{h:02d}:{m:02d}:{s:02d}"

    ok = messagebox.askyesno(name, f"{name} через {time_str}.\nПродолжить?")
    if not ok:
        return

    cancel_action(silent=True)

    if action == "shutdown":
        os.system(f"shutdown /s /t {seconds}")
    elif action == "restart":
        os.system(f"shutdown /r /t {seconds}")
    elif action == "winre":
        os.system(f"shutdown /r /o /t {seconds}")
    elif action == "sleep":
        def sleeper():
            time.sleep(seconds)
            if not countdown_stop.is_set():
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        threading.Thread(target=sleeper, daemon=True).start()

    countdown_stop.clear()
    countdown_thread = threading.Thread(
        target=countdown, args=(seconds, name), daemon=True
    )
    countdown_thread.start()

def cancel_action(silent=False):
    global countdown_thread
    countdown_stop.set()
    os.system("shutdown /a")
    status_label.configure(text="Отменено")
    progress.set(0)
    if not silent:
        messagebox.showinfo("Отмена", "Действие отменено!")

# ---------- Интерфейс ----------
app = ctk.CTk()
app.title("ReversRun — панель управления")
app.geometry("400x660")
app.resizable(False, False)

# ---------- ИКОНКА ----------
def set_icon():
    paths = [
        r"E:\revers_run\resources\icon.ico",
        os.path.join(os.path.dirname(sys.argv[0]), "resources", "icon.ico"),
        os.path.join(os.path.dirname(sys.argv[0]), "icon.ico"),
        "resources/icon.ico",
        "icon.ico",
    ]
    for path in paths:
        try:
            if os.path.exists(path):
                app.iconbitmap(path)
                return True
        except:
            continue
    return False

set_icon()

# Заголовок
title = ctk.CTkLabel(app, text="⚡ ReversRun",
                     font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                     text_color="#00ff88")
title.pack(pady=(20, 5))

subtitle = ctk.CTkLabel(app, text="панель управления ПК",
                        font=ctk.CTkFont(family="Segoe UI", size=12),
                        text_color="#888888")
subtitle.pack()

# ---------- Рамка с таймером (3 поля) ----------
timer_frame = ctk.CTkFrame(app, fg_color="transparent")
timer_frame.pack(pady=20)

ctk.CTkLabel(timer_frame, text="Через",
             font=ctk.CTkFont(family="Segoe UI", size=14),
             text_color="white").pack(side="left", padx=5)

# Часы
entry_h = ctk.CTkEntry(timer_frame, width=50, height=40,
                       font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                       justify="center",
                       fg_color="#2d2d2d",
                       text_color="#00ff88",
                       corner_radius=10)
entry_h.insert(0, "0")
entry_h.pack(side="left", padx=3)

ctk.CTkLabel(timer_frame, text="ч",
             font=ctk.CTkFont(family="Segoe UI", size=12),
             text_color="white").pack(side="left")

# Минуты
entry_m = ctk.CTkEntry(timer_frame, width=50, height=40,
                       font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                       justify="center",
                       fg_color="#2d2d2d",
                       text_color="#00ff88",
                       corner_radius=10)
entry_m.insert(0, "5")
entry_m.pack(side="left", padx=3)

ctk.CTkLabel(timer_frame, text="м",
             font=ctk.CTkFont(family="Segoe UI", size=12),
             text_color="white").pack(side="left")

# Секунды
entry_s = ctk.CTkEntry(timer_frame, width=50, height=40,
                       font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                       justify="center",
                       fg_color="#2d2d2d",
                       text_color="#00ff88",
                       corner_radius=10)
entry_s.insert(0, "0")
entry_s.pack(side="left", padx=3)

ctk.CTkLabel(timer_frame, text="с",
             font=ctk.CTkFont(family="Segoe UI", size=12),
             text_color="white").pack(side="left")

# Прогресс-бар
progress = ctk.CTkProgressBar(app, width=320, height=15,
                              corner_radius=8,
                              progress_color="#00ff88")
progress.set(0)
progress.pack(pady=10)

# Статус
status_label = ctk.CTkLabel(app, text="Готов к работе",
                            font=ctk.CTkFont(family="Segoe UI", size=13),
                            text_color="#00ff88")
status_label.pack(pady=5)

# Кнопки
def make_button(text, color, command):
    btn = ctk.CTkButton(app, text=text,
                        font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                        fg_color=color,
                        hover_color=color,
                        text_color="white",
                        width=300, height=45,
                        corner_radius=15,
                        command=command)
    btn.pack(pady=7)
    return btn

make_button("🔴 Выключить", "#c0392b",
            lambda: do_action("shutdown", "Выключение"))
make_button("🔄 Перезагрузить", "#2980b9",
            lambda: do_action("restart", "Перезагрузка"))
make_button("🛠 WinRE", "#8e44ad",
            lambda: do_action("winre", "Загрузка в WinRE"))
make_button("💤 Спящий режим", "#16a085",
            lambda: do_action("sleep", "Спящий режим"))
make_button("❌ ОТМЕНИТЬ", "#e67e22", cancel_action)

# Подсказка
hint = ctk.CTkLabel(app, text="Введи время и нажми кнопку",
                    font=ctk.CTkFont(family="Segoe UI", size=11),
                    text_color="#666666")
hint.pack(pady=15)

app.mainloop()