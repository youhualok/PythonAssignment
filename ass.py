import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# 1. Database Manager
class DatabaseManager:
    def __init__(self, db_name="condocare.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Initialize all database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                name TEXT NOT NULL,
                unit TEXT
            )""")

            # 2. Tickets Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resident_username TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                assigned_tech TEXT,
                rating INTEGER DEFAULT 0,
                feedback TEXT,
                created_at TEXT NOT NULL
            )""")

            # 3. Bookings Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resident_username TEXT NOT NULL,
                facility TEXT NOT NULL,
                date TEXT NOT NULL,
                slot TEXT NOT NULL,
                created_at TEXT NOT NULL
            )""")

            # 4. Bills Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resident_username TEXT NOT NULL,
                month TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                paid_at TEXT
            )""")

            # 5. Announcements Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                date_posted TEXT NOT NULL
            )""")
            
            conn.commit()
        self._seed_mock_data()

    def _seed_mock_data(self):
        """Seed only default Admin account (youhua / 123456)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Always guarantee Admin 'youhua' exists
            cursor.execute("INSERT OR REPLACE INTO users VALUES ('youhua', '123456', 'Admin', 'Youhua (Property Manager)', 'Manager Office')")
            conn.commit()

# 2. Main Application Window
class CondoCareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CondoCare Pro - Enterprise Condominium Management System")
        self.geometry("1020x700")
        self.minsize(950, 650)
        self.configure(bg="#0f172a")

        self.db = DatabaseManager()
        self.current_user = None

        self.setup_styles()
        self.container = tk.Frame(self, bg="#0f172a")
        self.container.pack(fill="both", expand=True)

        self.show_login_screen()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("TNotebook", background="#0f172a", borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 7], background="#334155", foreground="#f8fafc")
        self.style.map("TNotebook.Tab", background=[("selected", "#0284c7")], foreground=[("selected", "#ffffff")])
        
        self.style.configure("Treeview", background="#1e293b", foreground="#f8fafc", fieldbackground="#1e293b", font=("Segoe UI", 9), rowheight=28, borderwidth=0)
        self.style.configure("Treeview.Heading", background="#0f172a", foreground="#38bdf8", font=("Segoe UI", 10, "bold"), padding=[6, 6])
        self.style.map("Treeview", background=[("selected", "#0284c7")], foreground=[("selected", "#ffffff")])

    def show_login_screen(self):
        for w in self.container.winfo_children():
            w.destroy()

        card = tk.Frame(self.container, bg="#1e293b", bd=1, relief="solid", padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="🏢 CondoCare Pro", font=("Segoe UI", 24, "bold"), bg="#1e293b", fg="#38bdf8").pack(pady=(0, 4))
        tk.Label(card, text="Smart Condominium Maintenance Portal", font=("Segoe UI", 10), bg="#1e293b", fg="#94a3b8").pack(pady=(0, 25))

        tk.Label(card, text="Username", font=("Segoe UI", 9, "bold"), bg="#1e293b", fg="#cbd5e1", anchor="w").pack(fill="x")
        self.user_entry = tk.Entry(card, font=("Segoe UI", 11), bg="#334155", fg="white", insertbackground="white", bd=0, relief="flat", width=28)
        self.user_entry.pack(pady=(2, 12), ipady=6)

        tk.Label(card, text="Password", font=("Segoe UI", 9, "bold"), bg="#1e293b", fg="#cbd5e1", anchor="w").pack(fill="x")
        self.pass_entry = tk.Entry(card, show="*", font=("Segoe UI", 11), bg="#334155", fg="white", insertbackground="white", bd=0, relief="flat", width=28)
        self.pass_entry.pack(pady=(2, 20), ipady=6)

        tk.Button(card, text="LOG IN", font=("Segoe UI", 11, "bold"), bg="#3b82f6", fg="white", activebackground="#2563eb", activeforeground="white", bd=0, cursor="hand2", width=25, command=self.handle_login).pack(pady=4, ipady=6)
        tk.Button(card, text="Register Resident Account", font=("Segoe UI", 9, "bold"), bg="#0f172a", fg="#38bdf8", activebackground="#1e293b", activeforeground="white", bd=0, cursor="hand2", width=25, command=self.open_register_window).pack(pady=6, ipady=4)

    def handle_login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, role, name, unit FROM users WHERE username=? AND password=?", (username, password))
            row = cursor.fetchone()

            if row:
                self.current_user = {"username": row[0], "role": row[1], "name": row[2], "unit": row[3]}
                self.show_main_dashboard()
            else:
                messagebox.showerror("Authentication Failed", "Invalid Username or Password!")

    def open_register_window(self):
        reg_win = tk.Toplevel(self)
        reg_win.title("Resident Registration")
        reg_win.geometry("400x450")
        reg_win.configure(bg="#1e293b")
        reg_win.grab_set()

        tk.Label(reg_win, text="📝 Resident Sign Up", font=("Segoe UI", 16, "bold"), bg="#1e293b", fg="#38bdf8").pack(pady=20)

        fields = [("Username", "u"), ("Password", "p"), ("Full Name", "n"), ("Unit No. (e.g. Block A #03-01)", "unit")]
        entries = {}

        for label, key in fields:
            tk.Label(reg_win, text=label, font=("Segoe UI", 9, "bold"), bg="#1e293b", fg="#cbd5e1", anchor="w").pack(fill="x", padx=35, pady=(4, 0))
            e = tk.Entry(reg_win, font=("Segoe UI", 10), bg="#334155", fg="white", insertbackground="white", bd=0, show="*" if key == "p" else "")
            e.pack(fill="x", padx=35, pady=(0, 8), ipady=4)
            entries[key] = e

        def do_register():
            u = entries["u"].get().strip()
            p = entries["p"].get().strip()
            n = entries["n"].get().strip()
            unit = entries["unit"].get().strip()

            if not u or not p or not n or not unit:
                messagebox.showwarning("Incomplete Form", "All fields are required!", parent=reg_win)
                return

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users WHERE username=?", (u,))
                if cursor.fetchone():
                    messagebox.showerror("Duplicate Error", "Username already exists!", parent=reg_win)
                    return

                cursor.execute("INSERT INTO users VALUES (?, ?, 'Resident', ?, ?)", (u, p, n, unit))
                conn.commit()

            messagebox.showinfo("Registration Complete", "Account created successfully! You may now log in.", parent=reg_win)
            reg_win.destroy()

        tk.Button(reg_win, text="Submit Registration", font=("Segoe UI", 10, "bold"), bg="#10b981", fg="white", bd=0, cursor="hand2", command=do_register).pack(pady=20, ipady=6, padx=35, fill="x")

    def show_main_dashboard(self):
        for w in self.container.winfo_children():
            w.destroy()

        top_bar = tk.Frame(self.container, bg="#0f172a", height=55)
        top_bar.pack(side="top", fill="x")

        tk.Label(top_bar, text="🏢 CondoCare Pro", font=("Segoe UI", 14, "bold"), bg="#0f172a", fg="#38bdf8").pack(side="left", padx=20, pady=12)
        
        user_info = f"👤 {self.current_user['name']} | Role: {self.current_user['role']} | Unit: {self.current_user['unit']}"
        tk.Label(top_bar, text=user_info, font=("Segoe UI", 10), bg="#0f172a", fg="#94a3b8").pack(side="right", padx=15)
        
        tk.Button(top_bar, text="Logout", bg="#ef4444", fg="white", font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2", padx=10, command=self.show_login_screen).pack(side="right", padx=5, pady=12)
        tk.Button(top_bar, text="My Profile", bg="#0284c7", fg="white", font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2", padx=10, command=self.show_user_profile).pack(side="right", padx=5, pady=12)

        content = tk.Frame(self.container, bg="#0f172a")
        content.pack(side="top", fill="both", expand=True, padx=12, pady=12)

        role = self.current_user["role"]
        if role == "Resident":
            ResidentView(content, self)
        elif role == "Technician":
            TechnicianView(content, self)
        elif role == "Admin":
            AdminView(content, self)

    def show_user_profile(self):
        p_win = tk.Toplevel(self)
        p_win.title("My Profile")
        p_win.geometry("400x380")
        p_win.configure(bg="#1e293b")
        p_win.grab_set()

        tk.Label(p_win, text="👤 Account Overview", font=("Segoe UI", 16, "bold"), bg="#1e293b", fg="#38bdf8").pack(pady=20)

        u = self.current_user
        info_str = f"Username:  {u['username']}\nFull Name: {u['name']}\nRole:      {u['role']}\nLocation:  {u['unit']}"
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if u['role'] == 'Resident':
                cursor.execute("SELECT COUNT(*) FROM tickets WHERE resident_username=?", (u['username'],))
                t_cnt = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM bookings WHERE resident_username=?", (u['username'],))
                b_cnt = cursor.fetchone()[0]
                info_str += f"\n\n--- Activity Metrics ---\nTotal Maintenance Tickets: {t_cnt}\nTotal Facility Bookings:  {b_cnt}"
            elif u['role'] == 'Technician':
                cursor.execute("SELECT COUNT(*) FROM tickets WHERE assigned_tech=?", (u['username'],))
                t_cnt = cursor.fetchone()[0]
                info_str += f"\n\n--- Workload Metrics ---\nTotal Assigned Work Orders: {t_cnt}"

        card = tk.Frame(p_win, bg="#0f172a", padx=20, pady=20, bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(card, text=info_str, font=("Consolas", 10), bg="#0f172a", fg="#f8fafc", justify="left").pack(anchor="w")
        tk.Button(p_win, text="Close Window", bg="#64748b", fg="white", font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2", command=p_win.destroy).pack(pady=12)

# 3. Resident Portal View
class ResidentView(ttk.Notebook):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.db = app.db
        self.pack(fill="both", expand=True)

        self.tab_tickets = tk.Frame(self, bg="#1e293b")
        self.tab_facility = tk.Frame(self, bg="#1e293b")
        self.tab_fees = tk.Frame(self, bg="#1e293b")
        self.tab_announcements = tk.Frame(self, bg="#1e293b")

        self.add(self.tab_tickets, text=" Maintenance Tickets ")
        self.add(self.tab_facility, text=" Facility Booking ")
        self.add(self.tab_fees, text=" Maintenance Fees ")
        self.add(self.tab_announcements, text=" Announcements ")

        self.setup_tickets_tab()
        self.setup_facility_tab()
        self.setup_fees_tab()
        self.setup_announcements_tab()

    def setup_tickets_tab(self):
        left_frame = tk.LabelFrame(self.tab_tickets, text="Submit Service Request", bg="#1e293b", fg="#38bdf8", font=("Segoe UI", 11, "bold"), padx=15, pady=15)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(left_frame, text="Issue Title:", bg="#1e293b", fg="#cbd5e1").pack(anchor="w")
        self.t_title = tk.Entry(left_frame, width=28, bg="#334155", fg="white", bd=0)
        self.t_title.pack(pady=(0, 10), ipady=4)

        tk.Label(left_frame, text="Category:", bg="#1e293b", fg="#cbd5e1").pack(anchor="w")
        self.t_cat = ttk.Combobox(left_frame, values=["Plumbing", "Electrical", "Lift", "Appliance", "Common Area", "Pest Control"], width=26)
        self.t_cat.current(0)
        self.t_cat.pack(pady=(0, 10))

        tk.Label(left_frame, text="Description:", bg="#1e293b", fg="#cbd5e1").pack(anchor="w")
        self.t_desc = tk.Text(left_frame, height=5, width=28, bg="#334155", fg="white", bd=0)
        self.t_desc.pack(pady=(0, 12))

        tk.Button(left_frame, text="Submit Request", bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.submit_ticket).pack(fill="x", ipady=5)

        right_frame = tk.LabelFrame(self.tab_tickets, text="My Service Ticket History", bg="#1e293b", fg="#38bdf8", font=("Segoe UI", 11, "bold"), padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.ticket_listbox = tk.Listbox(right_frame, bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 10), bd=0, selectbackground="#0284c7")
        self.ticket_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(right_frame, command=self.ticket_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.ticket_listbox.config(yscrollcommand=scrollbar.set)

        btn_bar = tk.Frame(right_frame, bg="#1e293b")
        btn_bar.pack(fill="x", pady=(8, 0))
        tk.Button(btn_bar, text="⭐ Rate Completed Ticket", bg="#f59e0b", fg="white", font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2", command=self.rate_ticket).pack(side="left", ipady=3, padx=5)

        self.refresh_tickets()

    def submit_ticket(self):
        title = self.t_title.get().strip()
        cat = self.t_cat.get()
        desc = self.t_desc.get("1.0", "end").strip()

        if not title or not desc:
            messagebox.showwarning("Warning", "Please fill in all ticket details.")
            return

        keywords_high = ["leak", "water", "burst", "pipe", "fire", "smoke", "power", "electric", "stuck", "lift", "漏水", "断电", "爆管"]
        priority = "High (Auto-Detected)" if any(kw in title.lower() or kw in desc.lower() for kw in keywords_high) else "Medium"
        today = datetime.date.today().strftime("%Y-%m-%d")

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tickets (resident_username, title, category, description, priority, status, assigned_tech, rating, feedback, created_at)
                VALUES (?, ?, ?, ?, ?, 'Pending', 'Unassigned', 0, '', ?)
            """, (self.app.current_user["username"], title, cat, desc, priority, today))
            conn.commit()

        messagebox.showinfo("Success", f"Ticket Created!\nPriority Flagged: {priority}")
        self.t_title.delete(0, 'end')
        self.t_desc.delete("1.0", "end")
        self.refresh_tickets()

    def refresh_tickets(self):
        self.ticket_listbox.delete(0, 'end')
        self.ticket_ids = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, category, priority, status, assigned_tech, rating FROM tickets WHERE resident_username=? ORDER BY id DESC", (self.app.current_user["username"],))
            for r in cursor.fetchall():
                self.ticket_ids.append(r[0])
                rating_str = f" [Rating: {'⭐'*r[6]}]" if r[6] > 0 else ""
                line = f" #{r[0]} | [{r[2]}] {r[1]}  ---> Prio: {r[3]} | Status: {r[4]} | Tech: {r[5]}{rating_str}"
                self.ticket_listbox.insert('end', line)

    def rate_ticket(self):
        sel = self.ticket_listbox.curselection()
        if not sel:
            messagebox.showwarning("Selection Needed", "Please select a ticket from your history list.")
            return

        tid = self.ticket_ids[sel[0]]
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM tickets WHERE id=?", (tid,))
            status = cursor.fetchone()[0]

            if status != "Completed":
                messagebox.showwarning("Not Eligible", "You can only rate tickets marked as 'Completed'.")
                return

            val = simpledialog.askinteger("Rate Service", "Enter rating (1 to 5 stars):", minvalue=1, maxvalue=5, parent=self)
            if val:
                fb = simpledialog.askstring("Feedback", "Optional feedback review:", parent=self) or ""
                cursor.execute("UPDATE tickets SET rating=?, feedback=? WHERE id=?", (val, fb, tid))
                conn.commit()
                messagebox.showinfo("Thank You", "Feedback submitted successfully!")
                self.refresh_tickets()

    def setup_facility_tab(self):
        left_frame = tk.LabelFrame(self.tab_facility, text="Facility Booking Form", bg="#1e293b", fg="#38bdf8", font=("Segoe UI", 11, "bold"), padx=15, pady=15)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(left_frame, text="Select Facility:", bg="#1e293b", fg="#cbd5e1").pack(anchor="w")
        facilities = [
            "BBQ Pit 1", "BBQ Pit 2", "Function Hall", 
            "Tennis Court 1", "Badminton Court A", 
            "Ping Pong Court 1", "Ping Pong Court 2",
            "Karaoke Room A", "Karaoke Room B"
        ]
        self.fac_combo = ttk.Combobox(left_frame, values=facilities, width=26)
        self.fac_combo.current(0)
        self.fac_combo.pack(pady=(0, 10))

        tk.Label(left_frame, text="Date (YYYY-MM-DD):", bg="#1e293b", fg="#cbd5e1").pack(anchor="w")
        self.fac_date = tk.Entry(left_frame, width=28, bg="#334155", fg="white", bd=0)
        self.fac_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.fac_date.pack(pady=(0, 10), ipady=4)

        tk.Label(left_frame, text="Time Slot:", bg="#1e293b", fg="#cbd5e1").pack(anchor="w")
        slots = ["10:00 - 12:00", "12:00 - 14:00", "14:00 - 16:00", "16:00 - 18:00", "18:00 - 20:00", "20:00 - 22:00"]
        self.fac_slot = ttk.Combobox(left_frame, values=slots, width=26)
        self.fac_slot.current(0)
        self.fac_slot.pack(pady=(0, 15))

        tk.Button(left_frame, text="Confirm Booking", bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.book_facility).pack(fill="x", ipady=5)

        right_frame = tk.LabelFrame(self.tab_facility, text="My Active Reservations", bg="#1e293b", fg="#38bdf8", font=("Segoe UI", 11, "bold"), padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.booking_listbox = tk.Listbox(right_frame, bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 10), bd=0, selectbackground="#0284c7")
        self.booking_listbox.pack(fill="both", expand=True)

        self.refresh_bookings()

    def book_facility(self):
        fac = self.fac_combo.get()
        date_val = self.fac_date.get().strip()
        slot_val = self.fac_slot.get()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM bookings WHERE facility=? AND date=? AND slot=?", (fac, date_val, slot_val))
            if cursor.fetchone():
                messagebox.showerror("Conflict Error", "This time slot is ALREADY booked! Please select another time.")
                return

            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("INSERT INTO bookings (resident_username, facility, date, slot, created_at) VALUES (?, ?, ?, ?, ?)",
                           (self.app.current_user["username"], fac, date_val, slot_val, now))
            conn.commit()

        messagebox.showinfo("Success", "Facility successfully reserved!")
        self.refresh_bookings()

    def refresh_bookings(self):
        self.booking_listbox.delete(0, 'end')
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT facility, date, slot FROM bookings WHERE resident_username=? ORDER BY date DESC", (self.app.current_user["username"],))
            for r in cursor.fetchall():
                self.booking_listbox.insert('end', f" 📅 {r[0]}  |  Date: {r[1]}  |  Slot: {r[2]}")

    def setup_fees_tab(self):
        frame = tk.LabelFrame(self.tab_fees, text="Monthly Maintenance Statements", bg="#1e293b", fg="#38bdf8", font=("Segoe UI", 11, "bold"), padx=15, pady=15)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.fee_listbox = tk.Listbox(frame, bg="#0f172a", fg="#f8fafc", font=("Consolas", 11), bd=0, selectbackground="#0284c7")
        self.fee_listbox.pack(fill="both", expand=True, pady=(0, 10))

        tk.Button(frame, text="Pay Selected Bill Online (Simulate Gateway)", bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.pay_fee).pack(ipady=5)
        self.refresh_fees()

    def refresh_fees(self):
        self.fee_listbox.delete(0, 'end')
        self.fee_ids = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, month, amount, status, paid_at FROM bills WHERE resident_username=?", (self.app.current_user["username"],))
            for r in cursor.fetchall():
                self.fee_ids.append(r[0])
                status_str = f"PAID ({r[4]})" if r[3] == "Paid" else "UNPAID (Overdue)"
                self.fee_listbox.insert('end', f" Month: {r[1]}  |  Amount Due: ${r[2]:.2f}  |  Status: {status_str}")

    def pay_fee(self):
        sel = self.fee_listbox.curselection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please click on a bill from the list to make payment.")
            return

        bill_id = self.fee_ids[sel[0]]
        today = datetime.date.today().strftime("%Y-%m-%d")

        with self.db.get_connection() as conn:
            conn.cursor().execute("UPDATE bills SET status='Paid', paid_at=? WHERE id=?", (today, bill_id))
            conn.commit()

        messagebox.showinfo("Payment Successful", "Payment processed! Digital e-receipt generated.")
        self.refresh_fees()

    def setup_announcements_tab(self):
        frame = tk.LabelFrame(self.tab_announcements, text="Community Notice Board", bg="#1e293b", fg="#38bdf8", font=("Segoe UI", 11, "bold"), padx=15, pady=15)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        txt = tk.Text(frame, bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 11), bd=0)
        txt.pack(fill="both", expand=True)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, content, date_posted FROM announcements ORDER BY id DESC")
            rows = cursor.fetchall()
            if not rows:
                txt.insert('end', "No announcements published yet.\n")
            else:
                for r in rows:
                    txt.insert('end', f"📢 {r[0]} ({r[2]})\n", "title")
                    txt.insert('end', f"{r[1]}\n{'-'*65}\n\n")

        txt.tag_config("title", font=("Segoe UI", 11, "bold"), foreground="#38bdf8")
        txt.config(state="disabled")

# 4. Technician View
class TechnicianView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#1e293b")
        self.app = app
        self.db = app.db
        self.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(self, text="🛠️ Maintenance Technician Workbench", font=("Segoe UI", 14, "bold"), bg="#1e293b", fg="#38bdf8").pack(pady=10)

        frame = tk.Frame(self, bg="#1e293b")
        frame.pack(fill="both", expand=True)

        self.task_listbox = tk.Listbox(frame, bg="#0f172a", fg="#f8fafc", font=("Consolas", 10), bd=0, selectbackground="#0284c7")
        self.task_listbox.pack(fill="both", expand=True, pady=10)

        btn_box = tk.Frame(self, bg="#1e293b")
        btn_box.pack(pady=5)

        tk.Button(btn_box, text="Accept Task", bg="#0284c7", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", padx=15, command=lambda: self.update_status("In Progress")).pack(side="left", padx=10, ipady=4)
        tk.Button(btn_box, text="Mark Completed", bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", padx=15, command=lambda: self.update_status("Completed")).pack(side="left", padx=10, ipady=4)

        self.refresh_tasks()

    def refresh_tasks(self):
        self.task_listbox.delete(0, 'end')
        self.task_ids = []
        tech_username = self.app.current_user["username"]

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, category, priority, status, resident_username FROM tickets WHERE assigned_tech=? OR status='Pending' ORDER BY id DESC", (tech_username,))
            for r in cursor.fetchall():
                self.task_ids.append(r[0])
                self.task_listbox.insert('end', f" #{r[0]}  [{r[3]}]  {r[1]} ({r[2]})  |  Status: {r[4]}  |  Resident: {r[5]}")

    def update_status(self, new_status):
        sel = self.task_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select Task", "Please select a task from the list.")
            return

        tid = self.task_ids[sel[0]]
        tech_username = self.app.current_user["username"]

        with self.db.get_connection() as conn:
            conn.cursor().execute("UPDATE tickets SET status=?, assigned_tech=? WHERE id=?", (new_status, tech_username, tid))
            conn.commit()

        messagebox.showinfo("Status Updated", f"Ticket #{tid} status changed to {new_status}")
        self.refresh_tasks()

# 5. Admin Workbench View
class AdminView(ttk.Notebook):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.db = app.db
        self.pack(fill="both", expand=True)

        self.tab_analytics = tk.Frame(self, bg="#1e293b")
        self.tab_all_tickets = tk.Frame(self, bg="#1e293b")
        self.tab_users = tk.Frame(self, bg="#1e293b")
        self.tab_techs = tk.Frame(self, bg="#1e293b")
        self.tab_bookings = tk.Frame(self, bg="#1e293b")
        self.tab_announcements = tk.Frame(self, bg="#1e293b")

        self.add(self.tab_analytics, text=" Dashboard ")
        self.add(self.tab_all_tickets, text=" Service Tickets ")
        self.add(self.tab_users, text=" User Management ")
        self.add(self.tab_techs, text=" Technician Details ")
        self.add(self.tab_bookings, text=" Booking Logs ")
        self.add(self.tab_announcements, text=" Broadcast Notices ")

        self.setup_analytics_tab()
        self.setup_all_tickets_tab()
        self.setup_users_tab()
        self.setup_techs_tab()
        self.setup_bookings_tab()
        self.setup_announcements_tab()

        self.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        self.refresh_all_data()

    def refresh_all_data(self):
        self.setup_analytics_tab_content()
        self.refresh_all_tickets_table()
        self.refresh_users_table()
        self.refresh_techs_table()
        self.refresh_bookings_table()
        self.refresh_announcements()

    def setup_analytics_tab(self):
        self.chart_frame_container = tk.Frame(self.tab_analytics, bg="#1e293b")
        self.chart_frame_container.pack(fill="both", expand=True)
        self.setup_analytics_tab_content()

    def setup_analytics_tab_content(self):
        for w in self.chart_frame_container.winfo_children():
            w.destroy()

        kpi_frame = tk.Frame(self.chart_frame_container, bg="#1e293b")
        kpi_frame.pack(fill="x", padx=10, pady=10)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status!='Completed'")
            open_tickets = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM bills WHERE status='Unpaid'")
            unpaid_bills = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM bookings")
            total_bookings = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

        self.card(kpi_frame, "Open Tickets", str(open_tickets), "#ef4444").pack(side="left", expand=True, padx=5)
        self.card(kpi_frame, "Unpaid Statements", str(unpaid_bills), "#f59e0b").pack(side="left", expand=True, padx=5)
        self.card(kpi_frame, "Total Bookings", str(total_bookings), "#0284c7").pack(side="left", expand=True, padx=5)
        self.card(kpi_frame, "Active Users", str(total_users), "#8b5cf6").pack(side="left", expand=True, padx=5)

        chart_frame = tk.LabelFrame(self.chart_frame_container, text="Real-Time Maintenance Issue Category Breakdown", bg="#1e293b", fg="#38bdf8", font=("Segoe UI", 11, "bold"))
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(chart_frame, bg="#0f172a", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=10, pady=10)

        canvas.create_text(250, 20, text="System Issue Distribution (Dynamic Query)", fill="white", font=("Segoe UI", 11, "bold"))
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category, COUNT(*) FROM tickets GROUP BY category")
            categories = dict(cursor.fetchall())

        if not categories:
            canvas.create_text(250, 110, text="No active service requests recorded.", fill="#94a3b8", font=("Segoe UI", 10))
        else:
            x = 60
            colors = ["#ef4444", "#f59e0b", "#3b82f6", "#10b981", "#8b5cf6", "#ec4899"]
            for idx, (cat, val) in enumerate(categories.items()):
                h = max(val * 30, 8)
                canvas.create_rectangle(x, 210 - h, x + 55, 210, fill=colors[idx % len(colors)])
                canvas.create_text(x + 27, 225, text=cat, fill="white", font=("Segoe UI", 9))
                canvas.create_text(x + 27, 195 - h, text=str(val), fill="white", font=("Segoe UI", 9, "bold"))
                x += 95

    def card(self, parent, title, val, bg):
        f = tk.Frame(parent, bg=bg, padx=15, pady=12)
        tk.Label(f, text=title, font=("Segoe UI", 10, "bold"), bg=bg, fg="white").pack()
        tk.Label(f, text=val, font=("Segoe UI", 18, "bold"), bg=bg, fg="white").pack()
        return f

    def setup_all_tickets_tab(self):
        top_bar = tk.Frame(self.tab_all_tickets, bg="#1e293b")
        top_bar.pack(fill="x", padx=10, pady=10)

        tk.Button(top_bar, text="👨‍🔧 Reassign Technician", bg="#0284c7", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", padx=10, command=self.reassign_ticket).pack(side="left", padx=(0, 10), ipady=4)
        tk.Button(top_bar, text="🗑️ Delete Ticket", bg="#ef4444", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", padx=10, command=self.delete_ticket).pack(side="left", ipady=4)

        tree_frame = tk.Frame(self.tab_all_tickets, bg="#1e293b")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tickets_tree = ttk.Treeview(tree_frame, columns=("ID", "Resident", "Title", "Category", "Priority", "Status", "Tech"), show="headings")
        self.tickets_tree.heading("ID", text="ID")
        self.tickets_tree.heading("Resident", text="Resident")
        self.tickets_tree.heading("Title", text="Title")
        self.tickets_tree.heading("Category", text="Category")
        self.tickets_tree.heading("Priority", text="Priority")
        self.tickets_tree.heading("Status", text="Status")
        self.tickets_tree.heading("Tech", text="Assigned Tech")

        self.tickets_tree.column("ID", width=50, anchor="center")
        self.tickets_tree.column("Resident", width=110, anchor="center")
        self.tickets_tree.column("Title", width=180, anchor="w")
        self.tickets_tree.column("Category", width=110, anchor="center")
        self.tickets_tree.column("Priority", width=140, anchor="center")
        self.tickets_tree.column("Status", width=110, anchor="center")
        self.tickets_tree.column("Tech", width=110, anchor="center")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tickets_tree.yview)
        self.tickets_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tickets_tree.pack(fill="both", expand=True)

        self.refresh_all_tickets_table()

    def refresh_all_tickets_table(self):
        for item in self.tickets_tree.get_children():
            self.tickets_tree.delete(item)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, resident_username, title, category, priority, status, assigned_tech FROM tickets ORDER BY id DESC")
            for r in cursor.fetchall():
                self.tickets_tree.insert("", "end", values=r)

    def reassign_ticket(self):
        sel = self.tickets_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a ticket from the table.")
            return

        tid = self.tickets_tree.item(sel, "values")[0]
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE role='Technician'")
            techs = [r[0] for r in cursor.fetchall()]

        if not techs:
            messagebox.showwarning("No Techs", "No technician accounts exist in the system!")
            return

        win = tk.Toplevel(self)
        win.title("Reassign Ticket")
        win.geometry("320x200")
        win.configure(bg="#1e293b")
        win.grab_set()

        tk.Label(win, text=f"Reassign Ticket #{tid}", font=("Segoe UI", 12, "bold"), bg="#1e293b", fg="#38bdf8").pack(pady=15)
        combo = ttk.Combobox(win, values=techs, width=22)
        combo.current(0)
        combo.pack(pady=10)

        def save():
            new_tech = combo.get()
            with self.db.get_connection() as conn:
                conn.cursor().execute("UPDATE tickets SET assigned_tech=?, status='In Progress' WHERE id=?", (new_tech, tid))
                conn.commit()
            messagebox.showinfo("Assigned", f"Ticket #{tid} assigned to {new_tech}!")
            win.destroy()
            self.refresh_all_tickets_table()

        tk.Button(win, text="Confirm Assignment", bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=save).pack(pady=10, ipady=4)

    def delete_ticket(self):
        sel = self.tickets_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a ticket to delete.")
            return

        tid = self.tickets_tree.item(sel, "values")[0]
        if messagebox.askyesno("Confirm Delete", f"Delete Service Ticket #{tid}?"):
            with self.db.get_connection() as conn:
                conn.cursor().execute("DELETE FROM tickets WHERE id=?", (tid,))
                conn.commit()
            messagebox.showinfo("Deleted", "Ticket removed.")
            self.refresh_all_tickets_table()

    def setup_users_tab(self):
        top_bar = tk.Frame(self.tab_users, bg="#1e293b")
        top_bar.pack(fill="x", padx=10, pady=10)

        tk.Button(top_bar, text="+ Create Account (Admin / Resident / Tech)", bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", padx=10, command=self.add_user_dialog).pack(side="left", padx=(0, 10), ipady=4)
        tk.Button(top_bar, text="🗑️ Delete Selected Account", bg="#ef4444", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", padx=10, command=self.delete_user).pack(side="left", ipady=4)

        tree_frame = tk.Frame(self.tab_users, bg="#1e293b")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.users_tree = ttk.Treeview(tree_frame, columns=("Username", "Role", "Name", "Unit"), show="headings")
        self.users_tree.heading("Username", text="Username")
        self.users_tree.heading("Role", text="Role")
        self.users_tree.heading("Name", text="Full Name")
        self.users_tree.heading("Unit", text="Unit / Office")
        
        self.users_tree.column("Username", width=140, anchor="center")
        self.users_tree.column("Role", width=120, anchor="center")
        self.users_tree.column("Name", width=200, anchor="w")
        self.users_tree.column("Unit", width=180, anchor="w")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        self.users_tree.pack(fill="both", expand=True)
        self.refresh_users_table()

    def refresh_users_table(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, role, name, unit FROM users")
            for r in cursor.fetchall():
                self.users_tree.insert("", "end", values=r)

    def add_user_dialog(self):
        win = tk.Toplevel(self)
        win.title("Create User Account")
        win.geometry("380x430")
        win.configure(bg="#1e293b")
        win.grab_set()

        tk.Label(win, text="➕ Create Account", font=("Segoe UI", 16, "bold"), bg="#1e293b", fg="#38bdf8").pack(pady=15)

        tk.Label(win, text="Username:", font=("Segoe UI", 9, "bold"), bg="#1e293b", fg="#cbd5e1", anchor="w").pack(fill="x", padx=30)
        u_entry = tk.Entry(win, bg="#334155", fg="white", bd=0)
        u_entry.pack(fill="x", padx=30, pady=(0, 8), ipady=4)

        tk.Label(win, text="Password:", font=("Segoe UI", 9, "bold"), bg="#1e293b", fg="#cbd5e1", anchor="w").pack(fill="x", padx=30)
        p_entry = tk.Entry(win, show="*", bg="#334155", fg="white", bd=0)
        p_entry.pack(fill="x", padx=30, pady=(0, 8), ipady=4)

        tk.Label(win, text="Role:", font=("Segoe UI", 9, "bold"), bg="#1e293b", fg="#cbd5e1", anchor="w").pack(fill="x", padx=30)
        r_combo = ttk.Combobox(win, values=["Admin", "Resident", "Technician"])
        r_combo.current(1)
        r_combo.pack(fill="x", padx=30, pady=(0, 8))

        tk.Label(win, text="Full Name:", font=("Segoe UI", 9, "bold"), bg="#1e293b", fg="#cbd5e1", anchor="w").pack(fill="x", padx=30)
        n_entry = tk.Entry(win, bg="#334155", fg="white", bd=0)
        n_entry.pack(fill="x", padx=30, pady=(0, 8), ipady=4)

        tk.Label(win, text="Unit / Office Location:", font=("Segoe UI", 9, "bold"), bg="#1e293b", fg="#cbd5e1", anchor="w").pack(fill="x", padx=30)
        unit_entry = tk.Entry(win, bg="#334155", fg="white", bd=0)
        unit_entry.pack(fill="x", padx=30, pady=(0, 15), ipady=4)

        def create():
            u, p, r, n, unit = u_entry.get().strip(), p_entry.get().strip(), r_combo.get(), n_entry.get().strip(), unit_entry.get().strip()
            if not u or not p or not n or not unit:
                messagebox.showwarning("Warning", "All fields are required!", parent=win)
                return

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users WHERE username=?", (u,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Username already exists!", parent=win)
                    return
                cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (u, p, r, n, unit))
                conn.commit()

            messagebox.showinfo("Success", f"Created {r} account '{u}'!", parent=win)
            win.destroy()
            self.refresh_all_data()

        tk.Button(win, text="Create Account", bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=create).pack(fill="x", padx=30, ipady=5)

    def delete_user(self):
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Needed", "Please select a user account to delete from the table.")
            return

        values = self.users_tree.item(selected_item, "values")
        target_username = values[0]

        if target_username == self.app.current_user["username"]:
            messagebox.showerror("Security Denied", "You cannot delete your own logged-in admin account!")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete user '{target_username}'?")
        if confirm:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username=?", (target_username,))
                cursor.execute("UPDATE tickets SET assigned_tech='Unassigned', status='Pending' WHERE assigned_tech=? AND status!='Completed'", (target_username,))
                conn.commit()

            messagebox.showinfo("Deleted", f"User '{target_username}' deleted.")
            self.refresh_all_data()

    def setup_techs_tab(self):
        tree_frame = tk.Frame(self.tab_techs, bg="#1e293b")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tech_tree = ttk.Treeview(tree_frame, columns=("Username", "Name", "AssignedTickets", "CompletedTickets"), show="headings")
        self.tech_tree.heading("Username", text="Tech Username")
        self.tech_tree.heading("Name", text="Full Name")
        self.tech_tree.heading("AssignedTickets", text="In-Progress / Pending")
        self.tech_tree.heading("CompletedTickets", text="Completed Work Orders")

        self.tech_tree.column("Username", width=150, anchor="center")
        self.tech_tree.column("Name", width=200, anchor="w")
        self.tech_tree.column("AssignedTickets", width=160, anchor="center")
        self.tech_tree.column("CompletedTickets", width=160, anchor="center")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tech_tree.yview)
        self.tech_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        self.tech_tree.pack(fill="both", expand=True)
        self.refresh_techs_table()

    def refresh_techs_table(self):
        for item in self.tech_tree.get_children():
            self.tech_tree.delete(item)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, name FROM users WHERE role='Technician'")
            techs = cursor.fetchall()

            for t_user, t_name in techs:
                cursor.execute("SELECT COUNT(*) FROM tickets WHERE assigned_tech=? AND status!='Completed'", (t_user,))
                active_cnt = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM tickets WHERE assigned_tech=? AND status='Completed'", (t_user,))
                completed_cnt = cursor.fetchone()[0]

                self.tech_tree.insert("", "end", values=(t_user, t_name, active_cnt, completed_cnt))

    def setup_bookings_tab(self):
        top_bar = tk.Frame(self.tab_bookings, bg="#1e293b")
        top_bar.pack(fill="x", padx=10, pady=10)

        tk.Button(top_bar, text="🗑️ Cancel Selected Reservation", bg="#ef4444", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", padx=10, command=self.delete_booking).pack(side="left", ipady=4)

        tree_frame = tk.Frame(self.tab_bookings, bg="#1e293b")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.booking_tree = ttk.Treeview(tree_frame, columns=("ID", "Resident", "Facility", "Date", "Slot", "BookedAt"), show="headings")
        self.booking_tree.heading("ID", text="ID")
        self.booking_tree.heading("Resident", text="Resident Username")
        self.booking_tree.heading("Facility", text="Facility Name")
        self.booking_tree.heading("Date", text="Booking Date")
        self.booking_tree.heading("Slot", text="Time Slot")
        self.booking_tree.heading("BookedAt", text="Timestamp")

        self.booking_tree.column("ID", width=60, anchor="center")
        self.booking_tree.column("Resident", width=140, anchor="center")
        self.booking_tree.column("Facility", width=180, anchor="w")
        self.booking_tree.column("Date", width=120, anchor="center")
        self.booking_tree.column("Slot", width=140, anchor="center")
        self.booking_tree.column("BookedAt", width=140, anchor="center")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.booking_tree.yview)
        self.booking_tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        self.booking_tree.pack(fill="both", expand=True)
        self.refresh_bookings_table()

    def refresh_bookings_table(self):
        for item in self.booking_tree.get_children():
            self.booking_tree.delete(item)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, resident_username, facility, date, slot, created_at FROM bookings ORDER BY id DESC")
            for r in cursor.fetchall():
                self.booking_tree.insert("", "end", values=r)

    def delete_booking(self):
        sel = self.booking_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a booking entry to cancel.")
            return

        booking_id = self.booking_tree.item(sel, "values")[0]
        if messagebox.askyesno("Confirm Cancel", f"Cancel booking ID #{booking_id}?"):
            with self.db.get_connection() as conn:
                conn.cursor().execute("DELETE FROM bookings WHERE id=?", (booking_id,))
                conn.commit()
            messagebox.showinfo("Cancelled", "Booking has been removed.")
            self.refresh_bookings_table()

    def setup_announcements_tab(self):
        form = tk.LabelFrame(self.tab_announcements, text="Publish Building Broadcast Notice", bg="#1e293b", fg="#38bdf8", font=("Segoe UI", 11, "bold"), padx=15, pady=15)
        form.pack(fill="x", padx=10, pady=10)

        tk.Label(form, text="Notice Title:", bg="#1e293b", fg="#cbd5e1").pack(anchor="w")
        self.ann_title = tk.Entry(form, width=60, bg="#334155", fg="white", bd=0)
        self.ann_title.pack(fill="x", pady=(0, 8), ipady=4)

        tk.Label(form, text="Notice Content:", bg="#1e293b", fg="#cbd5e1").pack(anchor="w")
        self.ann_content = tk.Text(form, height=3, width=60, bg="#334155", fg="white", bd=0)
        self.ann_content.pack(fill="x", pady=(0, 8))

        btn_box = tk.Frame(form, bg="#1e293b")
        btn_box.pack(fill="x")

        tk.Button(btn_box, text="📢 Broadcast Notice", bg="#8b5cf6", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.publish_announcement).pack(side="left", ipady=4, padx=(0, 10))
        tk.Button(btn_box, text="🗑️ Delete Selected Notice", bg="#ef4444", fg="white", font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", command=self.delete_announcement).pack(side="left", ipady=4)

        list_frame = tk.LabelFrame(self.tab_announcements, text="Published Announcements History", bg="#1e293b", fg="#38bdf8", font=("Segoe UI", 11, "bold"), padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.ann_listbox = tk.Listbox(list_frame, bg="#0f172a", fg="#f8fafc", font=("Consolas", 10), bd=0, selectbackground="#0284c7")
        self.ann_listbox.pack(fill="both", expand=True)

        self.refresh_announcements()

    def publish_announcement(self):
        t = self.ann_title.get().strip()
        c = self.ann_content.get("1.0", "end").strip()

        if not t or not c:
            messagebox.showwarning("Warning", "Notice title and content are required!")
            return

        today = datetime.date.today().strftime("%Y-%m-%d")
        with self.db.get_connection() as conn:
            conn.cursor().execute("INSERT INTO announcements (title, content, date_posted) VALUES (?, ?, ?)", (t, c, today))
            conn.commit()

        messagebox.showinfo("Broadcast Sent", "Notice broadcasted to all residents!")
        self.ann_title.delete(0, 'end')
        self.ann_content.delete("1.0", "end")
        self.refresh_announcements()

    def refresh_announcements(self):
        self.ann_listbox.delete(0, 'end')
        self.ann_ids = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, date_posted FROM announcements ORDER BY id DESC")
            for r in cursor.fetchall():
                self.ann_ids.append(r[0])
                self.ann_listbox.insert('end', f" #{r[0]}  |  Title: {r[1]}  (Date Posted: {r[2]})")

    def delete_announcement(self):
        sel = self.ann_listbox.curselection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a notice from the list to delete.")
            return

        ann_id = self.ann_ids[sel[0]]
        if messagebox.askyesno("Confirm Delete", f"Delete Notice #{ann_id}?"):
            with self.db.get_connection() as conn:
                conn.cursor().execute("DELETE FROM announcements WHERE id=?", (ann_id,))
                conn.commit()
            messagebox.showinfo("Deleted", "Notice removed.")
            self.refresh_announcements()

# 6. Main Program Entry Point
if __name__ == "__main__":
    app = CondoCareApp()
    app.mainloop()