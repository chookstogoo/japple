import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter import ttk
import os
from PIL import Image, ImageTk

from barcode_scanner import scan_and_fetch_book
from virtual_barcode import generate_local_barcode, scan_screen_for_barcode
from models.biology_book import BiologyBook
from models.chemistry_book import ChemistryBook
from models.engineering_book import EngineeringBook
from models.history_book import HistoryBook
from models.mathematics_book import MathematicsBook
from models.member import Member
from models.physics_book import PhysicsBook
from services.library import Library

BOOK_TYPES = {
    "Biology": BiologyBook,
    "Chemistry": ChemistryBook,
    "Engineering": EngineeringBook,
    "History": HistoryBook,
    "Mathematics": MathematicsBook,
    "Physics": PhysicsBook,
}


class LibraryApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.library = Library("City Library")

        self.status_var = tk.StringVar(value="Welcome to the Library System.")
        self.current_user = None
        self.current_role = None

        self.colors = {
            "sidebar": "#1e293b",
            "main_bg": "#f1f5f9",
            "white": "#ffffff",
            "text_dark": "#0f172a",
            "text_light": "#64748b",
            "card_blue": "#3b82f6",
            "card_green": "#22c55e",
            "card_orange": "#f59e0b",
            "card_purple": "#a855f7",
            "card_indigo": "#6366f1",
            "card_red": "#ef4444",
        }
        self.root.configure(bg=self.colors["main_bg"])

        self._build_login_screen()

    def on_closing(self):
        self.root.destroy()
        os._exit(0)

    def _build_login_screen(self):
        self.login_container = tk.Frame(self.root, bg=self.colors["main_bg"])
        self.login_container.pack(fill="both", expand=True)

        signup_frame = tk.Frame(self.login_container, bg="#e2e8f0")
        signup_frame.pack(side="left", fill="both", expand=True)

        signin_frame = tk.Frame(self.login_container, bg="white")
        signin_frame.pack(side="right", fill="both", expand=True)

        tk.Label(signup_frame, text="Create Account", font=("Segoe UI", 28, "bold"), bg="#e2e8f0",
                 fg=self.colors['text_dark']).pack(pady=(180, 30))

        tk.Label(signup_frame, text="Username", bg="#e2e8f0", font=("Segoe UI", 12)).pack(pady=(10, 0))
        self.signup_user = tk.StringVar()
        tk.Entry(signup_frame, textvariable=self.signup_user, font=("Segoe UI", 14), width=25).pack(pady=5)

        tk.Label(signup_frame, text="Password (Min 8 chars)", bg="#e2e8f0", font=("Segoe UI", 12)).pack(pady=(10, 0))
        self.signup_pass = tk.StringVar()
        tk.Entry(signup_frame, textvariable=self.signup_pass, font=("Segoe UI", 14), width=25, show="*").pack(pady=5)

        tk.Label(signup_frame, text="Account Role", bg="#e2e8f0", font=("Segoe UI", 12)).pack(pady=(10, 0))
        self.signup_role = tk.StringVar(value="student")
        ttk.Combobox(signup_frame, textvariable=self.signup_role, values=["student", "admin"], state="readonly",
                     font=("Segoe UI", 14), width=23).pack(pady=5)

        tk.Button(signup_frame, text="Sign Up", font=("Segoe UI", 12, "bold"), bg=self.colors['card_green'], fg="white",
                  command=self.handle_signup, width=20, pady=8, cursor="hand2").pack(pady=30)

        tk.Label(signin_frame, text="Welcome Back", font=("Segoe UI", 28, "bold"), bg="white",
                 fg=self.colors['text_dark']).pack(pady=(200, 30))

        tk.Label(signin_frame, text="Username", bg="white", font=("Segoe UI", 12)).pack(pady=(10, 0))
        self.signin_user = tk.StringVar()
        tk.Entry(signin_frame, textvariable=self.signin_user, font=("Segoe UI", 14), width=25).pack(pady=5)

        tk.Label(signin_frame, text="Password", bg="white", font=("Segoe UI", 12)).pack(pady=(10, 0))
        self.signin_pass = tk.StringVar()
        tk.Entry(signin_frame, textvariable=self.signin_pass, font=("Segoe UI", 14), width=25, show="*").pack(pady=5)

        tk.Button(signin_frame, text="Sign In", font=("Segoe UI", 12, "bold"), bg=self.colors['card_blue'], fg="white",
                  command=self.handle_signin, width=20, pady=8, cursor="hand2").pack(pady=30)

    def handle_signup(self):
        user = self.signup_user.get().strip()
        pwd = self.signup_pass.get().strip()
        role = self.signup_role.get().strip()

        if not user or not pwd:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        if len(pwd) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long.")
            return

        success, msg = self.library.register_user(user, pwd, role)
        if success:
            messagebox.showinfo("Success", "Account created! You can now sign in on the right.")
            self.signup_user.set("")
            self.signup_pass.set("")
        else:
            messagebox.showerror("Error", msg)

    def handle_signin(self):
        user = self.signin_user.get().strip()
        pwd = self.signin_pass.get().strip()

        success, role = self.library.authenticate_user(user, pwd)
        if success:
            self.current_user = user
            self.current_role = role
            if role == 'student' and user not in self.library.members:
                self.library.register_member(Member(user, user.capitalize()))
            self.login_container.destroy()
            self.launch_main_app()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def handle_logout(self):
        if messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
            self.current_user = None
            self.current_role = None
            if hasattr(self, 'sidebar'): self.sidebar.destroy()
            if hasattr(self, 'main_frame'): self.main_frame.destroy()
            self._build_login_screen()

    def launch_main_app(self):
        self._init_vars()
        self._build_layout()
        self._build_screens()

        if self.current_role == 'admin':
            self._show_screen("home")
        else:
            self._show_screen("view")

        self.refresh_views()

    def _init_vars(self):
        self.book_type_var = tk.StringVar(value="Biology")
        self.book_id_var = tk.StringVar()
        self.book_title_var = tk.StringVar()
        self.book_year_var = tk.StringVar()
        self.book_author_var = tk.StringVar()
        self.book_pages_var = tk.StringVar()
        self.member_id_var = tk.StringVar()
        self.member_name_var = tk.StringVar()
        self.issue_member_var = tk.StringVar()
        self.issue_book_var = tk.StringVar()
        self.return_member_var = tk.StringVar()
        self.return_book_var = tk.StringVar()
        self.delete_id_var = tk.StringVar()
        self.request_member_var = tk.StringVar()
        self.request_book_var = tk.StringVar()
        self.books = []
        self.members = []
        self.transactions = []

    def _build_layout(self) -> None:
        self.create_sidebar()

        self.main_frame = tk.Frame(self.root, bg=self.colors['main_bg'])
        self.main_frame.pack(side='right', fill='both', expand=True)

        self.create_header(self.main_frame)

        self.content_frame = tk.Frame(self.main_frame, bg=self.colors['main_bg'])
        self.content_frame.pack(fill='both', expand=True)

        self.status_label = tk.Label(self.main_frame, textvariable=self.status_var, anchor="w", bg="#e2e8f0",
                                     fg="#0f172a", padx=12, pady=6, font=("Segoe UI", 9))
        self.status_label.pack(side="bottom", fill="x")

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=self.colors['sidebar'], width=250)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # Pack Bottom Frame FIRST so it securely anchors to the bottom
        bottom_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        bottom_frame.pack(side='bottom', fill='x', pady=20)

        tk.Button(bottom_frame, text="🚪 Log Out", font=('Arial', 10, 'bold'), bg=self.colors['card_red'], fg='white',
                  bd=0, pady=8, cursor='hand2', command=self.handle_logout).pack(fill='x', padx=20, pady=(0, 10))
        tk.Label(bottom_frame, text="Library Management System", font=('Arial', 10), fg='#94a3b8',
                 bg=self.colors['sidebar']).pack(padx=20)
        tk.Label(bottom_frame, text="© 2026 All rights reserved.", font=('Arial', 9), fg='#64748b',
                 bg=self.colors['sidebar']).pack(padx=20, pady=5)

        # Then pack the Logo to the top
        logo_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        logo_frame.pack(side='top', fill='x', pady=20)
        tk.Label(logo_frame, text="📚 LIBRARY MS", font=('Arial', 18, 'bold'), fg='white',
                 bg=self.colors['sidebar']).pack(padx=20)

        # Nav items
        if self.current_role == 'admin':
            nav_items = [
                ("📊 Dashboard", True), ("📖 Books", False), ("👥 Members", False),
                ("🔄 Transactions", False), ("📋 Reports", False), ("⚙️ Settings", False),
                ("🔍 Search", False)
            ]
        else:
            nav_items = [
                ("📖 Books", True), ("🔄 Request Book", False), ("📋 Reports", False)
            ]

        for item, is_active in nav_items:
            bg_color = '#2563eb' if is_active else self.colors['sidebar']
            tk.Button(self.sidebar, text=item, font=('Arial', 11), bg=bg_color, fg='white', bd=0, pady=15, anchor='w',
                      padx=20, cursor='hand2', command=lambda x=item: self.nav_click(x)).pack(side='top', fill='x',
                                                                                              padx=10, pady=2)

        if self.current_role == 'admin':
            quick_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
            quick_frame.pack(side='top', fill='x', pady=20)
            tk.Label(quick_frame, text="QUICK ACTIONS", font=('Arial', 10, 'bold'), fg='#94a3b8',
                     bg=self.colors['sidebar']).pack(padx=20, pady=(0, 10))

            quick_actions = [("➕ Add Book", self.colors['card_green']), ("👤 Add Member", self.colors['card_blue']),
                             ("📊 Generate Report", self.colors['card_orange'])]
            for action, color in quick_actions:
                tk.Button(self.sidebar, text=action, font=('Arial', 10), bg=color, fg='white', bd=0, pady=8,
                          cursor='hand2', command=lambda x=action: self.quick_action(x)).pack(side='top', fill='x',
                                                                                              padx=20, pady=2)

    def nav_click(self, item):
        if "Dashboard" in item:
            self._show_screen("home")
        elif "Books" in item:
            self._show_screen("view")
        elif "Members" in item:
            self._show_screen("member")
        elif "Transactions" in item:
            self._show_screen("issue")
        elif "Request Book" in item:
            self._show_screen("request")
        elif "Reports" in item:
            self._show_screen("report")
        elif "Settings" in item:
            self._show_screen("settings")
        elif "Search" in item:
            self.trigger_screen_scanner()
        else:
            messagebox.showinfo("Navigation", f"Module '{item}' is under construction.")

    def trigger_screen_scanner(self):
        self.status_var.set("Scanning screen for barcodes...")
        self.root.update()
        scanned_id = scan_screen_for_barcode()

        if scanned_id:
            book = self.library.items.get(scanned_id)
            if book:
                info = (
                    f"📖 Book Identified!\n\nTitle: {book.title}\nAuthor: {getattr(book, 'author', 'Unknown')}\nStatus: {'Borrowed' if book.is_borrowed else 'Available'}\n\n(Virtual ID: {scanned_id})")
                messagebox.showinfo("Scanner Result", info)
                self.status_var.set(f"Successfully identified {book.title} from screen.")
            else:
                messagebox.showwarning("Scanner Result", f"Scanned ID '{scanned_id}' not found in the local database.")
                self.status_var.set("Scanned unknown barcode.")
        else:
            messagebox.showerror("Scanner Result",
                                 "No barcode detected on your screen. Make sure a barcode window is open and visible.")
            self.status_var.set("Screenshot scan failed.")

    def quick_action(self, action):
        if "Add Book" in action:
            self._show_screen("add")
        elif "Add Member" in action:
            self._show_screen("member")
        elif "Generate Report" in action:
            self._show_screen("report")
        else:
            messagebox.showinfo("Quick Action", f"Action '{action}' triggered.")

    def create_header(self, parent):
        header = tk.Frame(parent, bg=self.colors['white'], height=80)
        header.pack(fill='x', padx=20, pady=20)
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=self.colors['white'])
        title_frame.pack(side='left', padx=20, pady=20)

        tk.Label(title_frame, text="📊 Library Dashboard", font=('Arial', 24, 'bold'), fg=self.colors['text_dark'],
                 bg=self.colors['white']).pack(anchor='w')
        tk.Label(title_frame, text=f"Welcome back! Today is {datetime.now().strftime('%B %d, %Y')}", font=('Arial', 11),
                 fg=self.colors['text_light'], bg=self.colors['white']).pack(anchor='w')

        right_frame = tk.Frame(header, bg=self.colors['white'])
        right_frame.pack(side='right', padx=20, pady=20)

        search_frame = tk.Frame(right_frame, bg='#f3f4f6', relief='flat', bd=1)
        search_frame.pack(side='left', padx=10)

        self.search_entry = tk.Entry(search_frame, font=('Arial', 10), bg='#f3f4f6', bd=0, width=25,
                                     fg=self.colors['text_light'])
        self.search_entry.pack(side='left', padx=10, pady=8)
        self.search_entry.insert(0, "Search books, members...")

        # Clear placeholder text safely
        def on_focus_in(e):
            if self.search_entry.get() == "Search books, members...":
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(fg=self.colors['text_dark'])

        def on_focus_out(e):
            if not self.search_entry.get().strip():
                self.search_entry.insert(0, "Search books, members...")
                self.search_entry.config(fg=self.colors['text_light'])

        self.search_entry.bind('<FocusIn>', on_focus_in)
        self.search_entry.bind('<FocusOut>', on_focus_out)

        tk.Button(search_frame, text="🔍", font=('Arial', 12), bg='#f3f4f6', bd=0, cursor='hand2').pack(side='right',
                                                                                                       padx=5)

        user_frame = tk.Frame(right_frame, bg=self.colors['white'])
        user_frame.pack(side='left', padx=10)

        tk.Button(user_frame, text="👤", font=('Arial', 16), bg=self.colors['card_blue'], fg='white', width=3, height=1,
                  bd=0, cursor='hand2').pack(side='left')

        user_info = tk.Frame(user_frame, bg=self.colors['white'])
        user_info.pack(side='left', padx=10)

        tk.Label(user_info, text=f"Hi, {self.current_user}", font=('Arial', 12, 'bold'), fg=self.colors['text_dark'],
                 bg=self.colors['white']).pack(anchor='w')
        tk.Label(user_info, text=f"Role: {self.current_role.capitalize()}", font=('Arial', 9),
                 fg=self.colors['text_light'], bg=self.colors['white']).pack(anchor='w')

    def _build_screens(self) -> None:
        self.screens: dict[str, tk.Frame] = {
            "home": self._build_home_screen(),
            "add": self._build_add_book_screen(),
            "view": self._build_view_books_screen(),
            "delete": self._build_delete_book_screen(),
            "issue": self._build_issue_book_screen(),
            "return": self._build_return_book_screen(),
            "request": self._build_request_book_screen(),
            "member": self._build_member_screen(),
            "report": self._build_report_screen(),
            "settings": self._build_settings_screen(),
        }
        for screen in self.screens.values():
            screen.pack_forget()

    def _show_screen(self, key: str) -> None:
        for frame in self.screens.values():
            frame.pack_forget()
        self.screens[key].pack(fill="both", expand=True)
        self.refresh_views()

    def _make_panel(self, title: str) -> tk.Frame:
        panel = tk.Frame(self.content_frame, bg="white", bd=1, relief="solid")
        tk.Label(panel, text=title, bg="white", fg="#1b2b3a", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16,
                                                                                                  pady=(14, 10))
        return panel

    def _build_home_screen(self) -> tk.Frame:
        panel = tk.Frame(self.content_frame, bg=self.colors["main_bg"])
        self.render_dashboard(panel)
        return panel

    def render_dashboard(self, parent: tk.Frame):
        for widget in parent.winfo_children():
            widget.destroy()

        # Fix layout overflowing: Lock top and bottom row heights, expand middle.
        top_row = tk.Frame(parent, bg=self.colors['main_bg'])
        top_row.pack(side='top', fill='x', padx=20, pady=(10, 5))

        bot_row = tk.Frame(parent, bg=self.colors['main_bg'])
        bot_row.pack(side='bottom', fill='x', padx=20, pady=(5, 20))

        mid_row = tk.Frame(parent, bg=self.colors['main_bg'])
        mid_row.pack(side='top', fill='both', expand=True, padx=20, pady=5)

        self.create_metric_cards(top_row)
        self.create_bottom_section(bot_row)
        self.create_middle_section(mid_row)

    def create_metric_cards(self, parent: tk.Frame):
        total_books = len(self.library.items)
        borrowed_books = sum(1 for b in self.library.items.values() if b.is_borrowed)
        available_books = total_books - borrowed_books
        overdue_books = len([t for t in self.transactions if t['status'] == 'Overdue'])

        cards_data = [
            (f"{total_books:,}", "Total Books", self.colors['card_blue'], "📚"),
            (f"{available_books:,}", "Available Books", self.colors['card_green'], "✅"),
            (f"{borrowed_books:,}", "Books Borrowed", self.colors['card_orange'], "📖"),
            (f"{overdue_books:,}", "Overdue Books", self.colors['card_red'], "⚠️")
        ]

        for col, (value, label, color, icon) in enumerate(cards_data):
            parent.grid_columnconfigure(col, weight=1)
            card = tk.Frame(parent, bg=color)
            card.grid(row=0, column=col, padx=10, sticky='nsew')

            tk.Label(card, text=icon, font=('Arial', 20), fg='white', bg=color).pack(pady=(10, 2))
            tk.Label(card, text=value, font=('Arial', 22, 'bold'), fg='white', bg=color).pack()
            tk.Label(card, text=label, font=('Arial', 10), fg='white', bg=color).pack(pady=(0, 5))

        parent.grid_rowconfigure(0, weight=1)

    def create_middle_section(self, parent: tk.Frame):
        left_frame = tk.Frame(parent, bg=self.colors['white'], relief='flat', bd=1)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        trans_header = tk.Frame(left_frame, bg=self.colors['white'])
        trans_header.pack(fill='x', padx=20, pady=(15, 5))
        tk.Label(trans_header, text="Recent Transactions", font=('Arial', 14, 'bold'), fg=self.colors['text_dark'],
                 bg=self.colors['white']).pack(side='left')

        self.create_transactions_list(left_frame)

        right_frame = tk.Frame(parent, bg=self.colors['white'], relief='flat', bd=1)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))

        cat_header = tk.Frame(right_frame, bg=self.colors['white'])
        cat_header.pack(fill='x', padx=20, pady=(15, 5))
        tk.Label(cat_header, text="Book Categories", font=('Arial', 14, 'bold'), fg=self.colors['text_dark'],
                 bg=self.colors['white']).pack()

        self.create_category_chart(right_frame)

    def approve_req(self, t_id):
        if messagebox.askyesno("Approve", "Approve this request and issue the book?"):
            ok, msg = self.library.admin_approve_request(t_id)
            if ok:
                messagebox.showinfo("Success", msg)
            else:
                messagebox.showerror("Error", msg)
            self.refresh_views()

    def reject_req(self, t_id):
        if messagebox.askyesno("Reject", "Reject this student request?"):
            self.library.admin_reject_request(t_id)
            self.refresh_views()

    def create_transactions_list(self, parent: tk.Frame):
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_manager() == 'pack' and widget.winfo_y() > 30:
                widget.destroy()

        status_colors = {
            'Completed': self.colors['card_green'],
            'Done': self.colors['card_green'],
            'Approved': self.colors['card_green'],
            'Active': self.colors['card_blue'],
            'Pending': self.colors['card_orange'],
            'Overdue': self.colors['card_red'],
            'Rejected': self.colors['card_red']
        }
        type_icons = {'Borrow': '📖', 'Return': '📚', 'Request': '🔖', 'Renew': '🔄'}

        if not self.transactions:
            tk.Label(parent, text="No recent transactions.", bg=self.colors['white'], fg=self.colors['text_light'],
                     pady=20).pack()
            return

        for transaction in self.transactions[:4]:
            trans_row = tk.Frame(parent, bg=self.colors['white'])
            trans_row.pack(fill='x', padx=20, pady=5)

            icon_color = status_colors.get(transaction['status'], self.colors['card_blue'])
            icon_frame = tk.Frame(trans_row, bg=icon_color, width=35, height=35)
            icon_frame.pack(side='left', padx=(0, 15))
            icon_frame.pack_propagate(False)

            icon_text = type_icons.get(transaction['type'], '📄')
            tk.Label(icon_frame, text=icon_text, font=('Arial', 10), fg='white', bg=icon_color).place(relx=0.5,
                                                                                                      rely=0.5,
                                                                                                      anchor='center')

            details_frame = tk.Frame(trans_row, bg=self.colors['white'])
            details_frame.pack(side='left', fill='x', expand=True)
            tk.Label(details_frame, text=f"{transaction['member']} - {transaction['book']}", font=('Arial', 10, 'bold'),
                     fg=self.colors['text_dark'], bg=self.colors['white']).pack(anchor='w')
            tk.Label(details_frame, text=f"{transaction['type']} • {transaction['date']}", font=('Arial', 8),
                     fg=self.colors['text_light'], bg=self.colors['white']).pack(anchor='w')

            right_details = tk.Frame(trans_row, bg=self.colors['white'])
            right_details.pack(side='right')

            if self.current_role == 'admin' and transaction['status'] == 'Pending':
                tk.Button(right_details, text="✅", bg=self.colors['card_green'], fg='white', relief='flat',
                          font=('Arial', 8), cursor="hand2",
                          command=lambda t=transaction['id']: self.approve_req(t)).pack(side='left', padx=2)
                tk.Button(right_details, text="❌", bg=self.colors['card_red'], fg='white', relief='flat',
                          font=('Arial', 8), cursor="hand2",
                          command=lambda t=transaction['id']: self.reject_req(t)).pack(side='left', padx=2)

            status_bg = status_colors.get(transaction['status'], self.colors['card_blue'])
            tk.Label(right_details, text=transaction['status'], font=('Arial', 8, 'bold'), fg='white', bg=status_bg,
                     padx=6, pady=2).pack(side='left', padx=5)

    def create_category_chart(self, parent: tk.Frame):
        chart_frame = tk.Frame(parent, bg=self.colors['white'])
        chart_frame.pack(fill='both', expand=True, padx=20, pady=10)

        categories = {}
        for book in self.library.items.values():
            ctype = book.get_item_type()
            categories[ctype] = categories.get(ctype, 0) + 1

        if not categories: categories = {'None': 1}

        canvas = tk.Canvas(chart_frame, bg=self.colors['white'], highlightthickness=0)
        canvas.pack(fill='both', expand=True)

        colors = [self.colors['card_blue'], self.colors['card_green'], self.colors['card_orange'],
                  self.colors['card_purple'], self.colors['card_red'], self.colors['card_indigo']]

        max_value = max(categories.values()) if categories else 1
        bar_height = 20
        spacing = 25
        start_y = 10

        for i, (category, count) in enumerate(categories.items()):
            y = start_y + i * spacing
            bar_width = int((count / max_value) * 150)
            color = colors[i % len(colors)]

            canvas.create_rectangle(80, y, 80 + bar_width, y + bar_height, fill=color, outline="")
            canvas.create_text(75, y + bar_height // 2, text=category, font=('Arial', 10), anchor='e',
                               fill=self.colors['text_dark'])
            canvas.create_text(85 + bar_width, y + bar_height // 2, text=str(count), font=('Arial', 9), anchor='w',
                               fill=self.colors['text_light'])

    def create_bottom_section(self, parent: tk.Frame):
        members_frame = tk.Frame(parent, bg=self.colors['white'])
        members_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        tk.Label(members_frame, text="Top Active Members", font=('Arial', 14, 'bold'), fg=self.colors['text_dark'],
                 bg=self.colors['white']).pack(anchor='w', padx=20, pady=(15, 5))

        all_members = list(self.library.members.values())
        all_members.sort(key=lambda m: len(m.borrowed_item_ids), reverse=True)
        colors = [self.colors['card_green'], self.colors['card_blue'], self.colors['card_orange'],
                  self.colors['card_purple']]

        if not all_members:
            tk.Label(members_frame, text="No members yet.", bg="white").pack(pady=10)
        else:
            for i, member in enumerate(all_members[:3]):
                color = colors[i % len(colors)]
                member_row = tk.Frame(members_frame, bg=self.colors['white'])
                member_row.pack(fill='x', padx=20, pady=2)

                avatar = tk.Frame(member_row, bg=color, width=30, height=30)
                avatar.pack(side='left', padx=(0, 10))
                avatar.pack_propagate(False)
                tk.Label(avatar, text=member.name[0].upper(), font=('Arial', 10, 'bold'), fg='white', bg=color).place(
                    relx=0.5, rely=0.5, anchor='center')

                info_frame = tk.Frame(member_row, bg=self.colors['white'])
                info_frame.pack(side='left', fill='x', expand=True)
                tk.Label(info_frame, text=member.name, font=('Arial', 10, 'bold'), fg=self.colors['text_dark'],
                         bg=self.colors['white']).pack(anchor='w')
                tk.Label(info_frame, text=f"{member.member_id} • {len(member.borrowed_item_ids)} books",
                         font=('Arial', 8), fg=self.colors['text_light'], bg=self.colors['white']).pack(anchor='w')

        stats_frame = tk.Frame(parent, bg=self.colors['white'])
        stats_frame.pack(side='left', fill='both', expand=True, padx=10)

        tk.Label(stats_frame, text="Library Statistics", font=('Arial', 14, 'bold'), fg=self.colors['text_dark'],
                 bg=self.colors['white']).pack(anchor='w', padx=20, pady=(15, 5))
        tk.Label(stats_frame, text="Monthly Circulation", font=('Arial', 10), fg=self.colors['text_light'],
                 bg=self.colors['white']).pack(anchor='w', padx=20)
        tk.Label(stats_frame, text="0 books", font=('Arial', 18, 'bold'), fg=self.colors['text_dark'],
                 bg=self.colors['white']).pack(anchor='w', padx=20, pady=(0, 5))

        stats_row = tk.Frame(stats_frame, bg=self.colors['white'])
        stats_row.pack(fill='x', padx=20, pady=5)

        month_stat = tk.Frame(stats_row, bg=self.colors['card_green'], width=100, height=45)
        month_stat.pack(side='left', padx=(0, 10))
        month_stat.pack_propagate(False)
        tk.Label(month_stat, text="This Month", font=('Arial', 8, 'bold'), fg='white',
                 bg=self.colors['card_green']).pack(pady=(4, 0))
        tk.Label(month_stat, text="0 books", font=('Arial', 10, 'bold'), fg='white',
                 bg=self.colors['card_green']).pack()

        tk.Label(stats_row, text="Returns\n0 books", font=('Arial', 10), fg=self.colors['text_dark'],
                 bg=self.colors['white']).pack(side='left', padx=15)

    def _build_settings_screen(self) -> tk.Frame:
        panel = self._make_panel("⚙️ Settings & Database Management")

        wrap = tk.Frame(panel, bg="white")
        wrap.pack(anchor="w", padx=16, pady=12)
        tk.Label(wrap, text="Library Catalog Controls", bg="white", font=("Segoe UI", 12, "bold")).pack(anchor="w",
                                                                                                        pady=(0, 15))
        tk.Button(wrap, text="➕ Add New Book", command=lambda: self._show_screen("add"), bg=self.colors['card_green'],
                  fg="white", relief="flat", padx=20, pady=10, font=("Segoe UI", 10, "bold"), width=25,
                  cursor="hand2").pack(anchor="w", pady=8)
        tk.Button(wrap, text="🗑️ Delete Book", command=lambda: self._show_screen("delete"), bg=self.colors['card_red'],
                  fg="white", relief="flat", padx=20, pady=10, font=("Segoe UI", 10, "bold"), width=25,
                  cursor="hand2").pack(anchor="w", pady=8)
        return panel

    def _build_add_book_screen(self) -> tk.Frame:
        panel = self._make_panel("Add Book")
        form = tk.Frame(panel, bg="white")
        form.pack(anchor="w", padx=16, pady=8)

        fields = [
            ("Book Type",
             ttk.Combobox(form, textvariable=self.book_type_var, values=list(BOOK_TYPES.keys()), state="readonly",
                          width=34)),
            ("Book ID", tk.Entry(form, textvariable=self.book_id_var, width=37)),
            ("Title", tk.Entry(form, textvariable=self.book_title_var, width=37)),
            ("Year", tk.Entry(form, textvariable=self.book_year_var, width=37)),
            ("Author", tk.Entry(form, textvariable=self.book_author_var, width=37)),
            ("Pages", tk.Entry(form, textvariable=self.book_pages_var, width=37)),
        ]
        for row, (label, widget) in enumerate(fields):
            tk.Label(form, text=label, bg="white", fg="#2b2b2b", font=("Segoe UI", 10)).grid(row=row, column=0,
                                                                                             sticky="w", pady=7,
                                                                                             padx=(0, 10))
            widget.grid(row=row, column=1, sticky="w", pady=7)

        btn_frame = tk.Frame(panel, bg="white")
        btn_frame.pack(anchor="w", padx=16, pady=(10, 16))

        tk.Button(btn_frame, text="Save Book", command=self.add_book, bg="#1f6f43", fg="white", relief="flat", padx=14,
                  pady=8, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(side="left", padx=(0, 10))
        tk.Button(btn_frame, text="📷 Auto-Fill via Camera", command=self.trigger_scanner, bg=self.colors['card_blue'],
                  fg="white", relief="flat", padx=14, pady=8, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(
            side="left")
        return panel

    def trigger_scanner(self):
        self.status_var.set("Opening webcam... hold a book's barcode to the camera.")
        self.root.update()

        isbn, title, author = scan_and_fetch_book()

        if isbn and title:
            self.book_id_var.set(isbn)
            self.book_title_var.set(title)
            self.book_author_var.set(author)
            self.status_var.set(f"Successfully scanned '{title}'.")
        elif isbn:
            self.book_id_var.set(isbn)
            self.status_var.set("Scanned ISBN, but book not found in Open Library database.")
        else:
            self.status_var.set("Scan cancelled.")

    def _build_view_books_screen(self) -> tk.Frame:
        panel = self._make_panel("View Books")

        tree_container = tk.Frame(panel, bg="white")
        tree_container.pack(fill="both", expand=True, padx=16, pady=(4, 10))

        v_scroll = ttk.Scrollbar(tree_container, orient="vertical")
        h_scroll = ttk.Scrollbar(tree_container, orient="horizontal")

        columns = ("id", "type", "title", "year", "author", "pages", "status")
        self.books_tree = ttk.Treeview(tree_container, columns=columns, show="headings", yscrollcommand=v_scroll.set,
                                       xscrollcommand=h_scroll.set)

        v_scroll.config(command=self.books_tree.yview)
        h_scroll.config(command=self.books_tree.xview)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.books_tree.pack(side="left", fill="both", expand=True)

        headings = {"id": "Book ID", "type": "Type", "title": "Title", "year": "Year", "author": "Author",
                    "pages": "Pages", "status": "Status"}
        widths = {"id": 90, "type": 110, "title": 230, "year": 70, "author": 170, "pages": 70, "status": 90}
        for key in columns:
            self.books_tree.heading(key, text=headings[key])
            self.books_tree.column(key, width=widths[key], minwidth=widths[key], anchor="w")

        # Student restriction for Virtual Barcode visibility
        if self.current_role == 'admin':
            btn_frame = tk.Frame(panel, bg="white")
            btn_frame.pack(fill="x", padx=16, pady=(0, 16))
            tk.Button(btn_frame, text="👁️ Show Virtual Barcode", command=self.show_selected_barcode,
                      bg=self.colors['card_indigo'], fg="white", relief="flat", padx=14, pady=8,
                      font=("Segoe UI", 10, "bold"), cursor="hand2").pack(side="left")

        return panel

    def show_selected_barcode(self):
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please click a book in the list first.")
            return

        item_values = self.books_tree.item(selected[0], "values")
        book_id = item_values[0]

        filepath = f"barcodes/{book_id}.png"

        if not os.path.exists(filepath):
            try:
                generate_local_barcode(book_id)
            except Exception as e:
                messagebox.showerror("Error", f"Could not generate barcode image: {e}"); return

        popup = tk.Toplevel(self.root)
        popup.title(f"Access Barcode: {book_id}")
        popup.geometry("400x250")
        popup.configure(bg="white")
        popup.attributes('-topmost', True)  # <--- THIS FIXES THE KICK-OUT BUG

        try:
            img = Image.open(filepath)
            img = img.resize((350, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            lbl = tk.Label(popup, image=photo, bg="white")
            lbl.image = photo
            lbl.pack(expand=True, pady=10)

            tk.Label(popup, text="Click 'Search' in the sidebar to scan this image instantly.", bg="white",
                     font=("Segoe UI", 9)).pack(pady=(0, 10))
        except Exception as e:
            tk.Label(popup, text="Could not load barcode image.", bg="white").pack()

    def _build_delete_book_screen(self) -> tk.Frame:
        panel = self._make_panel("Delete Book")
        wrap = tk.Frame(panel, bg="white")
        wrap.pack(anchor="w", padx=16, pady=12)
        tk.Label(wrap, text="Book ID", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w",
                                                                               padx=(0, 10))
        tk.Entry(wrap, textvariable=self.delete_id_var, width=35).grid(row=0, column=1, sticky="w")
        tk.Button(panel, text="Delete Book", command=self.delete_book, bg="#a83a2a", fg="white", relief="flat", padx=14,
                  pady=8, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=8)
        return panel

    def _build_issue_book_screen(self) -> tk.Frame:
        panel = self._make_panel("Issue Book")
        wrap = tk.Frame(panel, bg="white")
        wrap.pack(anchor="w", padx=16, pady=12)
        tk.Label(wrap, text="Member ID", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=6,
                                                                                 padx=(0, 10))
        tk.Entry(wrap, textvariable=self.issue_member_var, width=35).grid(row=0, column=1, sticky="w", pady=6)
        tk.Label(wrap, text="Book ID", bg="white", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6,
                                                                               padx=(0, 10))
        tk.Entry(wrap, textvariable=self.issue_book_var, width=35).grid(row=1, column=1, sticky="w", pady=6)
        tk.Button(panel, text="Issue Book", command=self.issue_book, bg="#284d9b", fg="white", relief="flat", padx=14,
                  pady=8, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=8)
        return panel

    def _build_request_book_screen(self) -> tk.Frame:
        panel = self._make_panel("Request Book")
        wrap = tk.Frame(panel, bg="white")
        wrap.pack(anchor="w", padx=16, pady=12)

        tk.Label(wrap, text="Member ID", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=6,
                                                                                 padx=(0, 10))
        tk.Entry(wrap, textvariable=self.request_member_var, width=35).grid(row=0, column=1, sticky="w", pady=6)

        tk.Label(wrap, text="Book ID", bg="white", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6,
                                                                               padx=(0, 10))
        tk.Entry(wrap, textvariable=self.request_book_var, width=35).grid(row=1, column=1, sticky="w", pady=6)

        tk.Button(panel, text="Submit Request", command=self.request_book, bg=self.colors['card_orange'], fg="white",
                  relief="flat", padx=14, pady=8, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(anchor="w",
                                                                                                      padx=16, pady=8)
        return panel

    def request_book(self) -> None:
        member_id = self.request_member_var.get().strip()
        book_id = self.request_book_var.get().strip()

        if not member_id or not book_id:
            messagebox.showerror("Error", "Enter member ID and book ID.")
            return

        member = self.library.members.get(member_id)
        book = self.library.items.get(book_id)

        if member is None:
            messagebox.showerror("Error", "Member not found. Please register first.")
            return
        if book is None:
            messagebox.showerror("Error", "Book not found in the catalog.")
            return

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.library.log_transaction(member.name, book.title, "Request", current_time, "Pending")

        self.request_member_var.set("")
        self.request_book_var.set("")
        self.refresh_views()
        self.status_var.set(f"Book '{book.title}' requested by {member.name}.")
        messagebox.showinfo("Success",
                            f"Your request for '{book.title}' has been submitted and is pending admin approval.")

    def _build_return_book_screen(self) -> tk.Frame:
        panel = self._make_panel("Return Book")
        wrap = tk.Frame(panel, bg="white")
        wrap.pack(anchor="w", padx=16, pady=12)
        tk.Label(wrap, text="Member ID", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=6,
                                                                                 padx=(0, 10))
        tk.Entry(wrap, textvariable=self.return_member_var, width=35).grid(row=0, column=1, sticky="w", pady=6)
        tk.Label(wrap, text="Book ID", bg="white", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6,
                                                                               padx=(0, 10))
        tk.Entry(wrap, textvariable=self.return_book_var, width=35).grid(row=1, column=1, sticky="w", pady=6)
        tk.Button(panel, text="Return Book", command=self.return_book, bg="#6a4d1f", fg="white", relief="flat", padx=14,
                  pady=8, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=8)
        return panel

    def _build_member_screen(self) -> tk.Frame:
        panel = self._make_panel("Register Member")
        form = tk.Frame(panel, bg="white")
        form.pack(anchor="w", padx=16, pady=10)

        tk.Label(form, text="Member ID", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=6,
                                                                                 padx=(0, 10))
        tk.Entry(form, textvariable=self.member_id_var, width=35).grid(row=0, column=1, sticky="w", pady=6)

        tk.Label(form, text="Name", bg="white", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6,
                                                                            padx=(0, 10))
        tk.Entry(form, textvariable=self.member_name_var, width=35).grid(row=1, column=1, sticky="w", pady=6)

        tk.Button(panel, text="Register", command=self.register_member, bg="#1f6f43", fg="white", relief="flat",
                  padx=14, pady=8, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=(8, 12))

        list_container = tk.Frame(panel, bg="white")
        list_container.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        v_scroll = ttk.Scrollbar(list_container, orient="vertical")
        h_scroll = ttk.Scrollbar(list_container, orient="horizontal")

        self.members_listbox = tk.Listbox(list_container, yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        v_scroll.config(command=self.members_listbox.yview)
        h_scroll.config(command=self.members_listbox.xview)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.members_listbox.pack(side="left", fill="both", expand=True)

        return panel

    def _build_report_screen(self) -> tk.Frame:
        panel = self._make_panel("Transaction Reports")

        tree_container = tk.Frame(panel, bg="white")
        tree_container.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        v_scroll = ttk.Scrollbar(tree_container, orient="vertical")
        h_scroll = ttk.Scrollbar(tree_container, orient="horizontal")

        columns = ("member", "book", "type", "date", "status")
        self.reports_tree = ttk.Treeview(tree_container, columns=columns, show="headings", yscrollcommand=v_scroll.set,
                                         xscrollcommand=h_scroll.set)

        v_scroll.config(command=self.reports_tree.yview)
        h_scroll.config(command=self.reports_tree.xview)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.reports_tree.pack(side="left", fill="both", expand=True)

        headings = {"member": "Member Name", "book": "Book Title", "type": "Transaction Type", "date": "Date & Time",
                    "status": "Status"}
        widths = {"member": 200, "book": 250, "type": 150, "date": 200, "status": 100}
        for key in columns:
            self.reports_tree.heading(key, text=headings[key])
            self.reports_tree.column(key, width=widths[key], minwidth=widths[key], anchor="w")

        return panel

    def refresh_views(self) -> None:
        self.transactions = self.library.get_transactions()

        if hasattr(self, "books_tree"):
            for row in self.books_tree.get_children():
                self.books_tree.delete(row)
            for item in self.library.items.values():
                self.books_tree.insert(
                    "", "end",
                    values=(
                        item.item_id, item.get_item_type(), item.title, item.year,
                        getattr(item, 'author', '-'), getattr(item, 'pages', '-'),
                        "Issued" if item.is_borrowed else "Available",
                    ),
                )

        if hasattr(self, "members_listbox"):
            self.members_listbox.delete(0, tk.END)
            for member in self.library.members.values():
                borrowed = ", ".join(member.borrowed_item_ids) if member.borrowed_item_ids else "-"
                self.members_listbox.insert(tk.END, f"{member.member_id} | {member.name} | Borrowed: {borrowed}")

        if hasattr(self, "reports_tree"):
            for row in self.reports_tree.get_children():
                self.reports_tree.delete(row)
            for t in self.transactions:
                self.reports_tree.insert("", "end", values=(t["member"], t["book"], t["type"], t["date"], t["status"]))

        if "home" in self.screens and self.screens["home"].winfo_ismapped():
            self.render_dashboard(self.screens["home"])

    def add_book(self) -> None:
        item_id = self.book_id_var.get().strip()
        title = self.book_title_var.get().strip()
        year_raw = self.book_year_var.get().strip()
        author = self.book_author_var.get().strip()
        pages_raw = self.book_pages_var.get().strip()

        if not all([item_id, title, year_raw, author, pages_raw]):
            messagebox.showerror("Error", "Please fill in all book fields.")
            return

        try:
            year = int(year_raw)
            pages = int(pages_raw)
        except ValueError:
            messagebox.showerror("Error", "Year and pages must be numbers.")
            return

        book_class = BOOK_TYPES[self.book_type_var.get()]
        book = book_class(item_id, title, year, author, pages)

        if not self.library.add_item(book):
            messagebox.showerror("Error", "Book ID already exists.")
            return

        try:
            generate_local_barcode(item_id)
        except Exception as e:
            print(f"Could not generate barcode image: {e}")

        self.book_id_var.set("")
        self.book_title_var.set("")
        self.book_year_var.set("")
        self.book_author_var.set("")
        self.book_pages_var.set("")
        self.refresh_views()
        self.status_var.set(f"Added book {item_id}.")
        messagebox.showinfo("Success", "Book added successfully.")

    def register_member(self) -> None:
        member_id = self.member_id_var.get().strip()
        name = self.member_name_var.get().strip()
        if not member_id or not name:
            messagebox.showerror("Error", "Enter member ID and name.")
            return

        if not self.library.register_member(Member(member_id, name)):
            messagebox.showerror("Error", "Member ID already exists.")
            return

        self.member_id_var.set("")
        self.member_name_var.set("")
        self.refresh_views()
        self.status_var.set(f"Registered member {member_id}.")
        messagebox.showinfo("Success", "Member registered successfully.")

    def issue_book(self) -> None:
        member_id = self.issue_member_var.get().strip()
        book_id = self.issue_book_var.get().strip()
        if not member_id or not book_id:
            messagebox.showerror("Error", "Enter member ID and book ID.")
            return

        ok, message = self.library.borrow_item(member_id, book_id)
        if not ok:
            messagebox.showerror("Issue Failed", message)
            return

        self.issue_member_var.set("")
        self.issue_book_var.set("")
        self.refresh_views()
        self.status_var.set(message)
        messagebox.showinfo("Success", message)

    def return_book(self) -> None:
        member_id = self.return_member_var.get().strip()
        book_id = self.return_book_var.get().strip()
        if not member_id or not book_id:
            messagebox.showerror("Error", "Enter member ID and book ID.")
            return

        ok, message = self.library.return_item(member_id, book_id)
        if not ok:
            messagebox.showerror("Return Failed", message)
            return

        self.return_member_var.set("")
        self.return_book_var.set("")
        self.refresh_views()
        self.status_var.set(message)
        messagebox.showinfo("Success", message)

    def delete_book(self) -> None:
        book_id = self.delete_id_var.get().strip()
        if not book_id:
            messagebox.showerror("Error", "Enter a book ID.")
            return

        ok, message = self.library.delete_item(book_id)
        if not ok:
            messagebox.showerror("Delete Failed", message)
            return

        self.delete_id_var.set("")
        self.refresh_views()
        self.status_var.set(f"Deleted book {book_id}.")
        messagebox.showinfo("Success", message)


def run() -> None:
    root = tk.Tk()
    LibraryApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()