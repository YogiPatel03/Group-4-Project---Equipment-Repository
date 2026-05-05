import tkinter as tk
from tkinter import ttk, messagebox
from .db_connection import get_connection


def open_student_dashboard(login_root, user):
    login_root.withdraw()

    dashboard = tk.Toplevel()
    dashboard.title("Student Dashboard")
    dashboard.state("zoomed")
    dashboard.configure(bg="#dbeafe")

    student_id = user["user_id"]

    def logout():
        dashboard.destroy()
        login_root.deiconify()

    def run_query(query, params=None, fetch=False):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def clear_tree(tree):
        for row in tree.get_children():
            tree.delete(row)

    #  Header 
    header = tk.Frame(dashboard, bg="#2563eb", height=100)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text=f"Student Dashboard - Welcome, {user['first_name']}",
        font=("Avenir Next", 26, "bold"),
        bg="#2563eb",
        fg="white"
    ).place(relx=0.03, rely=0.5, anchor="w")

    tk.Button(
        header,
        text="Logout",
        font=("Avenir Next", 13, "bold"),
        bg="#f97316",
        fg="black",
        activebackground="#ea580c",
        activeforeground="white",
        bd=0,
        width=14,
        cursor="hand2",
        command=logout
    ).place(relx=0.95, rely=0.5, anchor="e")

    #  Tabs 
    notebook = ttk.Notebook(dashboard)
    notebook.pack(fill="both", expand=True, padx=25, pady=25)

    available_tab = tk.Frame(notebook, bg="#f8fafc")
    checked_out_tab = tk.Frame(notebook, bg="#f8fafc")
    history_tab = tk.Frame(notebook, bg="#f8fafc")
    account_tab = tk.Frame(notebook, bg="#f8fafc")

    notebook.add(available_tab, text="Available Equipment")
    notebook.add(checked_out_tab, text="My Checked Out Items")
    notebook.add(history_tab, text="My History")
    notebook.add(account_tab, text="My Account")

    # Available Equipment Tab
    available_columns = ("equipment_id", "item_name", "category", "condition_status")

    available_tree = ttk.Treeview(
        available_tab,
        columns=available_columns,
        show="headings",
        height=18
    )

    for col in available_columns:
        available_tree.heading(col, text=col.replace("_", " ").title())
        available_tree.column(col, width=200, anchor="center")

    available_tree.pack(fill="both", expand=True, padx=20, pady=20)

    def load_available_equipment():
        clear_tree(available_tree)

        try:
            rows = run_query(
                """
                SELECT equipment_id, item_name, category, condition_status
                FROM vw_available_equipment
                """,
                fetch=True
            )

            for row in rows:
                available_tree.insert(
                    "",
                    "end",
                    values=(
                        row["equipment_id"],
                        row["item_name"],
                        row["category"],
                        row["condition_status"]
                    )
                )

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def checkout_selected_item():
        selected = available_tree.focus()

        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to checkout.")
            return

        equipment_id = available_tree.item(selected, "values")[0]

        try:
            run_query(
                """
                INSERT INTO Checkout_Records
                (user_id, equipment_id, checkout_date, due_date, checkout_status)
                VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), 'checked_out')
                """,
                (student_id, equipment_id)
            )

            messagebox.showinfo("Success", "Item checked out successfully.")
            load_available_equipment()
            load_my_checked_out_items()
            load_my_history()

        except Exception as e:
            messagebox.showerror("Checkout Failed", str(e))

    tk.Button(
        available_tab,
        text="Checkout Selected Item",
        font=("Avenir Next", 13, "bold"),
        bg="#f97316",
        fg="black",
        activebackground="#ea580c",
        activeforeground="white",
        bd=0,
        width=24,
        cursor="hand2",
        command=checkout_selected_item
    ).pack(pady=(0, 20), ipady=8)

    # Checked Out Items Tab
    checked_columns = (
        "checkout_id",
        "equipment_id",
        "item_name",
        "checkout_date",
        "due_date",
        "checkout_status"
    )

    checked_tree = ttk.Treeview(
        checked_out_tab,
        columns=checked_columns,
        show="headings",
        height=18
    )

    for col in checked_columns:
        checked_tree.heading(col, text=col.replace("_", " ").title())
        checked_tree.column(col, width=170, anchor="center")

    checked_tree.pack(fill="both", expand=True, padx=20, pady=20)

    def load_my_checked_out_items():
        clear_tree(checked_tree)

        try:
            rows = run_query(
                """
                SELECT checkout_id, equipment_id, item_name,
                       checkout_date, due_date, checkout_status
                FROM vw_user_checkout_history
                WHERE user_id = %s AND checkout_status = 'checked_out'
                """,
                (student_id,),
                fetch=True
            )

            for row in rows:
                checked_tree.insert(
                    "",
                    "end",
                    values=(
                        row["checkout_id"],
                        row["equipment_id"],
                        row["item_name"],
                        row["checkout_date"],
                        row["due_date"],
                        row["checkout_status"]
                    )
                )

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def return_selected_item():
        selected = checked_tree.focus()

        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to return.")
            return

        checkout_id = checked_tree.item(selected, "values")[0]

        try:
            run_query(
                """
                UPDATE Checkout_Records
                SET checkout_status = 'returned', return_date = NOW()
                WHERE checkout_id = %s AND user_id = %s
                """,
                (checkout_id, student_id)
            )

            messagebox.showinfo("Success", "Item returned successfully.")
            load_available_equipment()
            load_my_checked_out_items()
            load_my_history()

        except Exception as e:
            messagebox.showerror("Return Failed", str(e))

    tk.Button(
        checked_out_tab,
        text="Return Selected Item",
        font=("Avenir Next", 13, "bold"),
        bg="#f97316",
        fg="black",
        activebackground="#ea580c",
        activeforeground="white",
        bd=0,
        width=24,
        cursor="hand2",
        command=return_selected_item
    ).pack(pady=(0, 20), ipady=8)

    # History Tab
    history_columns = (
        "checkout_id",
        "item_name",
        "checkout_date",
        "due_date",
        "return_date",
        "checkout_status"
    )

    history_tree = ttk.Treeview(
        history_tab,
        columns=history_columns,
        show="headings",
        height=18
    )

    for col in history_columns:
        history_tree.heading(col, text=col.replace("_", " ").title())
        history_tree.column(col, width=180, anchor="center")

    history_tree.pack(fill="both", expand=True, padx=20, pady=20)

    def load_my_history():
        clear_tree(history_tree)

        try:
            rows = run_query(
                """
                SELECT checkout_id, item_name, checkout_date,
                       due_date, return_date, checkout_status
                FROM vw_user_checkout_history
                WHERE user_id = %s
                ORDER BY checkout_date DESC
                """,
                (student_id,),
                fetch=True
            )

            for row in rows:
                history_tree.insert(
                    "",
                    "end",
                    values=(
                        row["checkout_id"],
                        row["item_name"],
                        row["checkout_date"],
                        row["due_date"],
                        row["return_date"],
                        row["checkout_status"]
                    )
                )

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

   # ============================================================
