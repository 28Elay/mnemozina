import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from db.local_storage import init_db, add_task, get_active_tasks, get_tasks_by_filter, mark_done, delete_task

THEMES = {
    "dark": {
        "bg": "#121212",
        "surface": "#1E1E1E",
        "text": "#E0E0E0",
        "accent": "#3B82F6",
        "accent_hover": "#2563EB",
        "border": "#374151",
        "hover": "#2D2D2D"
    },
    "light": {
        "bg": "#F3F4F6",
        "surface": "#FFFFFF",
        "text": "#1F2937",
        "accent": "#3B82F6",
        "accent_hover": "#2563EB",
        "border": "#D1D5DB",
        "hover": "#E5E7EB"
    }
}

PRIORITY_COLORS = {
    0: "#9CA3AF",
    1: "#6BCB77",
    2: "#FFD93D",
    3: "#FF6B6B"
}

PRIORITY_NAMES = {
    0: "Нет",
    1: "Низкий",
    2: "Средний",
    3: "Высокий"
}

current_theme = "dark"
current_filter = "all"

def get_theme():
    return THEMES[current_theme]

def toggle_theme():
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    theme_btn.config(text="Tёмная" if current_theme == "dark" else "Cветлая")
    apply_theme()
    load_reminders()

def apply_theme():
    t = get_theme()
    root.configure(bg=t["bg"])
    header_frame.configure(bg=t["bg"])
    filter_frame.configure(bg=t["bg"])
    input_container.configure(bg=t["surface"])
    canvas.configure(bg=t["bg"])
    scrollable_frame.configure(bg=t["bg"])

def set_datetime():
    try:
        vals = [int(w.get()) for w in (spin_year, spin_month, spin_day, spin_hour, spin_min)]
        chosen_dt = datetime(*vals)
        if chosen_dt < datetime.now():
            messagebox.showerror("Ошибка", "Нельзя установить время в прошлом!")
            return
        
        entry_due.config(state="normal")
        entry_due.delete(0, tk.END)
        entry_due.insert(0, chosen_dt.strftime("%Y-%m-%d %H:%M"))
        entry_due.config(state="readonly")
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректная дата!")

def reset_inputs():
    entry_title.delete(0, tk.END)
    text_desc.delete("1.0", tk.END)
    priority_var.set(0)
    
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
    title = entry_title.get().strip()
    desc = text_desc.get("1.0", tk.END).strip()
    due = entry_due.get().strip()
    priority = priority_var.get()
    
    if not title or not due:
        messagebox.showwarning("Внимание", "Заполните название и время!")
        return
    
    try:
        if datetime.strptime(due, "%Y-%m-%d %H:%M") < datetime.now():
            messagebox.showerror("Ошибка", "Время не может быть в прошлом!")
            return
    except ValueError:
        messagebox.showerror("Ошибка", "Неверный формат времени!")
        return
    
    add_task(title, desc, due, priority)
    reset_inputs()
    load_reminders()
    messagebox.showinfo("Успех", "Задача добавлена!")

def on_mark_done(task_id):
    mark_done(task_id)
    load_reminders()

def on_delete(task_id):
    if messagebox.askyesno("Подтверждение", "Удалить задачу?"):
        delete_task(task_id)
        load_reminders()

def load_reminders(filter_type="all"):
    global current_filter
    current_filter = filter_type
    
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    if filter_type == "all":
        reminders = get_active_tasks()
    else:
        reminders = get_tasks_by_filter(filter_type)
    
    if not reminders:
        filter_name = {"today": "Сегодня", "tomorrow": "Завтра"}.get(filter_type, "этом списке")
        tk.Label(
            scrollable_frame,
            text=f"Нет задач: {filter_name}",
            font=("Segoe UI", 14),
            fg=get_theme()["text"],
            bg=get_theme()["bg"]
        ).pack(pady=40)
        return
    
    for rem in reminders:
        create_task_row(scrollable_frame, rem)

