import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

DB_NAME = "reminders.db"

current_theme = "dark"
accent_hover = "#2563EB"

def setup_theme(theme_name="dark"):
    global current_theme, accent_hover
    current_theme = theme_name
    
    if theme_name == "dark":
        bg_color = "#121212"
        surface_color = "#1E1E1E"
        text_color = "#E0E0E0"
        accent_color = "#3B82F6"
        accent_hover = "#2563EB"
        border_color = "#374151"
        hover_color = "#2D2D2D"
    else:
        bg_color = "#F3F4F6"
        surface_color = "#FFFFFF"
        text_color = "#1F2937"
        accent_color = "#3B82F6"
        accent_hover = "#2563EB"
        border_color = "#D1D5DB"
        hover_color = "#E5E7EB"
    
    return bg_color, surface_color, text_color, accent_color, border_color, hover_color

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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

def toggle_theme():
    global bg_color, surface_color, text_color, accent_color, border_color, hover_color, accent_hover
    
    if current_theme == "dark":
        colors = setup_theme("light")
        theme_btn.config(text="🌙 Тёмная тема")
    else:
        colors = setup_theme("dark")
        theme_btn.config(text="☀️ Светлая тема")
    
    bg_color, surface_color, text_color, accent_color, border_color, hover_color = colors
    
    root.configure(bg=bg_color)
    header_frame.configure(bg=bg_color)
    input_container.configure(bg=surface_color)
    canvas.configure(bg=bg_color)
    
    text_desc.configure(bg=surface_color, fg=text_color, insertbackground=text_color, highlightbackground=border_color)
    entry_title.configure(bg=surface_color, fg=text_color, highlightbackground=border_color)
    
    spin_year.configure(bg=surface_color, fg=text_color, highlightbackground=border_color)
    spin_month.configure(bg=surface_color, fg=text_color, highlightbackground=border_color)
    spin_day.configure(bg=surface_color, fg=text_color, highlightbackground=border_color)
    spin_hour.configure(bg=surface_color, fg=text_color, highlightbackground=border_color)
    spin_min.configure(bg=surface_color, fg=text_color, highlightbackground=border_color)
    
    load_reminders()

def set_datetime():
    try:
        year = int(spin_year.get())
        month = int(spin_month.get())
        day = int(spin_day.get())
        hour = int(spin_hour.get())
        minute = int(spin_min.get())
        
        chosen_dt = datetime(year, month, day, hour, minute)
        
        if chosen_dt < datetime.now():
            messagebox.showerror("Ошибка", "Нельзя установить время в прошлом!")
            return
        
        formatted_time = chosen_dt.strftime("%Y-%m-%d %H:%M")
        entry_due.config(state="normal")
        entry_due.delete(0, tk.END)
        entry_due.insert(0, formatted_time)
        entry_due.config(state="readonly")
        
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректная дата или время!")

def add_reminder():
    title = entry_title.get().strip()
    desc = text_desc.get("1.0", tk.END).strip()
    due = entry_due.get().strip()

    if not title or not due:
        messagebox.showwarning("Внимание", "Заполните название и выберите время.")
        return

    try:
        due_dt = datetime.strptime(due, "%Y-%m-%d %H:%M")
        if due_dt < datetime.now():
            messagebox.showerror("Ошибка", "Время не может быть в прошлом!")
            return
    except ValueError:
        messagebox.showerror("Ошибка", "Неверный формат времени.")
        return

    conn = get_connection()
    conn.execute("INSERT INTO reminders (title, description, due_time, is_done) VALUES (?, ?, ?, 0)",
                 (title, desc, due))
    conn.commit()
    conn.close()

    entry_title.delete(0, tk.END)
    text_desc.delete("1.0", tk.END)
    
    default_time = datetime.now()
    entry_due.delete(0, tk.END)
    entry_due.insert(0, default_time.strftime("%Y-%m-%d %H:%M"))
    
    spin_year.delete(0, tk.END)
    spin_year.insert(0, str(default_time.year))
    spin_month.delete(0, tk.END)
    spin_month.insert(0, str(default_time.month))
    spin_day.delete(0, tk.END)
    spin_day.insert(0, str(default_time.day))
    spin_hour.delete(0, tk.END)
    spin_hour.insert(0, str(default_time.hour))
    spin_min.delete(0, tk.END)
    spin_min.insert(0, str(default_time.minute))

    load_reminders()

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
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    conn = get_connection()
    reminders = conn.execute("SELECT * FROM reminders WHERE is_done = 0 ORDER BY due_time ASC").fetchall()
    conn.close()

    if not reminders:
        label = tk.Label(scrollable_frame, text="Нет активных напоминаний", 
                  font=("Segoe UI", 14), fg=text_color, bg=bg_color)
        label.pack(pady=40)
        return

    for rem in reminders:
        create_task_row(scrollable_frame, rem)

