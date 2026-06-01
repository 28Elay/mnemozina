import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

# === НАСТРОЙКИ БД ===
DB_NAME = "reminders.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Создаёт таблицу напоминаний, если её нет"""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_time TEXT NOT NULL,
            is_done INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# === ЛОГИКА ===
def add_reminder():
    title = entry_title.get().strip()
    desc = text_desc.get("1.0", tk.END).strip()
    due = entry_due.get().strip()

    if not title or not due:
        messagebox.showwarning("Внимание", "Заполните название и время напоминания.")
        return

    try:
        datetime.strptime(due, "%Y-%m-%d %H:%M")
    except ValueError:
        messagebox.showerror("Ошибка", "Неверный формат времени.\nИспользуйте: ГГГГ-ММ-ДД ЧЧ:ММ")
        return

    conn = get_connection()
    conn.execute("INSERT INTO reminders (title, description, due_time, is_done) VALUES (?, ?, ?, 0)",
                 (title, desc, due))
    conn.commit()
    conn.close()

    # Очистка полей
    entry_title.delete(0, tk.END)
    text_desc.delete("1.0", tk.END)
    entry_due.delete(0, tk.END)
    # Возвращаем дефолтное время
    entry_due.insert(0, datetime.now().replace(hour=9, minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M"))
    
    load_reminders()
    messagebox.showinfo("Успех", "Напоминание добавлено!")

def mark_done(rid):
    conn = get_connection()
    conn.execute("UPDATE reminders SET is_done = 1 WHERE id = ?", (rid,))
    conn.commit()
    conn.close()
    load_reminders()

def delete_reminder(rid):
    conn = get_connection()
    conn.execute("DELETE FROM reminders WHERE id = ?", (rid,))
    conn.commit()
    conn.close()
    load_reminders()

def load_reminders():
    """Обновляет список активных напоминаний"""
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    conn = get_connection()
    # Показываем только невыполненные, отсортированные по времени
    reminders = conn.execute("SELECT * FROM reminders WHERE is_done = 0 ORDER BY due_time ASC").fetchall()
    conn.close()

    if not reminders:
        ttk.Label(scrollable_frame, text="Нет активных напоминаний ", 
                  font=("Segoe UI", 14), foreground="gray").pack(pady=30)
        return

    for rem in reminders:
        card = ttk.Frame(scrollable_frame, padding=10, relief="solid", borderwidth=1)
        card.pack(fill="x", pady=5)

        ttk.Label(card, text=rem["title"], font=("Segoe UI", 13, "bold")).pack(anchor="w")
        if rem["description"]:
            ttk.Label(card, text=rem["description"], font=("Segoe UI", 11), wraplength=500).pack(anchor="w")
        
        time_label = ttk.Label(card, text=f" {rem['due_time']}", font=("Segoe UI", 11), foreground="#555")
        time_label.pack(anchor="w", pady=(3, 5))

        btn_frame = ttk.Frame(card)
        btn_frame.pack(anchor="e")

        # Важно: используем default argument для корректного захвата переменной в lambda
        ttk.Button(btn_frame, text=" Выполнено", command=lambda r=rem["id"]: mark_done(r)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text=" Удалить", command=lambda r=rem["id"]: delete_reminder(r)).pack(side="left", padx=5)

def check_due_reminders():
    """Периодически проверяет, не наступило ли время напоминания"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_connection()
    due = conn.execute("SELECT id, title FROM reminders WHERE due_time <= ? AND is_done = 0", (now,)).fetchall()
    conn.close()

    if due:
        for rid, title in due:
            messagebox.showinfo("Напоминание!", f" {title}\nВремя пришло!")
            conn = get_connection()
            conn.execute("UPDATE reminders SET is_done = 1 WHERE id = ?", (rid,))
            conn.commit()
            conn.close()
        load_reminders()

    # Запускаем проверку снова через 10 секунд
    root.after(10000, check_due_reminders)

# === ИНТЕРФЕЙС ===
root = tk.Tk()
root.title("Напоминания")
root.geometry("650x750")
root.configure(bg="#F8F9FA")

# Инициализация БД
init_db()

# --- Блок добавления ---
input_frame = ttk.Frame(root, padding=15)
input_frame.pack(fill="x", padx=20, pady=10)

ttk.Label(input_frame, text="➕ Новое напоминание", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=5)

ttk.Label(input_frame, text="Название:").pack(anchor="w")
entry_title = ttk.Entry(input_frame, font=("Segoe UI", 12))
entry_title.pack(fill="x", pady=4)

ttk.Label(input_frame, text="Описание (необязательно):").pack(anchor="w")
text_desc = tk.Text(input_frame, height=3, font=("Segoe UI", 12), relief="solid", borderwidth=1)
text_desc.pack(fill="x", pady=4)

ttk.Label(input_frame, text="Время (ГГГГ-ММ-ДД ЧЧ:ММ):").pack(anchor="w")
entry_due = ttk.Entry(input_frame, font=("Segoe UI", 12))
entry_due.pack(fill="x", pady=4)

# Дефолтное время: завтра 9:00
tomorrow = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
if tomorrow < datetime.now():
    tomorrow = tomorrow.replace(day=tomorrow.day + 1)
entry_due.insert(0, tomorrow.strftime("%Y-%m-%d %H:%M"))

ttk.Button(input_frame, text="Добавить", command=add_reminder).pack(fill="x", pady=10)

# --- Блок списка ---
list_frame = ttk.Frame(root, padding=15)
list_frame.pack(fill="both", expand=True, padx=20, pady=5)

ttk.Label(list_frame, text=" Мои напоминания", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5))

# Canvas + Scrollbar для прокрутки списка
canvas = tk.Canvas(list_frame, bg="white", highlightthickness=0)
scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

load_reminders()

# Запуск фоновой проверки времени
root.after(10000, check_due_reminders)

root.mainloop()