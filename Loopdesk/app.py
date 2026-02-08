import tkinter as tk
import sqlite3
from datetime import date, timedelta

DB = "habits.db"

XP_PER_TASK = 10

def get_connection():
    return sqlite3.connect(DB)

def get_player():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS player (xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1)")
    cursor.execute("SELECT xp, level FROM player")
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO player (xp, level) VALUES (0,1)")
        conn.commit()
        row = (0,1)
    conn.close()
    return row

def update_player(xp, level):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE player SET xp=?, level=?", (xp, level))
    conn.commit()
    conn.close()

def xp_for_next(level):
    return 100 + (level-1)*50

def get_habits():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, streak FROM habits")
    habits = cursor.fetchall()
    conn.close()
    return habits

def add_habit():
    name = entry.get()
    if not name:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    entry.delete(0, tk.END)
    refresh()

def mark_done(habit_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT streak, last_completed FROM habits WHERE id = ?", (habit_id,))
    streak, last_completed = cursor.fetchone()

    today = date.today()
    if last_completed:
        last_completed = date.fromisoformat(last_completed)
        if last_completed == today:
            conn.close()
            return
        elif last_completed == today - timedelta(days=1):
            streak += 1
        else:
            streak = 1
    else:
        streak = 1

    cursor.execute(
        "UPDATE habits SET streak = ?, last_completed = ? WHERE id = ?",
        (streak, today.isoformat(), habit_id)
    )
    conn.commit()
    conn.close()

    give_xp()
    show_popup("✨ +10 XP")
    root.bell()
    refresh()

def give_xp():
    xp, level = get_player()
    xp += XP_PER_TASK
    needed = xp_for_next(level)
    if xp >= needed:
        xp -= needed
        level += 1
        show_popup(f"🏆 LEVEL UP! → {level}")
    update_player(xp, level)

def refresh():
    xp, level = get_player()
    needed = xp_for_next(level)
    level_label.config(text=f"Level {level}")
    xp_label.config(text=f"{xp}/{needed} XP")
    bar_width = int((xp/needed)*250)
    xp_bar.coords(bar_fill, 0, 0, bar_width, 10)

    for widget in habit_frame.winfo_children():
        widget.destroy()

    habits = get_habits()
    for h in habits:
        card = tk.Frame(habit_frame, bg="#1e1e1e", padx=12, pady=10)
        card.pack(fill="x", pady=6)

        tk.Label(card, text=h[1], fg="white", bg="#1e1e1e",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")

        tk.Label(card, text=f"🔥 {h[2]} day streak",
                 fg="#bbbbbb", bg="#1e1e1e",
                 font=("Segoe UI", 9)).pack(anchor="w")

        tk.Button(card, text="✔", font=("Segoe UI", 11),
                  command=lambda id=h[0]: mark_done(id),
                  bg="#2ecc71", fg="black", relief="flat",
                  width=3).place(relx=0.9, rely=0.25)

def show_popup(text):
    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.configure(bg="#f1c40f")
    tk.Label(popup, text=text, fg="black", bg="#f1c40f",
             font=("Segoe UI", 12, "bold")).pack(padx=20, pady=10)
    popup.after(1200, popup.destroy)
    x = root.winfo_x() + 100
    y = root.winfo_y() + 80
    popup.geometry(f"+{x}+{y}")

# --- UI ---
root = tk.Tk()
root.title("🎮 Habit Quest")
root.configure(bg="#121212")
root.geometry("380x550")

# XP BAR
top = tk.Frame(root, bg="#121212")
top.pack(pady=10)

level_label = tk.Label(top, text="Level 1", fg="white",
                       bg="#121212", font=("Segoe UI", 14, "bold"))
level_label.pack()

xp_label = tk.Label(top, text="0/100 XP", fg="#bbbbbb",
                    bg="#121212", font=("Segoe UI", 9))
xp_label.pack()

xp_bar = tk.Canvas(top, width=250, height=10, bg="#333", highlightthickness=0)
xp_bar.pack(pady=4)
bar_fill = xp_bar.create_rectangle(0, 0, 0, 10, fill="#f1c40f", width=0)

tk.Label(root, text="Habits", fg="white",
         bg="#121212", font=("Segoe UI", 16, "bold")).pack(pady=8)

entry = tk.Entry(root, width=28, font=("Segoe UI", 11))
entry.pack(pady=6)

tk.Button(root, text="➕ Add Habit", command=add_habit,
          bg="#3498db", fg="white", relief="flat",
          font=("Segoe UI", 10, "bold")).pack(pady=4)

habit_frame = tk.Frame(root, bg="#121212")
habit_frame.pack(fill="both", expand=True, pady=10)

refresh()
root.mainloop()