def create_task_row(parent, reminder):
    row_frame = tk.Frame(parent, bg=surface_color)
    row_frame.pack(fill="x", padx=20, pady=3)
    
    def on_enter(e):
        row_frame.configure(bg=hover_color)
    def on_leave(e):
        row_frame.configure(bg=surface_color)
    
    row_frame.bind("<Enter>", on_enter)
    row_frame.bind("<Leave>", on_leave)
    
    checkbox = tk.Canvas(row_frame, width=20, height=20, bg=surface_color, highlightthickness=1, 
                         highlightbackground=border_color, cursor="hand2")
    checkbox.create_rectangle(2, 2, 18, 18, outline=border_color, width=2)
    checkbox.pack(side="left", padx=(0, 12), pady=8)
    checkbox.bind("<Button-1>", lambda e: mark_done(reminder["id"]))
    
    content_frame = tk.Frame(row_frame, bg=surface_color)
    content_frame.pack(side="left", fill="x", expand=True, pady=8)
    
    title_label = tk.Label(content_frame, text=reminder["title"], 
                           font=("Segoe UI", 12), fg=text_color, bg=surface_color,
                           anchor="w")
    title_label.pack(anchor="w")
    
    time_label = tk.Label(row_frame, text=reminder["due_time"], 
                          font=("Segoe UI", 10), fg=accent_color, bg=surface_color)
    time_label.pack(side="right", padx=10, pady=8)
    
    delete_btn = tk.Button(row_frame, text="✕", font=('Segoe UI', 9),
                           bg=surface_color, fg=text_color,
                           activebackground=hover_color, activeforeground=text_color,
                           relief='flat', cursor="hand2",
                           command=lambda r=reminder["id"]: delete_reminder(r))
    delete_btn.pack(side="right", padx=5, pady=8)

init_db()

bg_color, surface_color, text_color, accent_color, border_color, hover_color = setup_theme("dark")

root = tk.Tk()
root.title("Ежедневник")
root.geometry("700x850")
root.minsize(600, 600)
root.configure(bg=bg_color)

header_frame = tk.Frame(root, bg=bg_color, padx=20, pady=10)
header_frame.pack(fill="x")

theme_btn = tk.Button(header_frame, text="☀️ Светлая тема", 
                      font=('Segoe UI', 10),
                      bg=surface_color, fg=text_color,
                      activebackground=hover_color, activeforeground=text_color,
                      relief='flat', cursor="hand2",
                      command=toggle_theme)
theme_btn.pack(side="right")

input_container = tk.Frame(root, bg=surface_color, padx=30, pady=20)
input_container.pack(fill="x", padx=30, pady=20)

title_label = tk.Label(input_container, text="Новое напоминание", 
                       font=('Segoe UI', 16, 'bold'),
                       bg=surface_color, fg=text_color)
title_label.pack(anchor="w", pady=(0, 15))

name_lbl = tk.Label(input_container, text="Название:", 
                    bg=surface_color, fg=text_color,
                    font=('Segoe UI', 11))
name_lbl.pack(anchor="w")
entry_title = tk.Entry(input_container, font=("Segoe UI", 12), 
                       bg=surface_color, fg=text_color,
                       insertbackground=text_color,
                       relief='solid', highlightthickness=1, highlightbackground=border_color)
entry_title.pack(fill="x", pady=4)

desc_lbl = tk.Label(input_container, text="Описание:", 
                    bg=surface_color, fg=text_color,
                    font=('Segoe UI', 11))
desc_lbl.pack(anchor="w", pady=(10, 0))
text_desc = tk.Text(input_container, height=3, font=("Segoe UI", 11), 
                    bg=surface_color, fg=text_color, 
                    insertbackground=text_color,
                    relief='solid', highlightthickness=1, highlightbackground=border_color)
text_desc.pack(fill="x", pady=4)

time_lbl = tk.Label(input_container, text="Дата и время:", 
                    bg=surface_color, fg=text_color,
                    font=('Segoe UI', 11))
time_lbl.pack(anchor="w", pady=(10, 0))

datetime_frame = tk.Frame(input_container, bg=surface_color)
datetime_frame.pack(fill="x", pady=4)

year_lbl = tk.Label(datetime_frame, text="Год:", 
                    bg=surface_color, fg=text_color,
                    font=('Segoe UI', 10))
year_lbl.grid(row=0, column=0, padx=5, pady=5, sticky="e")

now = datetime.now()
default_time = now

