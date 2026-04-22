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
        self.books = []  # Moved from init_sample_data
        self.members = []  # Moved from init_sample_data
        self.transactions = []  # Moved from init_sample_data

    def _build_layout(self) -> None:
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=self.colors["sidebar"], width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=self.colors["sidebar"])
        logo_frame.pack(fill="x", pady=20)
        tk.Label(
            logo_frame,
            text="📚 LIBRARY MS",
            font=("Arial", 18, "bold"),
            fg="white",
            bg=self.colors["sidebar"],
        ).pack(padx=20)

        nav_items = [
            ("Dashboard", "home"),
            ("Add Book", "add"),
            ("View Books", "view"),
            ("Delete Book", "delete"),
            ("Issue Book", "issue"),
            ("Return Book", "return"),
            ("Register Member", "member"),
        ]

        for label, key in nav_items:
            tk.Button(
                self.sidebar,
                text=label,
                command=lambda k=key: self._show_screen(k),
                bg=self.colors["sidebar"],
                fg="white",
                activebackground="#2563eb",
                activeforeground="white",
                bd=0,
                relief="flat",
                anchor="w",
                padx=20,
                pady=12,
                font=("Segoe UI", 10, "bold"),
            ).pack(fill="x", padx=10, pady=2)

        # Main content area
        self.main_frame = tk.Frame(self.root, bg=self.colors["main_bg"])
        self.main_frame.pack(side="left", fill="both", expand=True)

        # Status bar
        self.status_label = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            bg="#e2e8f0",
            fg="#0f172a",
            padx=12,
            pady=6,
            font=("Segoe UI", 9),
        )
        self.status_label.pack(side="bottom", fill="x")

    def init_sample_data(self):
        """Initialize sample data for the library system"""
        # self.books = [ # Moved to _init_vars
        #     {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "978-0-7432-7356-5", "status": "Available", "category": "Fiction"},
        #     {"title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "978-0-06-112008-4", "status": "Borrowed", "category": "Fiction"},
        # ]
        # self.members = [ # Moved to _init_vars
        #     {"name": "John Smith", "id": "M001", "email": "john.smith@email.com", "phone": "+1-555-0123", "status": "Active"},
        #     {"name": "Emily Johnson", "id": "M002", "email": "emily.j@email.com", "phone": "+1-555-0124", "status": "Active"},
        # ]
        # self.transactions = [ # Moved to _init_vars
        #     {"member": "John Smith", "book": "The Great Gatsby", "type": "Return", "date": "2 hours ago", "status": "Completed"},
        #     {"member": "Emily Johnson", "book": "To Kill a Mockingbird", "type": "Borrow", "date": "5 hours ago", "status": "Active"},
        # ]
        pass # No longer needed to initialize here, but keeping the method for potential future use

    def _build_screens(self) -> None:
        self.screens: dict[str, tk.Frame] = {
            "home": self._build_home_screen(),
            "add": self._build_add_book_screen(),
            "view": self._build_view_books_screen(),
            "delete": self._build_delete_book_screen(),
            "issue": self._build_issue_book_screen(),
            "return": self._build_return_book_screen(),
            "member": self._build_member_screen(),
        }
        for screen in self.screens.values():
            screen.pack_forget()

    def _show_screen(self, key: str) -> None:
        for frame in self.screens.values():
            frame.pack_forget()
        self.screens[key].pack(fill="both", expand=True)
        self.refresh_views()

    def _make_panel(self, title: str) -> tk.Frame:
        panel = tk.Frame(self.main_frame, bg="white", bd=1, relief="solid")
        tk.Label(
            panel,
            text=title,
            bg="white",
            fg="#1b2b3a",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", padx=16, pady=(14, 10))
        return panel

    def _build_home_screen(self) -> tk.Frame:
        panel = self._make_panel("Dashboard")
        self.render_dashboard(panel)
        return panel

    def render_dashboard(self, parent: tk.Frame):
        for widget in parent.winfo_children():
            if isinstance(widget, (tk.Frame, tk.Canvas)):
                widget.destroy()

        content_canvas = tk.Canvas(parent, bg=self.colors["main_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=content_canvas.yview)
        scrollable_frame = tk.Frame(content_canvas, bg=self.colors["main_bg"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all")),
        )
        content_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        content_canvas.configure(yscrollcommand=scrollbar.set)

        content_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.create_header(scrollable_frame)
        self.create_metric_cards(scrollable_frame)
        self.create_middle_section(scrollable_frame)
        self.create_bottom_section(scrollable_frame)

    def create_header(self, parent: tk.Frame):
        header = tk.Frame(parent, bg=self.colors["white"], height=80)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=self.colors["white"])
        title_frame.pack(side="left", padx=20, pady=20)
        tk.Label(
            title_frame,
            text="📊 Library Dashboard",
            font=("Arial", 24, "bold"),
            fg=self.colors["text_dark"],
            bg=self.colors["white"],
        ).pack(anchor="w")
        tk.Label(
            title_frame,
            text=f"Welcome back! Today is {datetime.now().strftime('%B %d, %Y')}",
            font=("Arial", 11),
            fg=self.colors["text_light"],
            bg=self.colors["white"],
        ).pack(anchor="w")

    def create_metric_cards(self, parent: tk.Frame):
        cards_frame = tk.Frame(parent, bg=self.colors["main_bg"])
        cards_frame.pack(fill="x", padx=20, pady=10)

        total_books = len(self.library.items)
        available_books = total_books - sum(1 for b in self.library.items.values() if b.is_borrowed)
        borrowed_books = sum(1 for b in self.library.items.values() if b.is_borrowed)
        total_members = len(self.library.members)

        cards_data = [
            (f"{total_books:,}", "Total Books", self.colors["card_blue"], "📚"),
            (f"{available_books:,}", "Available Books", self.colors["card_green"], "✅"),
            (f"{borrowed_books:,}", "Books Borrowed", self.colors["card_orange"], "📖"),
            (f"{total_members:,}", "Total Members", self.colors["card_purple"], "👥"),
        ]

        for i, (value, label, color, icon) in enumerate(cards_data):
            card = tk.Frame(cards_frame, bg=color, width=280, height=122)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            card.pack_propagate(False)
            tk.Label(card, text=icon, font=("Arial", 20), fg="white", bg=color).pack(pady=(15, 5))
            tk.Label(card, text=value, font=("Arial", 24, "bold"), fg="white", bg=color).pack()
            tk.Label(card, text=label, font=("Arial", 10), fg="white", bg=color).pack(pady=(0, 10))
            cards_frame.grid_columnconfigure(i, weight=1)

    def create_middle_section(self, parent: tk.Frame):
        middle_frame = tk.Frame(parent, bg=self.colors["main_bg"])
        middle_frame.pack(fill="x", padx=20, pady=20)

        left_frame = tk.Frame(middle_frame, bg=self.colors["white"], relief="flat", bd=1)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        trans_header = tk.Frame(left_frame, bg=self.colors["white"])
        trans_header.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(
            trans_header,
            text="Recent Transactions",
            font=("Arial", 16, "bold"),
            fg=self.colors["text_dark"],
            bg=self.colors["white"],
        ).pack(side="left")
        self.create_transactions_list(left_frame)

    def create_transactions_list(self, parent: tk.Frame):
        status_colors = {
            "Completed": self.colors["card_green"],
            "Active": self.colors["card_blue"],
        }
        type_icons = {"Borrow": "📖", "Return": "📚"}

        for transaction in self.transactions[:5]:
            trans_row = tk.Frame(parent, bg=self.colors["white"])
            trans_row.pack(fill="x", padx=20, pady=8)
            icon_color = status_colors.get(transaction["status"], self.colors["card_blue"])
            icon_frame = tk.Frame(trans_row, bg=icon_color, width=40, height=40)
            icon_frame.pack(side="left", padx=(0, 15))
            icon_frame.pack_propagate(False)
            icon_text = type_icons.get(transaction["type"], "📄")
            tk.Label(icon_frame, text=icon_text, font=("Arial", 12), fg="white", bg=icon_color).place(relx=0.5, rely=0.5, anchor="center")

            details_frame = tk.Frame(trans_row, bg=self.colors["white"])
            details_frame.pack(side="left", fill="x", expand=True)
            tk.Label(
                details_frame,
                text=f"{transaction['member']} - {transaction['book']}",
                font=("Arial", 11, "bold"),
                fg=self.colors["text_dark"],
                bg=self.colors["white"],
            ).pack(anchor="w")
            tk.Label(
                details_frame,
                text=f"{transaction['type']} • {transaction['date']}",
                font=("Arial", 9),
                fg=self.colors["text_light"],
                bg=self.colors["white"],
            ).pack(anchor="w")

    def create_bottom_section(self, parent: tk.Frame):
        bottom_frame = tk.Frame(parent, bg=self.colors["main_bg"])
        bottom_frame.pack(fill="x", padx=20, pady=20)

        members_frame = tk.Frame(bottom_frame, bg=self.colors["white"], width=400)
        members_frame.pack(side="left", fill="y", padx=(0, 10))
        members_frame.pack_propagate(False)
        tk.Label(
            members_frame,
            text="Top Active Members",
            font=("Arial", 16, "bold"),
            fg=self.colors["text_dark"],
            bg=self.colors["white"],
        ).pack(anchor="w", padx=20, pady=(20, 10))

        top_members = [
            ("John Smith", "12 books borrowed", "M001", self.colors["card_green"]),
            ("Emily Johnson", "8 books borrowed", "M002", self.colors["card_blue"]),
        ]
        for name, activity, member_id, color in top_members:
            member_row = tk.Frame(members_frame, bg=self.colors["white"])
            member_row.pack(fill="x", padx=20, pady=5)
            avatar = tk.Frame(member_row, bg=color, width=35, height=35)
            avatar.pack(side="left", padx=(0, 15))
            avatar.pack_propagate(False)
            tk.Label(avatar, text=name[0], font=("Arial", 12, "bold"), fg="white", bg=color).place(relx=0.5, rely=0.5, anchor="center")

            info_frame = tk.Frame(member_row, bg=self.colors["white"])
            info_frame.pack(side="left", fill="x", expand=True)
            tk.Label(info_frame, text=name, font=("Arial", 11, "bold"), fg=self.colors["text_dark"], bg=self.colors["white"]).pack(anchor="w")
            tk.Label(info_frame, text=f"{member_id} • {activity}", font=("Arial", 9), fg=self.colors["text_light"], bg=self.colors["white"]).pack(anchor="w")

    def _build_add_book_screen(self) -> tk.Frame:
        panel = self._make_panel("Add Book")
        form = tk.Frame(panel, bg="white")
        form.pack(anchor="w", padx=16, pady=8)

        fields = [
            ("Book Type", ttk.Combobox(form, textvariable=self.book_type_var, values=list(BOOK_TYPES.keys()), state="readonly", width=34)),
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
        columns = ("id", "type", "title", "year", "author", "pages", "status")
        self.books_tree = ttk.Treeview(panel, columns=columns, show="headings", height=18)
        headings = {
            "id": "Book ID", "type": "Type", "title": "Title", "year": "Year",
            "author": "Author", "pages": "Pages", "status": "Status",
        }
        widths = {"id": 90, "type": 110, "title": 230, "year": 70, "author": 170, "pages": 70, "status": 90}
        for key in columns:
            self.books_tree.heading(key, text=headings[key])
            self.books_tree.column(key, width=widths[key], anchor="w")
        self.books_tree.pack(fill="both", expand=True, padx=16, pady=(4, 16))
        return panel

    def _build_delete_book_screen(self) -> tk.Frame:
        panel = self._make_panel("Delete Book")
        wrap = tk.Frame(panel, bg="white")
        wrap.pack(anchor="w", padx=16, pady=12)
        tk.Label(wrap, text="Book ID", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=(0, 10))
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
        tk.Label(wrap, text="Member ID", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=6, padx=(0, 10))
        tk.Entry(wrap, textvariable=self.issue_member_var, width=35).grid(row=0, column=1, sticky="w", pady=6)
        tk.Label(wrap, text="Book ID", bg="white", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6, padx=(0, 10))
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
        tk.Label(wrap, text="Member ID", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=6, padx=(0, 10))
        tk.Entry(wrap, textvariable=self.return_member_var, width=35).grid(row=0, column=1, sticky="w", pady=6)
        tk.Label(wrap, text="Book ID", bg="white", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6, padx=(0, 10))
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
        tk.Label(form, text="Member ID", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=6, padx=(0, 10))
        tk.Entry(form, textvariable=self.member_id_var, width=35).grid(row=0, column=1, sticky="w", pady=6)
        tk.Label(form, text="Name", bg="white", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6, padx=(0, 10))
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
        self.members_listbox = tk.Listbox(panel, width=85, height=14)
        self.members_listbox.pack(fill="x", padx=16, pady=(4, 16))
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
                        getattr(item, 'author', '-'), getattr(item, 'pages', '-'), "Issued" if item.is_borrowed else "Available",
                    ),
                )

        if hasattr(self, "members_listbox"):
            self.members_listbox.delete(0, tk.END)
            for member in self.library.members.values():
                borrowed = ", ".join(member.borrowed_item_ids) if member.borrowed_item_ids else "-"
                self.members_listbox.insert(tk.END, f"{member.member_id} | {member.name} | Borrowed: {borrowed}")

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