def create_task_row(parent, rem):
    t = get_theme()
    row = tk.Frame(parent, bg=t["surface"])
    row.pack(fill="x", padx=20, pady=3)
    
    row.bind("<Enter>", lambda e: row.configure(bg=t["hover"]))
    row.bind("<Leave>", lambda e: row.configure(bg=t["surface"]))
    
    priority = rem.get("priority", 0)
    priority_color = PRIORITY_COLORS.get(priority, "#9CA3AF")
    
    priority_bar = tk.Frame(row, bg=priority_color, width=5)
    priority_bar.pack(side="left", fill="y", padx=(0, 10))
    
    chk = tk.Label(
        row, text="○", font=("Segoe UI", 16),
        fg=priority_color, bg=t["surface"], cursor="hand2"
    )
    chk.pack(side="left", padx=(0, 10))
    chk.bind("<Button-1>", lambda e, tid=rem["id"]: on_mark_done(tid))
    
    title_frame = tk.Frame(row, bg=t["surface"])
    title_frame.pack(side="left", fill="x", expand=True, pady=8)
    
    tk.Label(
        title_frame, text=rem["title"],
        font=("Segoe UI", 12, "bold"),
        fg=t["text"], bg=t["surface"], anchor="w"
    ).pack(anchor="w")
    
    if rem.get("description"):
        desc_text = rem["description"][:50] + ("..." if len(rem["description"]) > 50 else "")
        tk.Label(
            title_frame, text=desc_text,
            font=("Segoe UI", 9),
            fg=t["text"], bg=t["surface"], anchor="w"
        ).pack(anchor="w")
    
    tk.Label(
        row, text=rem["scheduled_at"],
        font=("Segoe UI", 10),
        fg=t["accent"], bg=t["surface"]
    ).pack(side="right", padx=10)
    
    priority_label = tk.Label(
        row, text=PRIORITY_NAMES.get(priority, ""),
        font=("Segoe UI", 8),
        fg=priority_color, bg=t["surface"]
    )
    priority_label.pack(side="right", padx=5)
    
    tk.Button(
        row, text="X", font=("Segoe UI", 10),
        bg=t["surface"], fg="#EF4444",
        activebackground=t["hover"], relief="flat",
        cursor="hand2", command=lambda tid=rem["id"]: on_delete(tid)
    ).pack(side="right", padx=5)

def make_spin(parent, text, r, c, from_, to, default):
    t = get_theme()
    tk.Label(
        parent, text=text, bg=t["surface"], fg=t["text"],
        font=("Segoe UI", 10)
    ).grid(row=r, column=c, padx=5, pady=5, sticky="e")
    
    spin = tk.Spinbox(
        parent, from_=from_, to=to, width=4,
        font=("Segoe UI", 11), bg=t["surface"], fg=t["text"],
        highlightbackground=t["border"], highlightthickness=1, relief="solid"
    )
    spin.delete(0, tk.END)
    spin.insert(0, str(default))
    spin.grid(row=r, column=c+1, padx=5, pady=5)
    return spin

init_db()
t = get_theme()

root = tk.Tk()
root.title("Mnemozina")
root.geometry("700x800")
root.minsize(600, 600)
root.configure(bg=t["bg"])

header_frame = tk.Frame(root, bg=t["bg"], padx=20, pady=10)
header_frame.pack(fill="x")

tk.Label(
    header_frame, text="Mnemozina",
    font=("Segoe UI", 18, "bold"),
    bg=t["bg"], fg=t["accent"]
).pack(side="left")

theme_btn = tk.Button(
    header_frame, text="Tёмная",
    font=("Segoe UI", 10), bg=t["surface"], fg=t["text"],
    activebackground=t["hover"], relief="flat",
    cursor="hand2", command=toggle_theme
)
theme_btn.pack(side="right")

filter_frame = tk.Frame(header_frame, bg=t["bg"])
filter_frame.pack(side="left", padx=20)

tk.Button(
    filter_frame, text="Bce", bg=t["surface"], fg=t["text"],
    relief="flat", cursor="hand2", command=lambda: load_reminders("all")
).pack(side="left", padx=3)

tk.Button(
    filter_frame, text="Cегодня", bg=t["surface"], fg=t["text"],
    relief="flat", cursor="hand2", command=lambda: load_reminders("today")
).pack(side="left", padx=3)

tk.Button(
    filter_frame, text="Zавтра", bg=t["surface"], fg=t["text"],
    relief="flat", cursor="hand2", command=lambda: load_reminders("tomorrow")
).pack(side="left", padx=3)

input_container = tk.Frame(root, bg=t["surface"], padx=30, pady=20)
input_container.pack(fill="x", padx=30, pady=20)