# Account Tab
# ============================================================
    account_tab.configure(bg="#f1f5f9")

    account_card = tk.Frame(
        account_tab,
        bg="white",
        padx=60,
        pady=45,
        highlightbackground="#e2e8f0",
        highlightthickness=1
    )
    account_card.place(relx=0.5, rely=0.48, anchor="center")

    tk.Label(
        account_card,
        text="My Account",
        font=("Avenir Next", 24, "bold"),
        bg="white",
        fg="#1e3a8a"
    ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

    tk.Label(
        account_card,
        text="View and update your personal information.",
        font=("Avenir Next", 12),
        bg="white",
        fg="#64748b"
    ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 25))

    tk.Label(
        account_card,
        text="Profile Information",
        font=("Avenir Next", 15, "bold"),
        bg="white",
        fg="#0f172a"
    ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 15))


    def make_account_field(row, label_text, readonly=False):
        tk.Label(
            account_card,
            text=label_text,
            font=("Avenir Next", 12, "bold"),
            bg="white",
            fg="#334155",
            anchor="w"
        ).grid(row=row, column=0, sticky="w", pady=9)

        entry = tk.Entry(
            account_card,
            width=34,
            font=("Avenir Next", 12),
            bg="#f8fafc",
            fg="#111827",
            relief="solid",
            bd=1,
            readonlybackground="#e5e7eb"
        )
        entry.grid(row=row, column=1, sticky="w", padx=(25, 0), pady=9, ipady=7)

        if readonly:
            entry.config(state="readonly")

        return entry


    first_name_entry = make_account_field(3, "First Name")
    last_name_entry = make_account_field(4, "Last Name")
    email_entry = make_account_field(5, "Email", readonly=True)
    phone_entry = make_account_field(6, "Phone")


    def load_my_account():
        try:
            rows = run_query(
                """
                SELECT first_name, last_name, email, phone
                FROM Users
                WHERE user_id = %s
                """,
                (student_id,),
                fetch=True
            )

            if rows:
                account = rows[0]

                first_name_entry.delete(0, tk.END)
                last_name_entry.delete(0, tk.END)
                phone_entry.delete(0, tk.END)

                email_entry.config(state="normal")
                email_entry.delete(0, tk.END)

                first_name_entry.insert(0, account["first_name"] or "")
                last_name_entry.insert(0, account["last_name"] or "")
                email_entry.insert(0, account["email"] or "")
                phone_entry.insert(0, account["phone"] or "")

                email_entry.config(state="readonly")

        except Exception as e:
            messagebox.showerror("Database Error", str(e))


    def update_my_account():
        first_name = first_name_entry.get().strip()
        last_name = last_name_entry.get().strip()
        phone = phone_entry.get().strip()

        
        if phone and not phone.isdigit():
            messagebox.showwarning(
                "Invalid Phone Number",
                "Phone number can only contain numbers."
            )
            return

        if not first_name or not last_name:
            messagebox.showwarning(
                "Missing Information",
                "First name and last name are required."
            )
            return

        try:
            run_query(
                """
                UPDATE Users
                SET first_name = %s,
                    last_name = %s,
                    phone = %s
                WHERE user_id = %s
                """,
                (first_name, last_name, phone, student_id)
            )

            messagebox.showinfo("Success", "Account updated successfully.")

        except Exception as e:
            messagebox.showerror("Update Failed", str(e))


    button_row = tk.Frame(account_card, bg="white")
    button_row.grid(row=7, column=0, columnspan=2, sticky="e", pady=(25, 0))

    tk.Button(
        button_row,
        text="Save Changes",
        font=("Avenir Next", 12, "bold"),
        bg="#f97316",
        fg="black",
        activebackground="#ea580c",
        activeforeground="white",
        bd=0,
        width=18,
        cursor="hand2",
        command=update_my_account
    ).pack(ipady=8)
    #  Load data 
    load_available_equipment()
    load_my_checked_out_items()
    load_my_history()
    load_my_account()