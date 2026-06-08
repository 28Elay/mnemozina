import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

DB_NAME = "reminders.db"
current_theme = "dark"

THEMES = {
    "dark": {"bg": "#121212", "surface": "#1E1E1E", "text": "#E0E0E0", "accent": "#3B82F6", "accent_hover": "#2563EB", "border": "#374151", "hover": "#2D2D2D"},
    "light": {"bg": "#F3F4F6", "surface": "#FFFFFF", "text": "#1F2937", "accent": "#3B82F6", "accent_hover": "#2563EB", "border": "#D1D5DB", "hover": "#E5E7EB"}
}

def get_theme():
    return THEMES[current_theme]

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, 
            description TEXT, due_time TEXT NOT NULL, is_done INTEGER DEFAULT 0)""")

def toggle_theme():
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    theme_btn.config(text="🌙 Тёмная тема" if current_theme == "dark" else "☀️ Светлая тема")
    t = get_theme()
    
    # Обновляем цвета основных контейнеров и полей ввода
    for w in [root, header_frame, canvas, scrollable_frame]: w.configure(bg=t["bg"])
    for w in [input_container, entry_title, text_desc, entry_due, spin_year, spin_month, spin_day, spin_hour, spin_min]:
        w.configure(bg=t["surface"], fg=t["text"])
        if isinstance(w, (tk.Entry, tk.Text)):
            w.configure(insertbackground=t["text"], highlightbackground=t["border"])
    load_reminders()

def set_datetime():
    try:
        vals = [int(w.get()) for w in (spin_year, spin_month, spin_day, spin_hour, spin_min)]
        chosen_dt = datetime(*vals)
        if chosen_dt < datetime.now():
            return messagebox.showerror("Ошибка", "Нельзя установить время в прошлом!")
        
        entry_due.config(state="normal")
        entry_due.delete(0, tk.END)
        entry_due.insert(0, chosen_dt.strftime("%Y-%m-%d %H:%M"))
        entry_due.config(state="readonly")
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректная дата или время!")

def reset_inputs():
    entry_title.delete(0, tk.END)
    text_desc.delete("1.0", tk.END)
    now = datetime.now()
    entry_due.config(state="normal")
    entry_due.delete(0, tk.END)
    entry_due.insert(0, now.strftime("%Y-%m-%d %H:%M"))
    entry_due.config(state="readonly")
    
    for spin, val in zip((spin_year, spin_month, spin_day, spin_hour, spin_min), 
                         (now.year, now.month, now.day, now.hour, now.minute)):
        spin.delete(0, tk.END)
        spin.insert(0, str(val))

def add_reminder():
    title, desc, due = entry_title.get().strip(), text_desc.get("1.0", tk.END).strip(), entry_due.get().strip()
    if not title or not due:
        return messagebox.showwarning("Внимание", "Заполните название и выберите время.")
    try:
        if datetime.strptime(due, "%Y-%m-%d %H:%M") < datetime.now():
            return messagebox.showerror("Ошибка", "Время не может быть в прошлом!")
    except ValueError:
        return messagebox.showerror("Ошибка", "Неверный формат времени.")

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO reminders (title, description, due_time, is_done) VALUES (?, ?, ?, 0)", (title, desc, due))
    reset_inputs()
    load_reminders()

def mark_done(rid):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE reminders SET is_done = 1 WHERE id = ?", (rid,))
    load_reminders()

def delete_reminder(rid):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM reminders WHERE id = ?", (rid,))
    load_reminders()

def load_reminders():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    with sqlite3.connect(DB_NAME) as conn:
        reminders = conn.execute("SELECT * FROM reminders WHERE is_done = 0 ORDER BY due_time ASC").fetchall()

    if not reminders:
        tk.Label(scrollable_frame, text="Нет активных напоминаний", font=("Segoe UI", 14), fg=get_theme()["text"], bg=get_theme()["bg"]).pack(pady=40)
        return

    for rem in reminders:
        create_task_row(scrollable_frame, rem)

def create_task_row(parent, rem):
    t = get_theme()
    row = tk.Frame(parent, bg=t["surface"])
    row.pack(fill="x", padx=20, pady=3)
    
    row.bind("<Enter>", lambda e: row.configure(bg=t["hover"]))
    row.bind("<Leave>", lambda e: row.configure(bg=t["surface"]))
    
    # Упрощенный чекбокс вместо Canvas
    chk = tk.Label(row, text="○", font=("Segoe UI", 14), fg=t["accent"], bg=t["surface"], cursor="hand2")
    chk.pack(side="left", padx=(0, 10))
    chk.bind("<Button-1>", lambda e: mark_done(rem["id"]))
    
    tk.Label(row, text=rem["title"], font=("Segoe UI", 12), fg=t["text"], bg=t["surface"], anchor="w").pack(side="left", fill="x", expand=True, pady=8)
    tk.Label(row, text=rem["due_time"], font=("Segoe UI", 10), fg=t["accent"], bg=t["surface"]).pack(side="right", padx=10)
    
    tk.Button(row, text="✕", font=("Segoe UI", 9), bg=t["surface"], fg=t["text"], activebackground=t["hover"], relief="flat", cursor="hand2",
              command=lambda r=rem["id"]: delete_reminder(r)).pack(side="right", padx=5)

def make_spin(parent, text, r, c, from_, to, default, fmt=None):
    t = get_theme()
    tk.Label(parent, text=text, bg=t["surface"], fg=t["text"], font=("Segoe UI", 10)).grid(row=r, column=c, padx=5, pady=5, sticky="e")
    kwargs = {"from_": from_, "to": to, "width": 6, "font": ("Segoe UI", 11), "bg": t["surface"], "fg": t["text"], "highlightbackground": t["border"], "highlightthickness": 1, "relief": "solid"}
    if fmt: kwargs["format"] = fmt
    spin = tk.Spinbox(parent, **kwargs)
    spin.delete(0, tk.END)
    spin.insert(0, str(default))
    spin.grid(row=r, column=c+1, padx=5, pady=5)
    return spin

# --- Инициализация интерфейса ---
init_db()
t = get_theme()

root = tk.Tk()
root.title("Ежедневник")
root.geometry("700x850")
root.minsize(600, 600)
root.configure(bg=t["bg"])

header_frame = tk.Frame(root, bg=t["bg"], padx=20, pady=10)
header_frame.pack(fill="x")

theme_btn = tk.Button(header_frame, text="☀️ Светлая тема", font=('Segoe UI', 10), bg=t["surface"], fg=t["text"],
                      activebackground=t["hover"], activeforeground=t["text"], relief='flat', cursor="hand2", command=toggle_theme)
theme_btn.pack(side="right")

input_container = tk.Frame(root, bg=t["surface"], padx=30, pady=20)
input_container.pack(fill="x", padx=30, pady=20)

tk.Label(input_container, text="Новое напоминание", font=('Segoe UI', 16, 'bold'), bg=t["surface"], fg=t["text"]).pack(anchor="w", pady=(0, 15))

for lbl_text, pack_args in [("Название:", {"anchor": "w"}), ("Описание:", {"anchor": "w", "pady": (10, 0)}), ("Дата и время:", {"anchor": "w", "pady": (10, 0)})]:
    tk.Label(input_container, text=lbl_text, bg=t["surface"], fg=t["text"], font=('Segoe UI', 11)).pack(**pack_args)

entry_title = tk.Entry(input_container, font=("Segoe UI", 12), bg=t["surface"], fg=t["text"], insertbackground=t["text"], relief='solid', highlightthickness=1, highlightbackground=t["border"])
entry_title.pack(fill="x", pady=4)

text_desc = tk.Text(input_container, height=3, font=("Segoe UI", 11), bg=t["surface"], fg=t["text"], insertbackground=t["text"], relief='solid', highlightthickness=1, highlightbackground=t["border"])
text_desc.pack(fill="x", pady=4)

datetime_frame = tk.Frame(input_container, bg=t["surface"])
datetime_frame.pack(fill="x", pady=4)

now = datetime.now()
spin_year = make_spin(datetime_frame, "Год:", 0, 0, now.year, now.year+5, now.year)
spin_month = make_spin(datetime_frame, "Месяц:", 0, 2, 1, 12, now.month, "%02.0f")
spin_day = make_spin(datetime_frame, "День:", 0, 4, 1, 31, now.day, "%02.0f")
spin_hour = make_spin(datetime_frame, "Час:", 1, 0, 0, 23, now.hour, "%02.0f")
spin_min = make_spin(datetime_frame, "Минуты:", 1, 2, 0, 59, now.minute, "%02.0f")

tk.Button(datetime_frame, text="✓ Установить", font=('Segoe UI', 9, 'bold'), bg=t["accent"], fg='white', activebackground=t["accent_hover"], relief='flat', cursor="hand2", command=set_datetime).grid(row=1, column=4, columnspan=2, padx=10, pady=5)

entry_due = tk.Entry(input_container, font=("Segoe UI", 12), bg=t["surface"], fg=t["accent"], state="readonly", relief='solid', highlightthickness=1, highlightbackground=t["border"])
entry_due.pack(fill="x", pady=4)
entry_due.config(state="normal")
entry_due.insert(0, now.strftime("%Y-%m-%d %H:%M"))
entry_due.config(state="readonly")

tk.Button(input_container, text="Добавить", font=('Segoe UI', 10, 'bold'), bg=t["accent"], fg='white', activebackground=t["accent_hover"], relief='flat', cursor="hand2", command=add_reminder).pack(fill="x", pady=15)

list_frame = tk.Frame(root, bg=t["bg"])
list_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(list_frame, bg=t["bg"], highlightthickness=0)
scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview, bg=t["surface"], troughcolor=t["bg"], activebackground=t["hover"])
scrollable_frame = tk.Frame(canvas, bg=t["bg"])

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

load_reminders()
root.mainloop()