tk.Label(
    input_container, text="Hoвaя зaдaчa",
    font=("Segoe UI", 16, "bold"),
    bg=t["surface"], fg=t["text"]
).pack(anchor="w", pady=(0, 15))

tk.Label(
    input_container, text="Haзвaниe:",
    bg=t["surface"], fg=t["text"], font=("Segoe UI", 11)
).pack(anchor="w")
entry_title = tk.Entry(
    input_container, font=("Segoe UI", 12),
    bg=t["surface"], fg=t["text"],
    insertbackground=t["text"], relief="solid",
    highlightthickness=1, highlightbackground=t["border"]
)
entry_title.pack(fill="x", pady=4)

tk.Label(
    input_container, text="Oпиcaниe:",
    bg=t["surface"], fg=t["text"], font=("Segoe UI", 11)
).pack(anchor="w", pady=(10, 0))
text_desc = tk.Text(
    input_container, height=3, font=("Segoe UI", 11),
    bg=t["surface"], fg=t["text"],
    insertbackground=t["text"], relief="solid",
    highlightthickness=1, highlightbackground=t["border"]
)
text_desc.pack(fill="x", pady=4)

tk.Label(
    input_container, text="Пpиopитeт:",
    bg=t["surface"], fg=t["text"], font=("Segoe UI", 11)
).pack(anchor="w", pady=(10, 0))
priority_var = tk.IntVar(value=0)
priority_frame = tk.Frame(input_container, bg=t["surface"])
priority_frame.pack(fill="x", pady=4)

for val, name in [(0, "Heт"), (1, "Hизкий"), (2, "Cpeдний"), (3, "Bыcoкий")]:
    tk.Radiobutton(
        priority_frame, text=name, variable=priority_var, value=val,
        bg=t["surface"], fg=t["text"],
        selectcolor=t["accent"], activebackground=t["hover"]
    ).pack(side="left", padx=10)

tk.Label(
    input_container, text="Дaтa и вpeмя:",
    bg=t["surface"], fg=t["text"], font=("Segoe UI", 11)
).pack(anchor="w", pady=(10, 0))

datetime_frame = tk.Frame(input_container, bg=t["surface"])
datetime_frame.pack(fill="x", pady=4)

now = datetime.now()
spin_year = make_spin(datetime_frame, "Гoд:", 0, 0, now.year, now.year + 5, now.year)
spin_month = make_spin(datetime_frame, "Mec:", 0, 2, 1, 12, now.month)
spin_day = make_spin(datetime_frame, "Дeнь:", 0, 4, 1, 31, now.day)
spin_hour = make_spin(datetime_frame, "Чac:", 1, 0, 0, 23, now.hour)
spin_min = make_spin(datetime_frame, "Mин:", 1, 2, 0, 59, now.minute)

tk.Button(
    datetime_frame, text="Пpимeнить",
    font=("Segoe UI", 9, "bold"), bg=t["accent"], fg="white",
    activebackground=t["accent_hover"], relief="flat",
    cursor="hand2", command=set_datetime
).grid(row=1, column=4, columnspan=2, padx=10, pady=5)

entry_due = tk.Entry(
    input_container, font=("Segoe UI", 12),
    bg=t["surface"], fg=t["accent"], state="readonly",
    relief="solid", highlightthickness=1, highlightbackground=t["border"]
)
entry_due.pack(fill="x", pady=4)
entry_due.config(state="normal")
entry_due.insert(0, now.strftime("%Y-%m-%d %H:%M"))
entry_due.config(state="readonly")

tk.Button(
    input_container, text="Дoбaвить зaдaчy",
    font=("Segoe UI", 11, "bold"), bg=t["accent"], fg="white",
    activebackground=t["accent_hover"], relief="flat",
    cursor="hand2", command=add_reminder
).pack(fill="x", pady=15)

list_frame = tk.Frame(root, bg=t["bg"])
list_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(list_frame, bg=t["bg"], highlightthickness=0)
scrollbar = tk.Scrollbar(
    list_frame, orient="vertical", command=canvas.yview,
    bg=t["surface"], troughcolor=t["bg"], activebackground=t["hover"]
)
scrollable_frame = tk.Frame(canvas, bg=t["bg"])

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", on_mousewheel)

load_reminders()

root.mainloop()