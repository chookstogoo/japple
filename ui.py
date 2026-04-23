import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter import ttk

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

        self.library = Library("City Library")
        self.status_var = tk.StringVar(value="Welcome. Add books and manage transactions.")

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

        self._init_vars()
        self.init_sample_data()
        self._build_layout()
        self._build_screens()
        self._show_screen("home")
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
        self.books = []
        self.members = []
        self.transactions = []

    def init_sample_data(self):
        """Initialize empty data for the library system"""
        self.books = []
        self.members = []
        self.transactions = []

    def _build_layout(self) -> None:
        """Create the overall structure: Sidebar + Main Area + Static Header"""
        self.create_sidebar()

        self.main_frame = tk.Frame(self.root, bg=self.colors['main_bg'])
        self.main_frame.pack(side='right', fill='both', expand=True)

        self.create_header(self.main_frame)

        self.content_frame = tk.Frame(self.main_frame, bg=self.colors['main_bg'])
        self.content_frame.pack(fill='both', expand=True)

        self.status_label = tk.Label(
            self.main_frame,
            textvariable=self.status_var,
            anchor="w",
            bg="#e2e8f0",
            fg="#0f172a",
            padx=12,
            pady=6,
            font=("Segoe UI", 9),
        )
        self.status_label.pack(side="bottom", fill="x")

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=self.colors['sidebar'], width=250)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        logo_frame.pack(fill='x', pady=20)

        logo_label = tk.Label(logo_frame, text="📚 LIBRARY MS", font=('Arial', 18, 'bold'), fg='white',
                              bg=self.colors['sidebar'])
        logo_label.pack(padx=20)

        # Cleaned up navigation list with Settings reinstated
        nav_items = [
            ("📊 Dashboard", True),
            ("📖 Books", False),
            ("👥 Members", False),
            ("🔄 Transactions", False),
            ("📋 Reports", False),
            ("⚙️ Settings", False),
            ("🔍 Search", False)
        ]

        for item, is_active in nav_items:
            bg_color = '#2563eb' if is_active else self.colors['sidebar']
            nav_button = tk.Button(self.sidebar, text=item, font=('Arial', 11),
                                   bg=bg_color, fg='white', bd=0, pady=15,
                                   anchor='w', padx=20, cursor='hand2',
                                   command=lambda x=item: self.nav_click(x))
            nav_button.pack(fill='x', padx=10, pady=2)

        quick_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        quick_frame.pack(fill='x', pady=20)

        tk.Label(quick_frame, text="QUICK ACTIONS", font=('Arial', 10, 'bold'), fg='#94a3b8',
                 bg=self.colors['sidebar']).pack(padx=20, pady=(0, 10))

        quick_actions = [
            ("➕ Add Book", self.colors['card_green']),
            ("👤 Add Member", self.colors['card_blue']),
            ("📊 Generate Report", self.colors['card_orange'])
        ]

        for action, color in quick_actions:
            btn = tk.Button(self.sidebar, text=action, font=('Arial', 10),
                            bg=color, fg='white', bd=0, pady=8,
                            cursor='hand2', command=lambda x=action: self.quick_action(x))
            btn.pack(fill='x', padx=20, pady=2)

        bottom_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        bottom_frame.pack(side='bottom', fill='x', pady=20)

        tk.Label(bottom_frame, text="Library Management System", font=('Arial', 10), fg='#94a3b8',
                 bg=self.colors['sidebar']).pack(padx=20)
        tk.Label(bottom_frame, text="© 2026 All rights reserved.", font=('Arial', 9), fg='#64748b',
                 bg=self.colors['sidebar']).pack(padx=20, pady=5)

    def nav_click(self, item):
        if "Dashboard" in item:
            self._show_screen("home")
        elif "Books" in item:
            self._show_screen("view")
        elif "Members" in item:
            self._show_screen("member")
        elif "Transactions" in item:
            self._show_screen("issue")
        elif "Reports" in item:
            self._show_screen("report")
        elif "Settings" in item:
            self._show_screen("settings")
        elif "Search" in item:
            self._show_screen("delete")  # You can remap Search functionality later if needed
        else:
            messagebox.showinfo("Navigation", f"Module '{item}' is under construction.")

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

        tk.Label(title_frame, text="📊 Library Dashboard", font=('Arial', 24, 'bold'),
                 fg=self.colors['text_dark'], bg=self.colors['white']).pack(anchor='w')
        tk.Label(title_frame, text=f"Welcome back! Today is {datetime.now().strftime('%B %d, %Y')}",
                 font=('Arial', 11), fg=self.colors['text_light'], bg=self.colors['white']).pack(anchor='w')

        right_frame = tk.Frame(header, bg=self.colors['white'])
        right_frame.pack(side='right', padx=20, pady=20)

        search_frame = tk.Frame(right_frame, bg='#f3f4f6', relief='flat', bd=1)
        search_frame.pack(side='left', padx=10)

        search_entry = tk.Entry(search_frame, font=('Arial', 10), bg='#f3f4f6', bd=0, width=25,
                                fg=self.colors['text_light'])
        search_entry.pack(side='left', padx=10, pady=8)
        search_entry.insert(0, "Search books, members...")

        tk.Button(search_frame, text="🔍", font=('Arial', 12), bg='#f3f4f6', bd=0, cursor='hand2').pack(side='right',
                                                                                                       padx=5)

        user_frame = tk.Frame(right_frame, bg=self.colors['white'])
        user_frame.pack(side='left', padx=10)

        tk.Button(user_frame, text="👤", font=('Arial', 16), bg=self.colors['card_blue'], fg='white', width=3, height=1,
                  bd=0, cursor='hand2').pack(side='left')

        user_info = tk.Frame(user_frame, bg=self.colors['white'])
        user_info.pack(side='left', padx=10)

        tk.Label(user_info, text="Hi, Librarian", font=('Arial', 12, 'bold'), fg=self.colors['text_dark'],
                 bg=self.colors['white']).pack(anchor='w')
        tk.Label(user_info, text="admin@library.com", font=('Arial', 9), fg=self.colors['text_light'],
                 bg=self.colors['white']).pack(anchor='w')

    def _build_screens(self) -> None:
        self.screens: dict[str, tk.Frame] = {
            "home": self._build_home_screen(),
            "add": self._build_add_book_screen(),
            "view": self._build_view_books_screen(),
            "delete": self._build_delete_book_screen(),
            "issue": self._build_issue_book_screen(),
            "return": self._build_return_book_screen(),
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
        tk.Label(
            panel,
            text=title,
            bg="white",
            fg="#1b2b3a",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", padx=16, pady=(14, 10))
        return panel

    def _build_home_screen(self) -> tk.Frame:
        panel = tk.Frame(self.content_frame, bg=self.colors["main_bg"])
        self.render_dashboard(panel)
        return panel

    def render_dashboard(self, parent: tk.Frame):
        """Clears and rebuilds a fully responsive dashboard that physically fits one screen"""
        for widget in parent.winfo_children():
            widget.destroy()

        # Create three proportional rows that share the vertical space
        top_row = tk.Frame(parent, bg=self.colors['main_bg'])
        top_row.pack(fill='both', expand=True, padx=20, pady=(10, 5))

        mid_row = tk.Frame(parent, bg=self.colors['main_bg'])
        mid_row.pack(fill='both', expand=True, padx=20, pady=5)

        bot_row = tk.Frame(parent, bg=self.colors['main_bg'])
        bot_row.pack(fill='both', expand=True, padx=20, pady=(5, 20))

        self.create_metric_cards(top_row)
        self.create_middle_section(mid_row)
        self.create_bottom_section(bot_row)

    def create_metric_cards(self, parent: tk.Frame):
        """Responsive metric cards that squish and stretch automatically"""
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

    def create_transactions_list(self, parent: tk.Frame):
        status_colors = {
            'Completed': self.colors['card_green'],
            'Active': self.colors['card_blue'],
            'Pending': self.colors['card_orange'],
            'Overdue': self.colors['card_red']
        }
        type_icons = {'Borrow': '📖', 'Return': '📚', 'Reserve': '🔖', 'Renew': '🔄'}

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

            status_bg = status_colors.get(transaction['status'], self.colors['card_blue'])
            tk.Label(right_details, text=transaction['status'], font=('Arial', 8, 'bold'), fg='white', bg=status_bg,
                     padx=6, pady=2).pack(anchor='e')

    def create_category_chart(self, parent: tk.Frame):
        chart_frame = tk.Frame(parent, bg=self.colors['white'])
        chart_frame.pack(fill='both', expand=True, padx=20, pady=10)

        categories = {}
        for book in self.library.items.values():
            ctype = book.get_item_type()
            categories[ctype] = categories.get(ctype, 0) + 1

        if not categories:
            categories = {'None': 1}

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
                name = member.name
                member_id = member.member_id
                activity = f"{len(member.borrowed_item_ids)} books"

                member_row = tk.Frame(members_frame, bg=self.colors['white'])
                member_row.pack(fill='x', padx=20, pady=2)

                avatar = tk.Frame(member_row, bg=color, width=30, height=30)
                avatar.pack(side='left', padx=(0, 10))
                avatar.pack_propagate(False)
                tk.Label(avatar, text=name[0].upper(), font=('Arial', 10, 'bold'), fg='white', bg=color).place(relx=0.5,
                                                                                                               rely=0.5,
                                                                                                               anchor='center')

                info_frame = tk.Frame(member_row, bg=self.colors['white'])
                info_frame.pack(side='left', fill='x', expand=True)
                tk.Label(info_frame, text=name, font=('Arial', 10, 'bold'), fg=self.colors['text_dark'],
                         bg=self.colors['white']).pack(anchor='w')
                tk.Label(info_frame, text=f"{member_id} • {activity}", font=('Arial', 8), fg=self.colors['text_light'],
                         bg=self.colors['white']).pack(anchor='w')

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

        other_stats = tk.Frame(stats_frame, bg=self.colors['white'])
        other_stats.pack(fill='x', padx=20, pady=5)
        tk.Label(other_stats, text="New Members This Month: 0", font=('Arial', 9), fg=self.colors['text_dark'],
                 bg=self.colors['white']).pack(anchor='w')
        tk.Label(other_stats, text="Average Books per Member: 0", font=('Arial', 9), fg=self.colors['text_dark'],
                 bg=self.colors['white']).pack(anchor='w', pady=(2, 0))

    def _build_settings_screen(self) -> tk.Frame:
        """Creates the settings panel to act as a hub for database management"""
        panel = self._make_panel("⚙️ Settings & Database Management")

        wrap = tk.Frame(panel, bg="white")
        wrap.pack(anchor="w", padx=16, pady=12)

        tk.Label(wrap, text="Library Catalog Controls", bg="white", font=("Segoe UI", 12, "bold")).pack(anchor="w",
                                                                                                        pady=(0, 15))

        tk.Button(
            wrap,
            text="➕ Add New Book",
            command=lambda: self._show_screen("add"),
            bg=self.colors['card_green'],
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            font=("Segoe UI", 10, "bold"),
            width=25,
            cursor="hand2"
        ).pack(anchor="w", pady=8)

        tk.Button(
            wrap,
            text="🗑️ Delete Book",
            command=lambda: self._show_screen("delete"),
            bg=self.colors['card_red'],
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            font=("Segoe UI", 10, "bold"),
            width=25,
            cursor="hand2"
        ).pack(anchor="w", pady=8)

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
            tk.Label(form, text=label, bg="white", fg="#2b2b2b", font=("Segoe UI", 10)).grid(
                row=row, column=0, sticky="w", pady=7, padx=(0, 10)
            )
            widget.grid(row=row, column=1, sticky="w", pady=7)

        tk.Button(
            panel,
            text="Save Book",
            command=self.add_book,
            bg="#1f6f43",
            fg="white",
            relief="flat",
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=16, pady=(10, 16))
        return panel

    def _build_view_books_screen(self) -> tk.Frame:
        panel = self._make_panel("View Books")

        tree_container = tk.Frame(panel, bg="white")
        tree_container.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        v_scroll = ttk.Scrollbar(tree_container, orient="vertical")
        h_scroll = ttk.Scrollbar(tree_container, orient="horizontal")

        columns = ("id", "type", "title", "year", "author", "pages", "status")
        self.books_tree = ttk.Treeview(tree_container, columns=columns, show="headings",
                                       yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.config(command=self.books_tree.yview)
        h_scroll.config(command=self.books_tree.xview)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.books_tree.pack(side="left", fill="both", expand=True)

        headings = {
            "id": "Book ID", "type": "Type", "title": "Title", "year": "Year",
            "author": "Author", "pages": "Pages", "status": "Status",
        }
        widths = {"id": 90, "type": 110, "title": 230, "year": 70, "author": 170, "pages": 70, "status": 90}
        for key in columns:
            self.books_tree.heading(key, text=headings[key])
            self.books_tree.column(key, width=widths[key], minwidth=widths[key], anchor="w")

        return panel

    def _build_delete_book_screen(self) -> tk.Frame:
        panel = self._make_panel("Delete Book")
        wrap = tk.Frame(panel, bg="white")
        wrap.pack(anchor="w", padx=16, pady=12)
        tk.Label(wrap, text="Book ID", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w",
                                                                               padx=(0, 10))
        tk.Entry(wrap, textvariable=self.delete_id_var, width=35).grid(row=0, column=1, sticky="w")
        tk.Button(
            panel,
            text="Delete Book",
            command=self.delete_book,
            bg="#a83a2a",
            fg="white",
            relief="flat",
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=16, pady=8)
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
        tk.Button(
            panel,
            text="Issue Book",
            command=self.issue_book,
            bg="#284d9b",
            fg="white",
            relief="flat",
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=16, pady=8)
        return panel

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
        tk.Button(
            panel,
            text="Return Book",
            command=self.return_book,
            bg="#6a4d1f",
            fg="white",
            relief="flat",
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=16, pady=8)
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

        tk.Button(
            panel,
            text="Register",
            command=self.register_member,
            bg="#1f6f43",
            fg="white",
            relief="flat",
            padx=14,
            pady=8,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=16, pady=(8, 12))

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
        self.reports_tree = ttk.Treeview(tree_container, columns=columns, show="headings",
                                         yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.config(command=self.reports_tree.yview)
        h_scroll.config(command=self.reports_tree.xview)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.reports_tree.pack(side="left", fill="both", expand=True)

        headings = {
            "member": "Member Name", "book": "Book Title", "type": "Transaction Type",
            "date": "Date & Time", "status": "Status"
        }
        widths = {"member": 200, "book": 250, "type": 150, "date": 200, "status": 100}
        for key in columns:
            self.reports_tree.heading(key, text=headings[key])
            self.reports_tree.column(key, width=widths[key], minwidth=widths[key], anchor="w")

        return panel

    def refresh_views(self) -> None:
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

        if self.screens["home"].winfo_ismapped():
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

        member = self.library.members.get(member_id)
        book = self.library.items.get(book_id)

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.transactions.insert(0, {
            "member": member.name, "book": book.title,
            "type": "Borrow", "date": current_time, "status": "Active"
        })

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

        member = self.library.members.get(member_id)
        book = self.library.items.get(book_id)

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.transactions.insert(0, {
            "member": member.name, "book": book.title,
            "type": "Return", "date": current_time, "status": "Completed"
        })

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