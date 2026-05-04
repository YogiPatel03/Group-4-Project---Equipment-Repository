import tkinter as tk
from tkinter import messagebox
from auth import login_user

def clear_errors():
    error_label.config(text="")
    email_entry.config(highlightbackground="#93c5fd", highlightcolor="#2563eb")
    password_entry.config(highlightbackground="#93c5fd", highlightcolor="#2563eb")

def set_error(message):
    email_entry.config(highlightbackground="#dc2626", highlightcolor="#dc2626")
    password_entry.config(highlightbackground="#dc2626", highlightcolor="#dc2626")
    error_label.config(text=f"⚠  {message}")
    root.update_idletasks()

def handle_login():
    clear_errors()

    email = email_entry.get().strip()
    password = password_entry.get().strip()

    if not email or not password:
        set_error("Please enter your email and password.")
        return

    try:
        user = login_user(email, password)
    except Exception as e:
        print(f"login_user raised an exception: {e}")
        set_error("Email or password is incorrect.")
        return

    if user is None:
        set_error("Email or password is incorrect.")
        return

    if user["role"] == "admin":
        messagebox.showinfo("Success", "Admin login successful.")
    else:
        messagebox.showinfo("Success", "Student login successful.")

root = tk.Tk()
root.title("School Inventory Login")
root.state("zoomed")
root.configure(bg="#dbeafe")

# ── Header ────────────────────────────────────────────────────────────────────
header = tk.Frame(root, bg="#2563eb", height=130)
header.pack(fill="x")
header.pack_propagate(False)

header_content = tk.Frame(header, bg = "#2563eb")
header_content.place(relx = 0.5, rely = 0.45, anchor = "center")

tk.Label(
    header_content,
    text="School Inventory",
    font=("Avenir Next", 30, "bold"),
    bg="#2563eb",
    fg="white"
).pack(pady=(25, 0))

tk.Label(
    header_content,
    text="Checkout Management System",
    font=("Avenir Next", 14),
    bg="#2563eb",
    fg="#dbeafe"
).pack(pady = (2, 0))

# ── Card ──────────────────────────────────────────────────────────────────────
card = tk.Frame(root, bg="white", padx=40, pady=35)
card.place(relx=0.5, rely=0.58, anchor="center")

tk.Label(
    card,
    text="Welcome Back!",
    font=("Avenir Next", 22, "bold"),
    bg="white",
    fg="#1e3a8a"
).pack(pady=(0, 5))

tk.Label(
    card,
    text="Log in to continue",
    font=("Avenir Next", 12),
    bg="white",
    fg="#64748b"
).pack(pady=(0, 20))

# ── Email ─────────────────────────────────────────────────────────────────────
tk.Label(
    card,
    text="Email",
    font=("Avenir Next", 12, "bold"),
    bg="white",
    fg="#334155"
).pack(anchor="w")

email_entry = tk.Entry(
    card,
    width=30,
    font=("Avenir Next", 13),
    bd=2,
    relief="solid",
    highlightthickness=1,
    highlightbackground="#93c5fd",
    highlightcolor="#2563eb"
)
email_entry.pack(pady=(5, 15), ipady=8)

# ── Password ──────────────────────────────────────────────────────────────────
tk.Label(
    card,
    text="Password",
    font=("Avenir Next", 12, "bold"),
    bg="white",
    fg="#334155"
).pack(anchor="w")

password_entry = tk.Entry(
    card,
    width=30,
    font=("Avenir Next", 13),
    show="*",
    bd=2,
    relief="solid",
    highlightthickness=1,
    highlightbackground="#93c5fd",
    highlightcolor="#2563eb"
)
password_entry.pack(pady=(5, 10), ipady=8)

# ── Single error label ────────────────────────────────────────────────────────
error_label = tk.Label(
    card,
    text="",
    font=("Avenir Next", 10),
    bg="white",
    fg="#dc2626"
)
error_label.pack(pady=(0, 10))

# ── Login button ──────────────────────────────────────────────────────────────
login_button = tk.Button(
    card,
    text="Login",
    font=("Avenir Next", 13, "bold"),
    bg="#f97316",
    fg="Black",
    activebackground="#ea580c",
    activeforeground="white",
    width=22,
    bd=0,
    cursor="hand2",
    command=handle_login
)
login_button.pack(ipady=9)

root.mainloop()