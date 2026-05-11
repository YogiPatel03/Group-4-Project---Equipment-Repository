import tkinter as tk
from tkinter import ttk, messagebox

from .db_connection import get_connection


CONDITION_OPTIONS = ("good", "fair", "damaged")
AVAILABILITY_OPTIONS = ("available", "checked_out", "maintenance")
ROLE_OPTIONS = ("admin", "student")
STATUS_OPTIONS = ("active", "inactive")


def open_admin_dashboard(login_root, user):
    login_root.withdraw()

    dashboard = tk.Toplevel()
    dashboard.title("Admin Dashboard")
    dashboard.state("zoomed")
    dashboard.configure(bg="#dbeafe")

    def logout():
        dashboard.destroy()
        login_root.deiconify()

    dashboard.protocol("WM_DELETE_WINDOW", logout)

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

    def run_procedure(procedure_name):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.callproc(procedure_name)
            rows = []
            for result in cursor.stored_results():
                rows.extend(result.fetchall())
            conn.commit()
            return rows
        finally:
            cursor.close()
            conn.close()

    def clear_tree(tree):
        for row in tree.get_children():
            tree.delete(row)

    def selected_values(tree, message):
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", message)
            return None
        return tree.item(selected, "values")

    def set_entry(entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, "" if value is None else value)

    def set_combo(combo, value):
        combo.set("" if value is None else value)

    def make_tree(parent, columns, widths=None):
        frame = tk.Frame(parent, bg="#f8fafc")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=16)
        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            width = 160 if widths is None else widths.get(col, 160)
            tree.column(col, width=width, anchor="center", stretch=True)

        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        return tree

    def make_form(parent):
        form = tk.Frame(parent, bg="white", padx=25, pady=18)
        form.pack(fill="x", padx=20, pady=(0, 20))
        return form

    def make_entry(form, row, column, label_text, width=26):
        tk.Label(
            form,
            text=label_text,
            font=("Avenir Next", 11, "bold"),
            bg="white",
            fg="#334155"
        ).grid(row=row, column=column, sticky="w", padx=(0, 12), pady=(0, 6))

        entry = tk.Entry(
            form,
            width=width,
            font=("Avenir Next", 11),
            bg="#f8fafc",
            fg="#111827",
            relief="solid",
            bd=1
        )
        entry.grid(row=row + 1, column=column, sticky="ew", padx=(0, 12), pady=(0, 12), ipady=5)
        return entry

    def make_combo(form, row, column, label_text, values, width=24):
        tk.Label(
            form,
            text=label_text,
            font=("Avenir Next", 11, "bold"),
            bg="white",
            fg="#334155"
        ).grid(row=row, column=column, sticky="w", padx=(0, 12), pady=(0, 6))

        combo = ttk.Combobox(form, values=values, state="readonly", width=width)
        combo.grid(row=row + 1, column=column, sticky="ew", padx=(0, 12), pady=(0, 12), ipady=4)
        return combo

    def make_button(parent, text, command, width=16, bg="#f97316"):
        return tk.Button(
            parent,
            text=text,
            font=("Avenir Next", 11, "bold"),
            bg=bg,
            fg="black",
            activebackground="#ea580c",
            activeforeground="white",
            bd=0,
            width=width,
            cursor="hand2",
            command=command
        )

    def valid_email(email):
        return "@" in email and "." in email.split("@")[-1]

    # Header
    header = tk.Frame(dashboard, bg="#2563eb", height=100)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text=f"Admin Dashboard - Welcome, {user['first_name']}",
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

    # Tabs
    notebook = ttk.Notebook(dashboard)
    notebook.pack(fill="both", expand=True, padx=25, pady=25)

    overview_tab = tk.Frame(notebook, bg="#f8fafc")
    equipment_tab = tk.Frame(notebook, bg="#f8fafc")
    users_tab = tk.Frame(notebook, bg="#f8fafc")
    records_tab = tk.Frame(notebook, bg="#f8fafc")
    overdue_tab = tk.Frame(notebook, bg="#f8fafc")

    notebook.add(overview_tab, text="Overview")
    notebook.add(equipment_tab, text="Equipment Management")
    notebook.add(users_tab, text="User Management")
    notebook.add(records_tab, text="Checkout Records")
    notebook.add(overdue_tab, text="Overdue Report")

    # Overview Tab
    overview_content = tk.Frame(overview_tab, bg="#f8fafc")
    overview_content.pack(fill="both", expand=True, padx=30, pady=30)

    stat_frame = tk.Frame(overview_content, bg="#f8fafc")
    stat_frame.pack(fill="x")

    stat_labels = {}

    def add_stat_card(column, title):
        card = tk.Frame(
            stat_frame,
            bg="white",
            padx=28,
            pady=24,
            highlightbackground="#e2e8f0",
            highlightthickness=1
        )
        card.grid(row=0, column=column, sticky="nsew", padx=8)
        stat_frame.grid_columnconfigure(column, weight=1)

        tk.Label(
            card,
            text=title,
            font=("Avenir Next", 12, "bold"),
            bg="white",
            fg="#475569"
        ).pack(anchor="w")

        value_label = tk.Label(
            card,
            text="0",
            font=("Avenir Next", 28, "bold"),
            bg="white",
            fg="#1e3a8a"
        )
        value_label.pack(anchor="w", pady=(8, 0))
        stat_labels[title] = value_label

    add_stat_card(0, "Total Equipment")
    add_stat_card(1, "Available Items")
    add_stat_card(2, "Checked Out")
    add_stat_card(3, "Active Users")

    recent_columns = ("checkout_id", "borrower_name", "item_name", "checkout_date", "due_date", "checkout_status")
    tk.Label(
        overview_content,
        text="Recent Checkout Activity",
        font=("Avenir Next", 18, "bold"),
        bg="#f8fafc",
        fg="#0f172a"
    ).pack(anchor="w", pady=(30, 0))
    recent_tree = make_tree(overview_content, recent_columns)

    def load_overview():
        try:
            stats = run_query(
                """
                SELECT
                    (SELECT COUNT(*) FROM Equipment) AS total_equipment,
                    (SELECT COUNT(*) FROM Equipment WHERE availability_status = 'available') AS available_items,
                    (SELECT COUNT(*) FROM Checkout_Records WHERE checkout_status = 'checked_out') AS checked_out,
                    (SELECT COUNT(*) FROM Users WHERE status = 'active') AS active_users
                """,
                fetch=True
            )[0]

            stat_labels["Total Equipment"].config(text=stats["total_equipment"])
            stat_labels["Available Items"].config(text=stats["available_items"])
            stat_labels["Checked Out"].config(text=stats["checked_out"])
            stat_labels["Active Users"].config(text=stats["active_users"])

            clear_tree(recent_tree)
            rows = run_query(
                """
                SELECT checkout_id, borrower_name, item_name, checkout_date, due_date, checkout_status
                FROM vw_user_checkout_history
                ORDER BY checkout_date DESC
                LIMIT 10
                """,
                fetch=True
            )
            for row in rows:
                recent_tree.insert(
                    "",
                    "end",
                    values=(
                        row["checkout_id"],
                        row["borrower_name"],
                        row["item_name"],
                        row["checkout_date"],
                        row["due_date"],
                        row["checkout_status"]
                    )
                )
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    make_button(overview_content, "Refresh Overview", load_overview, width=18).pack(anchor="e", pady=(0, 10), ipady=8)

    # Equipment Management Tab
    equipment_columns = (
        "equipment_id",
        "item_name",
        "category",
        "serial_number",
        "condition_status",
        "availability_status",
        "location"
    )
    equipment_tree = make_tree(equipment_tab, equipment_columns)
    equipment_form = make_form(equipment_tab)

    equipment_name_entry = make_entry(equipment_form, 0, 0, "Item Name")
    equipment_category_entry = make_entry(equipment_form, 0, 1, "Category")
    equipment_serial_entry = make_entry(equipment_form, 0, 2, "Serial Number")
    equipment_condition_combo = make_combo(equipment_form, 0, 3, "Condition", CONDITION_OPTIONS)
    equipment_availability_combo = make_combo(equipment_form, 2, 0, "Availability", AVAILABILITY_OPTIONS)
    equipment_location_entry = make_entry(equipment_form, 2, 1, "Location")

    def clear_equipment_form():
        for entry in (equipment_name_entry, equipment_category_entry, equipment_serial_entry, equipment_location_entry):
            entry.delete(0, tk.END)
        equipment_condition_combo.set(CONDITION_OPTIONS[0])
        equipment_availability_combo.set(AVAILABILITY_OPTIONS[0])

    def load_equipment():
        clear_tree(equipment_tree)
        try:
            rows = run_query(
                """
                SELECT equipment_id, item_name, category, serial_number,
                       condition_status, availability_status, location
                FROM Equipment
                ORDER BY equipment_id
                """,
                fetch=True
            )
            for row in rows:
                equipment_tree.insert(
                    "",
                    "end",
                    values=(
                        row["equipment_id"],
                        row["item_name"],
                        row["category"],
                        row["serial_number"],
                        row["condition_status"],
                        row["availability_status"],
                        row["location"]
                    )
                )
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def fill_equipment_form(event=None):
        values = selected_values(equipment_tree, "Please select an equipment item.")
        if values is None:
            return

        set_entry(equipment_name_entry, values[1])
        set_entry(equipment_category_entry, values[2])
        set_entry(equipment_serial_entry, values[3])
        set_combo(equipment_condition_combo, values[4])
        set_combo(equipment_availability_combo, values[5])
        set_entry(equipment_location_entry, values[6])

    equipment_tree.bind("<<TreeviewSelect>>", fill_equipment_form)

    def read_equipment_form():
        item_name = equipment_name_entry.get().strip()
        category = equipment_category_entry.get().strip()
        serial_number = equipment_serial_entry.get().strip()
        condition_status = equipment_condition_combo.get().strip()
        availability_status = equipment_availability_combo.get().strip()
        location = equipment_location_entry.get().strip() or None

        if not item_name or not category or not serial_number:
            messagebox.showwarning("Missing Information", "Item name, category, and serial number are required.")
            return None

        if condition_status not in CONDITION_OPTIONS or availability_status not in AVAILABILITY_OPTIONS:
            messagebox.showwarning("Invalid Status", "Please choose valid condition and availability values.")
            return None

        return item_name, category, serial_number, condition_status, availability_status, location

    def add_equipment():
        values = read_equipment_form()
        if values is None:
            return

        try:
            run_query(
                """
                INSERT INTO Equipment
                (item_name, category, serial_number, condition_status, availability_status, location)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                values
            )
            messagebox.showinfo("Success", "Equipment added successfully.")
            clear_equipment_form()
            refresh_all()
        except Exception as e:
            messagebox.showerror("Add Equipment Failed", str(e))

    def update_equipment():
        selected = selected_values(equipment_tree, "Please select an equipment item to update.")
        if selected is None:
            return

        values = read_equipment_form()
        if values is None:
            return

        try:
            run_query(
                """
                UPDATE Equipment
                SET item_name = %s,
                    category = %s,
                    serial_number = %s,
                    condition_status = %s,
                    availability_status = %s,
                    location = %s
                WHERE equipment_id = %s
                """,
                (*values, selected[0])
            )
            messagebox.showinfo("Success", "Equipment updated successfully.")
            refresh_all()
        except Exception as e:
            messagebox.showerror("Update Equipment Failed", str(e))

    def delete_equipment():
        selected = selected_values(equipment_tree, "Please select an equipment item to delete.")
        if selected is None:
            return

        if not messagebox.askyesno("Confirm Delete", "Delete the selected equipment item?"):
            return

        try:
            run_query("DELETE FROM Equipment WHERE equipment_id = %s", (selected[0],))
            messagebox.showinfo("Success", "Equipment deleted successfully.")
            clear_equipment_form()
            refresh_all()
        except Exception as e:
            messagebox.showerror("Delete Equipment Failed", str(e))

    equipment_button_row = tk.Frame(equipment_form, bg="white")
    equipment_button_row.grid(row=3, column=2, columnspan=2, sticky="e")

    make_button(equipment_button_row, "Add", add_equipment).pack(side="left", padx=4, ipady=7)
    make_button(equipment_button_row, "Update", update_equipment).pack(side="left", padx=4, ipady=7)
    make_button(equipment_button_row, "Delete", delete_equipment, bg="#dc2626").pack(side="left", padx=4, ipady=7)
    make_button(equipment_button_row, "Clear", clear_equipment_form, bg="#94a3b8").pack(side="left", padx=4, ipady=7)

    # User Management Tab
    user_columns = ("user_id", "first_name", "last_name", "email", "role", "phone", "created_at", "status")
    users_tree = make_tree(users_tab, user_columns)
    users_form = make_form(users_tab)

    user_first_name_entry = make_entry(users_form, 0, 0, "First Name")
    user_last_name_entry = make_entry(users_form, 0, 1, "Last Name")
    user_email_entry = make_entry(users_form, 0, 2, "Email")
    user_password_entry = make_entry(users_form, 0, 3, "Password")
    user_role_combo = make_combo(users_form, 2, 0, "Role", ROLE_OPTIONS)
    user_phone_entry = make_entry(users_form, 2, 1, "Phone")
    user_status_combo = make_combo(users_form, 2, 2, "Status", STATUS_OPTIONS)

    def clear_user_form():
        for entry in (user_first_name_entry, user_last_name_entry, user_email_entry, user_password_entry, user_phone_entry):
            entry.delete(0, tk.END)
        user_role_combo.set("student")
        user_status_combo.set("active")

    def load_users():
        clear_tree(users_tree)
        try:
            rows = run_query(
                """
                SELECT user_id, first_name, last_name, email, role, phone, created_at, status
                FROM Users
                ORDER BY user_id
                """,
                fetch=True
            )
            for row in rows:
                users_tree.insert(
                    "",
                    "end",
                    values=(
                        row["user_id"],
                        row["first_name"],
                        row["last_name"],
                        row["email"],
                        row["role"],
                        row["phone"],
                        row["created_at"],
                        row["status"]
                    )
                )
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def fill_user_form(event=None):
        values = selected_values(users_tree, "Please select a user.")
        if values is None:
            return

        set_entry(user_first_name_entry, values[1])
        set_entry(user_last_name_entry, values[2])
        set_entry(user_email_entry, values[3])
        user_password_entry.delete(0, tk.END)
        set_combo(user_role_combo, values[4])
        set_entry(user_phone_entry, values[5])
        set_combo(user_status_combo, values[7])

    users_tree.bind("<<TreeviewSelect>>", fill_user_form)

    def read_user_form(require_password):
        first_name = user_first_name_entry.get().strip()
        last_name = user_last_name_entry.get().strip()
        email = user_email_entry.get().strip()
        password = user_password_entry.get().strip()
        role = user_role_combo.get().strip()
        phone = user_phone_entry.get().strip() or None
        status = user_status_combo.get().strip()

        if not first_name or not last_name or not email:
            messagebox.showwarning("Missing Information", "First name, last name, and email are required.")
            return None

        if require_password and not password:
            messagebox.showwarning("Missing Password", "Password is required when creating a user.")
            return None

        if not valid_email(email):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return None

        if role not in ROLE_OPTIONS or status not in STATUS_OPTIONS:
            messagebox.showwarning("Invalid User Settings", "Please choose valid role and status values.")
            return None

        return first_name, last_name, email, password, role, phone, status

    def add_user():
        values = read_user_form(require_password=True)
        if values is None:
            return

        first_name, last_name, email, password, role, phone, status = values

        try:
            run_query(
                """
                INSERT INTO Users
                (first_name, last_name, email, password_hash, role, phone, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (first_name, last_name, email, password, role, phone, status)
            )
            messagebox.showinfo("Success", "User added successfully.")
            clear_user_form()
            refresh_all()
        except Exception as e:
            messagebox.showerror("Add User Failed", str(e))

    def update_user():
        selected = selected_values(users_tree, "Please select a user to update.")
        if selected is None:
            return

        values = read_user_form(require_password=False)
        if values is None:
            return

        first_name, last_name, email, password, role, phone, status = values
        user_id = selected[0]

        try:
            if password:
                run_query(
                    """
                    UPDATE Users
                    SET first_name = %s,
                        last_name = %s,
                        email = %s,
                        password_hash = %s,
                        role = %s,
                        phone = %s,
                        status = %s
                    WHERE user_id = %s
                    """,
                    (first_name, last_name, email, password, role, phone, status, user_id)
                )
            else:
                run_query(
                    """
                    UPDATE Users
                    SET first_name = %s,
                        last_name = %s,
                        email = %s,
                        role = %s,
                        phone = %s,
                        status = %s
                    WHERE user_id = %s
                    """,
                    (first_name, last_name, email, role, phone, status, user_id)
                )

            messagebox.showinfo("Success", "User updated successfully.")
            refresh_all()
        except Exception as e:
            messagebox.showerror("Update User Failed", str(e))

    def delete_user():
        selected = selected_values(users_tree, "Please select a user to delete.")
        if selected is None:
            return

        if str(selected[0]) == str(user["user_id"]):
            messagebox.showwarning("Delete Blocked", "You cannot delete your own logged-in account.")
            return

        if not messagebox.askyesno("Confirm Delete", "Delete the selected user account?"):
            return

        try:
            run_query("DELETE FROM Users WHERE user_id = %s", (selected[0],))
            messagebox.showinfo("Success", "User deleted successfully.")
            clear_user_form()
            refresh_all()
        except Exception as e:
            messagebox.showerror("Delete User Failed", str(e))

    users_button_row = tk.Frame(users_form, bg="white")
    users_button_row.grid(row=3, column=2, columnspan=2, sticky="e")

    make_button(users_button_row, "Add", add_user).pack(side="left", padx=4, ipady=7)
    make_button(users_button_row, "Update", update_user).pack(side="left", padx=4, ipady=7)
    make_button(users_button_row, "Delete", delete_user, bg="#dc2626").pack(side="left", padx=4, ipady=7)
    make_button(users_button_row, "Clear", clear_user_form, bg="#94a3b8").pack(side="left", padx=4, ipady=7)

    # Checkout Records Tab
    records_columns = (
        "checkout_id",
        "borrower_name",
        "email",
        "item_name",
        "serial_number",
        "checkout_date",
        "due_date",
        "return_date",
        "checkout_status"
    )
    records_tree = make_tree(records_tab, records_columns)

    records_actions = tk.Frame(records_tab, bg="#f8fafc")
    records_actions.pack(fill="x", padx=20, pady=(0, 20))

    def load_records():
        clear_tree(records_tree)
        try:
            rows = run_query(
                """
                SELECT checkout_id, borrower_name, email, item_name, serial_number,
                       checkout_date, due_date, return_date, checkout_status
                FROM vw_user_checkout_history
                ORDER BY checkout_date DESC
                """,
                fetch=True
            )
            for row in rows:
                records_tree.insert(
                    "",
                    "end",
                    values=(
                        row["checkout_id"],
                        row["borrower_name"],
                        row["email"],
                        row["item_name"],
                        row["serial_number"],
                        row["checkout_date"],
                        row["due_date"],
                        row["return_date"],
                        row["checkout_status"]
                    )
                )
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def mark_record_returned():
        selected = selected_values(records_tree, "Please select a checkout record.")
        if selected is None:
            return

        if selected[8] == "returned":
            messagebox.showinfo("Already Returned", "This record is already marked as returned.")
            return

        try:
            run_query(
                """
                UPDATE Checkout_Records
                SET checkout_status = 'returned',
                    return_date = NOW()
                WHERE checkout_id = %s
                """,
                (selected[0],)
            )
            messagebox.showinfo("Success", "Checkout record marked as returned.")
            refresh_all()
        except Exception as e:
            messagebox.showerror("Return Update Failed", str(e))

    make_button(records_actions, "Refresh Records", load_records, width=18).pack(side="left", padx=4, ipady=8)
    make_button(records_actions, "Mark Returned", mark_record_returned, width=18).pack(side="left", padx=4, ipady=8)

    # Overdue Report Tab
    overdue_columns = (
        "checkout_id",
        "user_id",
        "first_name",
        "last_name",
        "email",
        "equipment_id",
        "item_name",
        "serial_number",
        "checkout_date",
        "due_date",
        "days_overdue"
    )
    overdue_tree = make_tree(overdue_tab, overdue_columns)
    overdue_actions = tk.Frame(overdue_tab, bg="#f8fafc")
    overdue_actions.pack(fill="x", padx=20, pady=(0, 20))

    def load_overdue_report():
        clear_tree(overdue_tree)
        try:
            rows = run_procedure("GetOverdueCheckouts")
            for row in rows:
                overdue_tree.insert(
                    "",
                    "end",
                    values=(
                        row["checkout_id"],
                        row["user_id"],
                        row["first_name"],
                        row["last_name"],
                        row["email"],
                        row["equipment_id"],
                        row["item_name"],
                        row["serial_number"],
                        row["checkout_date"],
                        row["due_date"],
                        row["days_overdue"]
                    )
                )
            load_records()
            load_overview()
        except Exception as e:
            messagebox.showerror("Overdue Report Failed", str(e))

    make_button(overdue_actions, "Run Overdue Report", load_overdue_report, width=22).pack(side="left", padx=4, ipady=8)

    def refresh_all():
        load_overview()
        load_equipment()
        load_users()
        load_records()

    clear_equipment_form()
    clear_user_form()
    refresh_all()
