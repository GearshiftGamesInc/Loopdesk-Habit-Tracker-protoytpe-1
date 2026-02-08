import tkinter as tk
import sqlite3
from datetime import date, timedelta

DB = "habits.db"

def get_connection():
    return sqlite3.connect(DB)

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
    show_popup("🔥 Streak +1!")
    root.bell()
    refresh()

def show_popup(text):
    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.configure(bg="#2ecc71")
    tk.Label(popup, text=text, fg="black", bg="#2ecc71",
             font=("Segoe UI", 12, "bold")).pack(padx=20, pady=10)
    popup.after(1200, popup.destroy)
    x = root.winfo_x() + 200
    y = root.winfo_y() + 100
    popup.geometry(f"+{x}+{y}")

def refresh():
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

        bar = tk.Canvas(card, width=220, height=6, bg="#333", highlightthickness=0)
        bar.pack(anchor="w", pady=4)
        fill = min(h[2] * 10, 220)
        bar.create_rectangle(0, 0, fill, 6, fill="#2ecc71", width=0)

        tk.Button(card, text="✔", font=("Segoe UI", 11),
                  command=lambda id=h[0]: mark_done(id),
                  bg="#2ecc71", fg="black", relief="flat",
                  width=3).place(relx=0.9, rely=0.25)

# --- UI ---
root = tk.Tk()
root.title("🔥 Habit Quest")
root.configure(bg="#121212")
root.geometry("380x550")

tk.Label(root, text="🎮 Habit Quest", fg="white",
         bg="#121212", font=("Segoe UI", 18, "bold")).pack(pady=10)

entry = tk.Entry(root, width=28, font=("Segoe UI", 11))
entry.pack(pady=6)

tk.Button(root, text="➕ Add Habit", command=add_habit,
          bg="#3498db", fg="white", relief="flat",
          font=("Segoe UI", 10, "bold")).pack(pady=4)

habit_frame = tk.Frame(root, bg="#121212")
habit_frame.pack(fill="both", expand=True, pady=10)

refresh()
root.mainloop()