spin_year = tk.Spinbox(datetime_frame, from_=now.year, to=now.year+5, width=8,
                       font=("Segoe UI", 11),
                       bg=surface_color, fg=text_color,
                       highlightbackground=border_color, highlightthickness=1,
                       relief='solid')
spin_year.delete(0, tk.END)
spin_year.insert(0, str(default_time.year))
spin_year.grid(row=0, column=1, padx=5, pady=5)

month_lbl = tk.Label(datetime_frame, text="Месяц:", 
                     bg=surface_color, fg=text_color,
                     font=('Segoe UI', 10))
month_lbl.grid(row=0, column=2, padx=5, pady=5, sticky="e")

spin_month = tk.Spinbox(datetime_frame, from_=1, to=12, width=6,
                        font=("Segoe UI", 11),
                        bg=surface_color, fg=text_color,
                        highlightbackground=border_color, highlightthickness=1,
                        relief='solid',
                        format="%02.0f")
spin_month.delete(0, tk.END)
spin_month.insert(0, str(default_time.month))
spin_month.grid(row=0, column=3, padx=5, pady=5)

day_lbl = tk.Label(datetime_frame, text="День:", 
                   bg=surface_color, fg=text_color,
                   font=('Segoe UI', 10))
day_lbl.grid(row=0, column=4, padx=5, pady=5, sticky="e")

spin_day = tk.Spinbox(datetime_frame, from_=1, to=31, width=6,
                      font=("Segoe UI", 11),
                      bg=surface_color, fg=text_color,
                      highlightbackground=border_color, highlightthickness=1,
                      relief='solid',
                      format="%02.0f")
spin_day.delete(0, tk.END)
spin_day.insert(0, str(default_time.day))
spin_day.grid(row=0, column=5, padx=5, pady=5)

hour_lbl = tk.Label(datetime_frame, text="Час:", 
                    bg=surface_color, fg=text_color,
                    font=('Segoe UI', 10))
hour_lbl.grid(row=1, column=0, padx=5, pady=5, sticky="e")

spin_hour = tk.Spinbox(datetime_frame, from_=0, to=23, width=6,
                       font=("Segoe UI", 11),
                       bg=surface_color, fg=text_color,
                       highlightbackground=border_color, highlightthickness=1,
                       relief='solid',
                       format="%02.0f")
spin_hour.delete(0, tk.END)
spin_hour.insert(0, str(default_time.hour))
spin_hour.grid(row=1, column=1, padx=5, pady=5)

min_lbl = tk.Label(datetime_frame, text="Минуты:", 
                   bg=surface_color, fg=text_color,
                   font=('Segoe UI', 10))
min_lbl.grid(row=1, column=2, padx=5, pady=5, sticky="e")

spin_min = tk.Spinbox(datetime_frame, from_=0, to=59, width=6,
                      font=("Segoe UI", 11),
                      bg=surface_color, fg=text_color,
                      highlightbackground=border_color, highlightthickness=1,
                      relief='solid',
                      format="%02.0f")
spin_min.delete(0, tk.END)
spin_min.insert(0, str(default_time.minute))
spin_min.grid(row=1, column=3, padx=5, pady=5)

set_time_btn = tk.Button(datetime_frame, text="✓ Установить", 
                         font=('Segoe UI', 9, 'bold'),
                         bg=accent_color, fg='white',
                         activebackground=accent_hover, activeforeground='white',
                         relief='flat', cursor="hand2",
                         command=set_datetime)
set_time_btn.grid(row=1, column=4, columnspan=2, padx=10, pady=5)

entry_due = tk.Entry(input_container, font=("Segoe UI", 12), 
                     bg=surface_color, fg=accent_color,
                     state="readonly",
                     insertbackground=text_color,
                     relief='solid', highlightthickness=1, highlightbackground=border_color)
entry_due.pack(fill="x", pady=4)

entry_due.config(state="normal")
entry_due.insert(0, default_time.strftime("%Y-%m-%d %H:%M"))
entry_due.config(state="readonly")

add_btn = tk.Button(input_container, text="Добавить", 
                    font=('Segoe UI', 10, 'bold'),
                    bg=accent_color, fg='white',
                    activebackground=accent_hover, activeforeground='white',
                    relief='flat', cursor="hand2",
                    command=add_reminder)
add_btn.pack(fill="x", pady=15)

list_frame = tk.Frame(root, bg=bg_color)
list_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(list_frame, bg=bg_color, highlightthickness=0)
scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview,
                         bg=surface_color, troughcolor=bg_color,
                         activebackground=hover_color)
scrollable_frame = tk.Frame(canvas, bg=bg_color)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", _on_mousewheel)

load_reminders()

root.mainloop()
