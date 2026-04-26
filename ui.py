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

        # Shared DB service
        self.library = Library("City Library")

        # Global State
        self.status_var = tk.StringVar(value="Welcome to the Library System.")
        self.current_user = None
        self.current_role = None

        # Define Color Palette
        self.colors = {
            "sidebar": "#1e293b",  # Slate 800
            "sidebar_active": "#2563eb",  # Blue 600
            "main_bg": "#f1f5f9",  # Slate 100
            "white": "#ffffff",
            "border": "#e2e8f0",  # Slate 200
            "text_dark": "#0f172a",  # Slate 900
            "text_light": "#64748b",  # Slate 500
            "card_blue": "#3b82f6",  # Blue 500
            "card_green": "#16a34a",  # Green 600
            "card_orange": "#f59e0b",  # Amber 500
            "card_red": "#dc2626",  # Red 600
            "card_purple": "#a855f7",  # Purple 500
            "card_indigo": "#6366f1",  # Indigo 500
            "status_pending": "#f59e0b",  # Orange
            "status_done": "#16a34a",  # Green
            "status_rejected": "#dc2626",  # Red
            "status_active": "#3b82f6"  # Blue
        }
        self.root.configure(bg=self.colors["main_bg"])

        # Create barcodes directory if not exists
        if not os.path.exists("barcodes"):
            os.makedirs("barcodes")

        # UI State containers
        self.main_container = None
        self.screens = {}

        self._build_login_screen()

    def on_closing(self):
        """Final cleanup before exiting."""
        # Close DB connection properly
        if hasattr(self, 'library') and hasattr(self.library, 'conn'):
            self.library.conn.close()
        self.root.destroy()
        os._exit(0)

    # --- SHARED UI HELPERS ---

    def _make_panel(self, parent, title: str, subtitle: str = None) -> tk.Frame:
        """Standard white bordered panel helper."""
        panel = tk.Frame(parent, bg="white", bd=1, relief="solid", highlightthickness=0)
        panel.config(highlightbackground=self.colors['border'], highlightcolor=self.colors['border'])

        header_frame = tk.Frame(panel, bg="white")
        header_frame.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(header_frame, text=title, bg="white", fg=self.colors['text_dark'], font=("Arial", 18, "bold")).pack(
            anchor="w")
        if subtitle:
            tk.Label(header_frame, text=subtitle, bg="white", fg=self.colors['text_light'], font=("Arial", 10)).pack(
                anchor="w")

        return panel

    def _create_styled_treeview(self, parent, columns, headings, widths):
        """Creates a modern styled treeview with scrollbars."""
        tree_frame = tk.Frame(parent, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", fieldbackground="white", foreground=self.colors['text_dark'],
                        rowheight=35, font=("Arial", 10))
        style.configure("Treeview.Heading", background="#f8fafc", foreground=self.colors['text_light'],
                        font=("Arial", 10, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[('active', '#e2e8f0')])

        v_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal")

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=v_scroll.set,
                            xscrollcommand=h_scroll.set, style="Treeview")

        v_scroll.config(command=tree.yview)
        h_scroll.config(command=tree.xview)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)

        for key in columns:
            tree.heading(key, text=headings[key], anchor="w")
            tree.column(key, width=widths[key], minwidth=widths[key] // 2, anchor="w")

        return tree

    # --- LOGIN SYSTEM ---

    def _build_login_screen(self):
        """Constructs the initial login/signup screen."""
        self.login_container = tk.Frame(self.root, bg=self.colors["main_bg"])
        self.login_container.pack(fill="both", expand=True)

        signup_frame = tk.Frame(self.login_container, bg="#e2e8f0")
        signup_frame.pack(side="left", fill="both", expand=True)

        signin_frame = tk.Frame(self.login_container, bg="white")
        signin_frame.pack(side="right", fill="both", expand=True)

        tk.Label(signup_frame, text="📚", font=("Arial", 60), bg="#e2e8f0", fg=self.colors['card_blue']).pack(
            pady=(120, 10))
        tk.Label(signup_frame, text="Library System", font=("Arial", 28, "bold"), bg="#e2e8f0",
                 fg=self.colors['text_dark']).pack(pady=(0, 30))

        tk.Label(signup_frame, text="Username", bg="#e2e8f0", fg=self.colors['text_light'],
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=100, pady=(10, 0))
        self.signup_user = tk.StringVar()
        tk.Entry(signup_frame, textvariable=self.signup_user, font=("Arial", 12), width=30, relief="flat",
                 highlightthickness=1, highlightbackground=self.colors['border'], padx=10, pady=8).pack(pady=5)

        tk.Label(signup_frame, text="Password (Min 8 chars)", bg="#e2e8f0", fg=self.colors['text_light'],
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=100, pady=(10, 0))
        self.signup_pass = tk.StringVar()
        tk.Entry(signup_frame, textvariable=self.signup_pass, font=("Arial", 12), width=30, relief="flat",
                 highlightthickness=1, highlightbackground=self.colors['border'], padx=10, pady=8, show="*").pack(
            pady=5)

        tk.Label(signup_frame, text="Account Role", bg="#e2e8f0", fg=self.colors['text_light'],
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=100, pady=(10, 0))
        self.signup_role = tk.StringVar(value="student")
        ttk.Combobox(signup_frame, textvariable=self.signup_role, values=["student", "admin"], state="readonly",
                     font=("Arial", 12), width=28).pack(pady=5)

        tk.Button(signup_frame, text="Sign Up", font=("Arial", 11, "bold"), bg=self.colors['card_green'], fg="white",
                  command=self.handle_signup, width=25, pady=10, relief="flat", cursor="hand2").pack(pady=30)

        tk.Label(signin_frame, text="Welcome Back", font=("Arial", 28, "bold"), bg="white",
                 fg=self.colors['text_dark']).pack(pady=(200, 30))

        tk.Label(signin_frame, text="Username", bg="white", fg=self.colors['text_light'],
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=100, pady=(10, 0))
        self.signin_user = tk.StringVar()
        tk.Entry(signin_frame, textvariable=self.signin_user, font=("Arial", 12), width=30, relief="flat",
                 highlightthickness=1, highlightbackground=self.colors['border'], padx=10, pady=8).pack(pady=5)

        tk.Label(signin_frame, text="Password", bg="white", fg=self.colors['text_light'],
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=100, pady=(10, 0))
        self.signin_pass = tk.StringVar()
        tk.Entry(signin_frame, textvariable=self.signin_pass, font=("Arial", 12), width=30, relief="flat",
                 highlightthickness=1, highlightbackground=self.colors['border'], padx=10, pady=8, show="*").pack(
            pady=5)

        tk.Button(signin_frame, text="Sign In", font=("Arial", 11, "bold"), bg=self.colors['card_blue'], fg="white",
                  command=self.handle_signin, width=25, pady=10, relief="flat", cursor="hand2").pack(pady=30)

    def handle_signup(self):
        """Processing signup attempt."""
        user = self.signup_user.get().strip()
        pwd = self.signup_pass.get().strip()
        role = self.signup_role.get().strip()

        if not user or not pwd:
            messagebox.showerror("Signup Error", "Please fill in all fields.")
            return
        if len(pwd) < 8:
            messagebox.showerror("Signup Error", "Password must be at least 8 characters long.")
            return

        success, msg = self.library.register_user(user, pwd, role)
        if success:
            messagebox.showinfo("Success", "Account created! You can now sign in on the right.")
            self.signup_user.set("")
            self.signup_pass.set("")
        else:
            messagebox.showerror("Error", msg)

    def handle_signin(self):
        """Processing signin attempt."""
        user = self.signin_user.get().strip()
        pwd = self.signin_pass.get().strip()

        success, role = self.library.authenticate_user(user, pwd)
        if success:
            self.current_user = user
            self.current_role = role
            # Setup specific Member object if student logging in
            if role == 'student':
                # Create a default member ID matching username for student ease
                if user not in self.library.members:
                    self.library.register_member(Member(user, user.capitalize()))

            self.login_container.destroy()
            self.launch_main_app()
        else:
            messagebox.showerror("Login Error", "Invalid username or password.")

    # --- LOGOUT SYSTEM ---

    def handle_logout(self):
        """Cleanup current session and return to login screen."""
        if messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
            # Reset application state
            self.current_user = None
            self.current_role = None
            self.screens = {}
            self.signin_user.set("")
            self.signin_pass.set("")

            # Destroy main layout
            if self.main_container:
                self.main_container.destroy()
                self.main_container = None
            if self.sidebar:
                self.sidebar.destroy()
                self.sidebar = None

            # Rebuild login
            self._build_login_screen()

    # --- MAIN APPLICATION SYSTEM ---

    def launch_main_app(self):
        """Initialize main application layout after successful login."""
        self._init_vars()
        self._build_layout()
        self._build_screens()

        # Show initial screen based on role
        if self.current_role == 'admin':
            self._show_screen("home")
        else:
            # Students default to catalog
            self._show_screen("view")

        self.refresh_views()

    def _init_vars(self):
        """Initialize Tk variables for form data."""
        self.book_type_var = tk.StringVar(value="Biology")
        self.book_id_var = tk.StringVar()
        self.book_title_var = tk.StringVar()
        self.book_year_var = tk.StringVar()
        self.book_author_var = tk.StringVar()
        self.book_pages_var = tk.StringVar()

        self.member_id_var = tk.StringVar()
        self.member_name_var = tk.StringVar()

        # Internal processing data (not bound to specific UI entries directly)
        self.transactions = []
        self.sidebar_buttons = {}  # Store refs to update visual state

    def _build_layout(self) -> None:
        """Constructs the sidebar and main content area."""

        # Outer main container to allow easy destruction on logout
        self.main_container = tk.Frame(self.root, bg=self.colors['main_bg'])
        self.main_container.pack(fill="both", expand=True)

        # 1. Sidebar
        self.sidebar = tk.Frame(self.main_container, bg=self.colors['sidebar'], width=260)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # Sidebar Header
        logo_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        logo_frame.pack(fill='x', pady=(25, 30))
        tk.Label(logo_frame, text="📚", font=('Arial', 24), fg=self.colors['card_blue'], bg=self.colors['sidebar']).pack(
            side='left', padx=(25, 10))
        tk.Label(logo_frame, text="LIBRARY MS", font=('Arial', 16, 'bold'), fg='white', bg=self.colors['sidebar']).pack(
            side='left')

        # Sidebar Navigation
        if self.current_role == 'admin':
            nav_items = [
                ("home", "📊 Dashboard", "Dashboard Overview"),
                ("view", "📖 Books Catalog", "Manage books inventory"),
                ("member", "👥 Members", "Library members database"),
                ("report", "📋 Transactions Report", "View all request history"),
                ("scanner", "🔍 Scan Virtual Barcode", "Screen scanning utility"),
                ("settings", "⚙️ Database Actions", "Manual add/delete books")
            ]
        else:
            nav_items = [
                ("view", "📖 Book Catalog", "View available books"),
                ("request", "🔄 Request & Return", "Submit book requests"),
                ("report", "📋 My History", "View your request status")
            ]

        self.sidebar_buttons = {}
        for key, text, subtext in nav_items:
            # Container for grouping main text and subtext
            btn_container = tk.Frame(self.sidebar, bg=self.colors['sidebar'], cursor='hand2')
            btn_container.pack(fill='x', padx=10, pady=4)

            # Indicator line on the left (initially hidden)
            indicator = tk.Frame(btn_container, bg=self.colors['sidebar'], width=4)
            indicator.pack(side='left', fill='y')

            # Text area
            txt_frame = tk.Frame(btn_container, bg=self.colors['sidebar'])
            txt_frame.pack(side='left', fill='both', expand=True, padx=16, pady=12)

            main_lbl = tk.Label(txt_frame, text=text, font=('Arial', 11, 'bold'), fg='#f1f5f9',
                                bg=self.colors['sidebar'], anchor='w')
            main_lbl.pack(fill='x')

            sub_lbl = tk.Label(txt_frame, text=subtext, font=('Arial', 9), fg='#94a3b8', bg=self.colors['sidebar'],
                               anchor='w')
            sub_lbl.pack(fill='x')

            # Store refs to update coloring
            self.sidebar_buttons[key] = {
                'container': btn_container,
                'indicator': indicator,
                'txt_frame': txt_frame,
                'labels': [main_lbl, sub_lbl]
            }

            # Bind click events to the whole container and its children
            def _bind_click(widget, k=key):
                widget.bind("<Button-1>", lambda e: self.nav_click(k))
                for child in widget.winfo_children():
                    _bind_click(child, k)

            _bind_click(btn_container)

        # Quick Actions (Admin Only)
        if self.current_role == 'admin':
            qk_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
            qk_frame.pack(side='bottom', fill='x', pady=(0, 20))
            tk.Label(qk_frame, text="ADMIN SHORTCUTS", font=('Arial', 10, 'bold'), fg='#94a3b8',
                     bg=self.colors['sidebar'], anchor='w').pack(padx=25, pady=(0, 10))

            short_btns = [("➕ Add Book", "add"), ("🗑️ Delete Book", "delete")]
            for txt, target in short_btns:
                tk.Button(qk_frame, text=txt, font=('Arial', 10), bg='#334155', fg='white', relief='flat', bd=0, pady=8,
                          anchor='w', padx=20, cursor='hand2', command=lambda t=target: self._show_screen(t)).pack(
                    fill='x', padx=10, pady=3)

        # Logout Button (Shared)
        logout_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        # Place above quick actions for admin, absolute bottom for student
        if self.current_role == 'student':
            logout_frame.pack(side='bottom', fill='x', pady=20)
        else:
            logout_frame.pack(side='bottom', fill='x', pady=(20, 0))

        logout_btn = tk.Button(logout_frame, text="🚪 Log Out", font=('Arial', 10, 'bold'), bg=self.colors['card_red'],
                               fg='white', relief='flat', bd=0, pady=10, cursor='hand2', command=self.handle_logout)
        logout_btn.pack(fill='x', padx=10)

        # 2. Main Content Area
        self.main_content = tk.Frame(self.main_container, bg=self.colors['main_bg'])
        self.main_content.pack(side='right', fill='both', expand=True)

        # Header (search bar, user profile)
        self.create_header(self.main_content)

        # Content Screen Container (where different panels swap)
        self.content_frame = tk.Frame(self.main_content, bg=self.colors['main_bg'])
        self.content_frame.pack(fill='both', expand=True)

        # Status Bar
        self.status_label = tk.Label(self.main_content, textvariable=self.status_var, anchor="w", bg="#e2e8f0",
                                     fg=self.colors['text_dark'], padx=16, pady=8, font=("Arial", 9))
        self.status_label.pack(side="bottom", fill="x")

    def create_header(self, parent):
        """Standard top header containing search and user info."""
        header = tk.Frame(parent, bg=self.colors['main_bg'], height=100)
        header.pack(fill='x', padx=24, pady=10)
        header.pack_propagate(False)

        # Left: Search Bar
        search_outer = tk.Frame(header, bg=self.colors['main_bg'])
        search_outer.pack(side='left', fill='y')

        self.search_frame = tk.Frame(search_outer, bg='white', highlightthickness=1,
                                     highlightbackground=self.colors['border'])
        self.search_frame.pack(pady=25)

        tk.Label(self.search_frame, text="🔍", font=('Arial', 12), bg='white', fg=self.colors['text_light']).pack(
            side='left', padx=(12, 5))

        self.search_entry = tk.Entry(self.search_frame, font=('Arial', 11), bg='white', bd=0, width=40,
                                     fg=self.colors['text_light'])
        self.search_entry.pack(side='left', padx=5, pady=10)

        # Define placeholder text
        self.placeholder_text = "Search books by title, author, ID..."
        self.search_entry.insert(0, self.placeholder_text)

        # --- FIXED SEARCH PLACEHOLDER SYSTEM ---

        def on_search_focus_in(event):
            """Handle clicking into search bar."""
            self.search_frame.config(highlightbackground=self.colors['card_blue'])  # visual focus
            if self.search_entry.get() == self.placeholder_text:
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(fg=self.colors['text_dark'])  # Dark text when typing

        def on_search_focus_out(event):
            """Handle clicking out of search bar."""
            self.search_frame.config(highlightbackground=self.colors['border'])  # default border
            if not self.search_entry.get().strip():
                self.search_entry.config(fg=self.colors['text_light'])  # gray text
                self.search_entry.insert(0, self.placeholder_text)

        # Bind events for placeholder behavior
        self.search_entry.bind("<FocusIn>", on_search_focus_in)
        self.search_entry.bind("<FocusOut>", on_search_focus_out)

        # Handle Enter key to trigger search
        self.search_entry.bind('<Return>', lambda e: self.perform_search())

        # Right: User Profile
        right_frame = tk.Frame(header, bg=self.colors['main_bg'])
        right_frame.pack(side='right', fill='y')

        user_container = tk.Frame(right_frame, bg=self.colors['main_bg'])
        user_container.pack(pady=20)

        # Notifications (Placeholder)
        tk.Button(user_container, text="🔔", font=('Arial', 14), bg=self.colors['main_bg'], fg=self.colors['text_light'],
                  bd=0, relief='flat', cursor='hand2').pack(side='left', padx=15)

        # Visual divider
        tk.Frame(user_container, bg=self.colors['border'], width=1).pack(side='left', fill='y', padx=10, pady=5)

        # Avatar
        avatar_bg = self.colors['card_green'] if self.current_role == 'admin' else self.colors['card_indigo']
        tk.Label(user_container, text=self.current_user[0].upper(), font=('Arial', 11, 'bold'), bg=avatar_bg,
                 fg='white', width=4, height=2).pack(side='left', padx=(15, 10))

        # User Info
        info_frame = tk.Frame(user_container, bg=self.colors['main_bg'])
        info_frame.pack(side='left', fill='y', padx=(5, 15))

        tk.Label(info_frame, text=self.current_user.capitalize(), font=('Arial', 11, 'bold'),
                 fg=self.colors['text_dark'], bg=self.colors['main_bg'], anchor='w').pack(anchor='w')
        tk.Label(info_frame, text=f"Role: {self.current_role.capitalize()}", font=('Arial', 9),
                 fg=self.colors['text_light'], bg=self.colors['main_bg'], anchor='w').pack(anchor='w')

    def nav_click(self, key):
        """Handle sidebar navigation clicks."""
        # Visual Update of sidebar
        for k, widgets in self.sidebar_buttons.items():
            if k == key:
                # Set Active Visuals
                widgets['container'].config(bg='#334155')  # Slate 700 (darker gray)
                widgets['indicator'].config(bg=self.colors['sidebar_active'])  # Blue indicator
                widgets['txt_frame'].config(bg='#334155')
                widgets['labels'][0].config(fg='white', bg='#334155')  # White main text
                widgets['labels'][1].config(fg='#e2e8f0', bg='#334155')  # Light gray subtext
            else:
                # Set Inactive Visuals
                widgets['container'].config(bg=self.colors['sidebar'])
                widgets['indicator'].config(bg=self.colors['sidebar'])  # Hide indicator
                widgets['txt_frame'].config(bg=self.colors['sidebar'])
                widgets['labels'][0].config(fg='#f1f5f9', bg=self.colors['sidebar'])
                widgets['labels'][1].config(fg='#94a3b8', bg=self.colors['sidebar'])

        # Logical Update
        if key == "scanner":
            self.trigger_screen_scanner()
        else:
            self._show_screen(key)

    def perform_search(self):
        """Execute logic when search entry is submitted."""
        query = self.search_entry.get().strip().lower()
        if not query or query == self.placeholder_text:
            self.status_var.set("Search query is empty.")
            return

        # Navigate to catalog view to show results
        self.nav_click("view")

        # Filter the treeview
        if hasattr(self, "books_tree"):
            for row in self.books_tree.get_children():
                self.books_tree.delete(row)

            count = 0
            for item in self.library.items.values():
                author = getattr(item, 'author', '-').lower()
                title = item.title.lower()

                # Check for match in ID, title, or author
                if query in item.item_id.lower() or query in title or query in author:
                    self.books_tree.insert("", "end", values=(
                        item.item_id,
                        item.get_item_type(),
                        item.title,
                        item.year,
                        getattr(item, 'author', '-'),
                        getattr(item, 'pages', '-'),
                        "Issued" if item.is_borrowed else "Available",
                    ))
                    count += 1

            self.status_var.set(f"Search found {count} results for '{query}'. Click sidebar 'Catalog' to reset.")
            # Shift focus out of search bar so placeholder behavior is triggered properly next time
            self.main_content.focus_set()

            # --- SCREEN SWAPPING SYSTEM ---

    def _build_screens(self) -> None:
        """Preframes all panels but packs none."""
        # Mapping key to constructor function
        screen_map = {
            "home": self._build_home_screen,
            "add": self._build_add_book_screen,
            "view": self._build_view_books_screen,
            "delete": self._build_delete_book_screen,
            "request": self._build_student_request_screen,
            "member": self._build_member_screen,
            "report": self._build_report_screen,
            "settings": self._build_settings_screen,
        }

        # Ensure only relevant screens are built for the role
        admin_screens = ["home", "add", "view", "delete", "member", "report", "settings"]
        student_screens = ["view", "request", "report"]

        valid_screens = admin_screens if self.current_role == 'admin' else student_screens

        for key, constructor in screen_map.items():
            if key in valid_screens:
                frame = constructor()
                self.screens[key] = frame
                frame.pack_forget()  # Initially hidden

    def _show_screen(self, key: str) -> None:
        """Swaps the visible content screen."""
        if key not in self.screens: return

        # Hide all
        for frame in self.screens.values():
            frame.pack_forget()

        # Show selected
        self.screens[key].pack(fill="both", expand=True)
        self.refresh_views()
        self.status_var.set(f"Viewing {key.capitalize()} module.")

    def refresh_views(self) -> None:
        """Global UI refresh pulling latest data from DB and updating open treeviews."""
        # 1. Update underlying data cache
        self.transactions = self.library.get_all_transactions()

        # 2. Update specific UI components if they exist and are open

        # 📚 Admin Dashboard: Student Requests Table
        if hasattr(self, "request_tree") and self.screens["home"].winfo_ismapped():
            for row in self.request_tree.get_children():
                self.request_tree.delete(row)

            # Use specific pending helper
            pending_requests = self.library.get_pending_requests()
            for r in pending_requests:
                # Values map: (ID (hidden), Time, Member, Book, Status)
                # Apply color tag based on design mockup (light blue for pending)
                self.request_tree.insert("", "end", values=(
                    r["id"],
                    r["date"],
                    r["member_name"],
                    r["book_title"],
                    r["status"].upper()
                ), tags=('pending_row',))

            # Update Dashboard Stats Cards
            self._update_metric_cards()

        # 📖 Book Catalog Treeview
        if hasattr(self, "books_tree") and self.screens["view"].winfo_ismapped():
            for row in self.books_tree.get_children():
                self.books_tree.delete(row)

            # Determine if we should show all or just available for students
            source = self.library.items.values()
            if self.current_role == 'student':
                # Student catalog shows books so they can request them
                pass

            for item in source:
                status_text = "Issued" if item.is_borrowed else "Available"
                self.books_tree.insert("", "end", values=(
                    item.item_id,
                    item.get_item_type(),
                    item.title,
                    item.year,
                    getattr(item, 'author', '-'),
                    getattr(item, 'pages', '-'),
                    status_text,
                ), tags=(status_text.lower(),))

        # 🔄 Student Request Form: Update available books combobox
        if hasattr(self, "req_book_combo") and self.screens["request"].winfo_ismapped():
            # Only show available books for requesting
            available_books = [f"{i.item_id} | {i.title}" for i in self.library.items.values() if not i.is_borrowed]
            self.req_book_combo.config(values=available_books)
            if available_books:
                if not self.req_book_id_var.get():
                    self.req_book_combo.current(0)
            else:
                self.req_book_combo.set("No books available")

            # Update physical return combo: Only books borrowed by this student
            my_borrowed_raw = self.library.members[self.current_user].borrowed_item_ids
            my_borrowed_list = []
            for bid in my_borrowed_raw:
                bk = self.library.items.get(bid)
                if bk:
                    my_borrowed_list.append(f"{bid} | {bk.title}")

            if hasattr(self, "return_book_combo"):
                self.return_book_combo.config(values=my_borrowed_list)
                if my_borrowed_list:
                    if not self.return_book_id_var.get():
                        self.return_book_combo.current(0)
                else:
                    self.return_book_combo.set("No books borrowed")

        # 📋 Transactions Report Treeview
        if hasattr(self, "reports_tree") and self.screens["report"].winfo_ismapped():
            for row in self.reports_tree.get_children():
                self.reports_tree.delete(row)

            source = self.transactions
            # Students only see their own history
            if self.current_role == 'student':
                mid = self.current_user
                source = [t for t in self.transactions if
                          self.library.members.get(mid) and t['member'] == self.library.members[mid].name]

            for t in source:
                status_text = t["status"].upper()
                self.reports_tree.insert("", "end", values=(
                    t["date"],
                    t["member"],
                    t["book"],
                    t["type"],
                    status_text
                ), tags=(t["status"].lower(),))

        # 👥 Members List
        if hasattr(self, "members_tree") and self.screens["member"].winfo_ismapped():
            for row in self.members_tree.get_children():
                self.members_tree.delete(row)

            for m in self.library.members.values():
                borrowed_count = len(m.borrowed_item_ids)
                self.members_tree.insert("", "end", values=(
                    m.member_id,
                    m.name,
                    borrowed_count
                ))

    # --- 📊 ADMIN MODULES: DASHBOARD ---

    def _build_home_screen(self) -> tk.Frame:
        """Constructs Admin Dashboard based on mockup design."""
        panel = tk.Frame(self.content_frame, bg=self.colors["main_bg"])
        panel.config(padx=24)  # Internal padding for whole dashboard

        outer_layout = tk.Frame(panel, bg=self.colors["main_bg"])
        outer_layout.pack(fill='both', expand=True, pady=(0, 24))

        # --- Left Area (Metrics & Top Members) ---
        left_area = tk.Frame(outer_layout, bg=self.colors["main_bg"])
        left_area.pack(side='left', fill='both', expand=True, padx=(0, 12))

        # 1. Metric Cards
        self.metric_cards_frame = tk.Frame(left_area, bg=self.colors["main_bg"])
        self.metric_cards_frame.pack(fill='x', pady=(0, 12))
        self._build_metric_cards(self.metric_cards_frame)

        # 2. Top Members Panel
        members_panel = self._make_panel(left_area, "Top Active Members", "Members with most borrowed books")
        members_panel.pack(fill='both', expand=True)
        self._build_top_members_list(members_panel)

        # --- Right Area (Student Requests) ---
        right_area = tk.Frame(outer_layout, bg=self.colors["main_bg"])
        right_area.pack(side='right', fill='both', expand=True, padx=(12, 0))

        # 1. Student Requests Table Panel
        requests_panel = self._make_panel(right_area, "Student Request", "Manage pending book requests from students")
        requests_panel.pack(fill='both', expand=True)
        self._build_student_requests_table(requests_panel)

        return panel

    def _build_metric_cards(self, parent: tk.Frame):
        """Constructs the stylized stat cards."""
        for i in range(4): parent.grid_columnconfigure(i, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self.metric_labels = {}  # Store refs to update numbers

        cards_cfg = [
            ("books", "Total Books", "📚", "white", "#1e293b", "total_books_id"),
            ("borrowed", "Books Borrowed", "📖", "white", self.colors['card_orange'], "borrowed_books_id"),
            ("members", "Active Members", "👥", self.colors['text_dark'], "white", "members_id"),
            # white card with border
            ("pending", "Pending Request", "🔖", self.colors['text_dark'], "white", "pending_id"),
            # white card with border
        ]

        for col, (key, label, icon, fg, bg, _id) in enumerate(cards_cfg):
            card = tk.Frame(parent, bg=bg, bd=1 if bg == "white" else 0, relief="solid")
            if bg == "white": card.config(highlightbackground=self.colors['border'], highlightthickness=1)
            card.grid(row=0, column=col, padx=8, sticky='nsew')

            if col == 0: card.grid(padx=(0, 8))  # remove left padding on first
            if col == 3: card.grid(padx=(8, 0))  # remove right padding on last

            # Interior Layout
            tk.Label(card, text=icon, font=('Arial', 24),
                     fg=fg if fg != self.colors['text_dark'] else self.colors['card_blue'], bg=bg).place(x=20, y=20)

            # Subtext Label
            tk.Label(card, text=label, font=('Arial', 9),
                     fg=fg if fg != self.colors['text_dark'] else self.colors['text_light'], bg=bg, anchor='w').place(
                x=20, y=60, relwidth=0.8)

            # Big Number Label
            num_lbl = tk.Label(card, text="0", font=('Arial', 22, 'bold'), fg=fg, bg=bg, anchor='w')
            num_lbl.place(x=20, y=85, relwidth=0.8)
            self.metric_labels[key] = num_lbl

            if col == 2 or col == 3:
                num_lbl.config(fg=self.colors['text_dark'])

    def _update_metric_cards(self):
        """Calc stats and update numbers in cards."""
        if not hasattr(self, "metric_labels"): return

        total_books = len(self.library.items)
        borrowed_books = sum(1 for b in self.library.items.values() if b.is_borrowed)
        active_members = len(self.library.members)

        # Get count of pending requests specifically
        self.library.cursor.execute("SELECT COUNT(*) FROM transactions WHERE type='Request' AND status='Pending'")
        pending_count = self.library.cursor.fetchone()[0]

        # Update numbers
        self.metric_labels["books"].config(text=f"{total_books:,}")
        self.metric_labels["borrowed"].config(text=f"{borrowed_books:,}")
        self.metric_labels["members"].config(text=f"{active_members:,}")
        self.metric_labels["pending"].config(text=f"{pending_count:,}")

    def _build_student_requests_table(self, parent: tk.Frame):
        """Builds Request Management table with Approve/Reject buttons."""

        # Action Buttons Header
        btns_frame = tk.Frame(parent, bg="white")
        btns_frame.pack(fill="x", padx=24, pady=10)

        tk.Button(btns_frame, text="✅ Approve", font=('Arial', 10, 'bold'), bg=self.colors['card_green'], fg='white',
                  relief='flat', padx=16, pady=8, cursor="hand2", command=self.handle_approve_request).pack(side='left',
                                                                                                            padx=(0,
                                                                                                                  10))
        tk.Button(btns_frame, text="❌ Reject", font=('Arial', 10, 'bold'), bg=self.colors['card_red'], fg='white',
                  relief='flat', padx=16, pady=8, cursor="hand2", command=self.handle_reject_request).pack(side='left')

        # Treeview
        columns = ("id", "time", "member", "book", "status")
        headings = {"id": "ID", "time": "DATE & TIME", "member": "STUDENT NAME", "book": "BOOK TITLE",
                    "status": "STATUS"}
        widths = {"id": 0, "time": 150, "member": 160, "book": 220, "status": 90}

        self.request_tree = self._create_styled_treeview(parent, columns, headings, widths)
        # Hide internal DB ID column
        self.request_tree.column("id", width=0, stretch=tk.NO)

        # Visual Styling for rows based on status (Tags)
        self.request_tree.tag_configure('pending_row', background='#dbeafe',
                                        foreground=self.colors['card_blue'])  # Light blue bg for pending

    def _build_top_members_list(self, parent: tk.Frame):
        """Lists members with highest borrow count."""
        list_container = tk.Frame(parent, bg="white")
        list_container.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        # Minimal styling for a simple list
        tk.Label(list_container, text="Member Name", font=('Arial', 9, 'bold'), fg=self.colors['text_light'],
                 bg='white', anchor='w').grid(row=0, column=1, sticky='w', pady=(0, 10))
        tk.Label(list_container, text="Books Borrowed", font=('Arial', 9, 'bold'), fg=self.colors['text_light'],
                 bg='white', anchor='e').grid(row=0, column=2, sticky='e', pady=(0, 10))

        # Placeholder rows - logic needs dynamic refresh added in refresh_views
        for i in range(1, 5):
            tk.Label(list_container, text="👤", font=('Arial', 11), fg=self.colors['card_blue'], bg='white').grid(row=i,
                                                                                                                 column=0,
                                                                                                                 padx=(
                                                                                                                     0,
                                                                                                                     10),
                                                                                                                 pady=8)
            tk.Label(list_container, text="[Student Name]", font=('Arial', 10), fg=self.colors['text_dark'], bg='white',
                     anchor='w').grid(row=i, column=1, sticky='w')
            tk.Label(list_container, text="0 books", font=('Arial', 10, 'bold'), fg=self.colors['text_dark'],
                     bg='white', anchor='e').grid(row=i, column=2, sticky='e', padx=(20, 0))

            # Bottom border line
            tk.Frame(list_container, bg=self.colors['border'], height=1).grid(row=i, column=0, columnspan=3,
                                                                              sticky='ew', pady=(15, 0))

    # --- ACTION HANDLERS: ADMIN REQUEST MANAGEMENT ---

    def handle_approve_request(self):
        """Handle 'Approve' button click."""
        selected = self.request_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a request to approve.")
            return

        trans_values = self.request_tree.item(selected[0], "values")
        trans_id = trans_values[0]  # Hidden ID
        m_name = trans_values[2]
        b_title = trans_values[3]

        if messagebox.askyesno("Confirm Approval", f"Issue '{b_title}' to {m_name}?"):
            success, msg = self.library.admin_approve_request(trans_id)
            if success:
                self.status_var.set(f"Approved: Book issued.")
                messagebox.showinfo("Success", msg)
                self.refresh_views()
            else:
                messagebox.showerror("Error", msg)

    def handle_reject_request(self):
        """Handle 'Reject' button click."""
        selected = self.request_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a request to reject.")
            return

        trans_values = self.request_tree.item(selected[0], "values")
        trans_id = trans_values[0]
        m_name = trans_values[2]
        b_title = trans_values[3]

        if messagebox.askyesno("Confirm Rejection", f"Reject {m_name}'s request for '{b_title}'?"):
            self.library.admin_reject_request(trans_id)
            self.status_var.set(f"Rejected request for '{b_title}'.")
            messagebox.showinfo("Success", "Request has been rejected. Student will see status update.")
            self.refresh_views()

    # --- 📚 BOOK CATALOG & MANAGEMENT ---

    def _build_view_books_screen(self) -> tk.Frame:
        panel = self._make_panel(self.content_frame, "View Books", "Catalog of all library inventory")

        columns = ("id", "type", "title", "year", "author", "pages", "status")
        headings = {"id": "BOOK ID", "type": "CATEGORY", "title": "BOOK TITLE", "year": "YEAR", "author": "AUTHOR",
                    "pages": "PAGES", "status": "STATUS"}
        widths = {"id": 100, "type": 120, "title": 280, "year": 70, "author": 180, "pages": 70, "status": 100}

        self.books_tree = self._create_styled_treeview(panel, columns, headings, widths)

        # Tags for coloring availability
        self.books_tree.tag_configure('available', foreground=self.colors['card_green'])
        self.books_tree.tag_configure('issued', foreground=self.colors['text_light'])

        # Context Menu / Actions
        btn_frame = tk.Frame(panel, bg="white")
        btn_frame.pack(fill="x", padx=24, pady=(0, 20))

        tk.Button(btn_frame, text="👁️ Show Virtual Barcode", command=self.show_selected_barcode,
                  bg=self.colors['card_indigo'], fg="white", relief="flat", padx=16, pady=8, font=("Arial", 9, "bold"),
                  cursor="hand2").pack(side="left", padx=(0, 10))
        tk.Button(btn_frame, text="📋 Copy Book ID", command=self.copy_selected_id, bg="#f1f5f9",
                  fg=self.colors['text_dark'], relief="flat", padx=16, pady=8, font=("Arial", 9), cursor="hand2").pack(
            side="left")

        return panel

    def copy_selected_id(self):
        selected = self.books_tree.selection()
        if not selected: messagebox.showerror("Error", "Select a book first."); return
        item_id = self.books_tree.item(selected[0], "values")[0]
        self.root.clipboard_clear()
        self.root.clipboard_append(item_id)
        self.status_var.set(f"Copied {item_id} to clipboard.")

    def show_selected_barcode(self):
        """Displays popup with virtual barcode."""
        selected = self.books_tree.selection()
        if not selected: messagebox.showerror("Error", "Select a book first."); return

        item_values = self.books_tree.item(selected[0], "values")
        book_id = item_values[0]
        filepath = f"barcodes/{book_id}.png"

        # Generate if missing
        if not os.path.exists(filepath):
            try:
                generate_local_barcode(book_id)
            except Exception as e:
                messagebox.showerror("Error", f"Barcode generation failed: {e}"); return

        # Popup Window
        popup = tk.Toplevel(self.root)
        popup.title(f"Barcode: {book_id}")
        popup.geometry("400x250")
        popup.configure(bg="white")
        popup.resizable(False, False)

        try:
            img = Image.open(filepath).resize((350, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(popup, image=photo, bg="white")
            lbl.image = photo
            lbl.pack(expand=True, pady=10)
            tk.Label(popup, text=item_values[2], font=("Arial", 10, "bold"), bg="white",
                     fg=self.colors['text_dark']).pack()
            tk.Label(popup, text="Click 'Scan' in sidebar to test screen scanning.", bg="white",
                     fg=self.colors['text_light'], font=("Arial", 8)).pack(pady=(0, 10))
        except Exception:
            tk.Label(popup, text="Could not load barcode image.", bg="white").pack()

    def _build_settings_screen(self) -> tk.Frame:
        """Panel for manual database actions (legacy)."""
        panel = self._make_panel(self.content_frame, "⚙️ Database Actions", "Manual inventory management")
        wrap = tk.Frame(panel, bg="white")
        wrap.pack(anchor="w", padx=24, pady=12)

        tk.Button(wrap, text="➕ Manual Add Book", command=lambda: self._show_screen("add"),
                  bg=self.colors['card_green'], fg="white", relief="flat", padx=20, pady=10, font=("Arial", 9, "bold"),
                  width=25, cursor="hand2").pack(anchor="w", pady=8)
        tk.Button(wrap, text="🗑️ Manual Delete Book", command=lambda: self._show_screen("delete"),
                  bg=self.colors['card_red'], fg="white", relief="flat", padx=20, pady=10, font=("Arial", 9, "bold"),
                  width=25, cursor="hand2").pack(anchor="w", pady=8)

        tk.Frame(panel, bg=self.colors['border'], height=1).pack(fill='x', padx=24, pady=20)

        rtn_wrap = tk.Frame(panel, bg="white")
        rtn_wrap.pack(anchor="w", padx=24, pady=12)
        tk.Label(rtn_wrap, text="Final Audit / Manual Return", font=("Arial", 12, "bold"), bg='white').pack(anchor='w',
                                                                                                            pady=(0,
                                                                                                                  10))
        tk.Label(rtn_wrap, text="Member ID", bg="white").pack(anchor='w')
        self.manual_rtn_mem = tk.Entry(rtn_wrap, width=30)
        self.manual_rtn_mem.pack(anchor='w', pady=5)
        tk.Label(rtn_wrap, text="Book ID", bg="white").pack(anchor='w')
        self.manual_rtn_book = tk.Entry(rtn_wrap, width=30)
        self.manual_rtn_book.pack(anchor='w', pady=5)
        tk.Button(rtn_wrap, text="Process Audit Return", command=self.handle_admin_return,
                  bg=self.colors['card_orange'], fg="white", relief="flat", padx=15, pady=8).pack(pady=10)

        return panel

    def handle_admin_return(self):
        mid = self.manual_rtn_mem.get().strip()
        bid = self.manual_rtn_book.get().strip()
        if not mid or not bid: messagebox.showwarning("Error", "Fill IDs."); return

        ok, msg = self.library.admin_process_return(mid, bid)
        if ok:
            messagebox.showinfo("Success", msg)
            self.manual_rtn_mem.delete(0, tk.END)
            self.manual_rtn_book.delete(0, tk.END)
            self.refresh_views()
        else:
            messagebox.showerror("Error", msg)

    def _build_add_book_screen(self) -> tk.Frame:
        """Manual Add Book Form."""
        panel = self._make_panel(self.content_frame, "Add Book", "Enter book details or use camera scan")
        form = tk.Frame(panel, bg="white")
        form.pack(anchor="w", padx=24, pady=10)

        # Style Combobox for type
        style = ttk.Style()
        style.configure("Form.TCombobox", padding=5, font=("Arial", 10))

        fields = [
            ("Category",
             ttk.Combobox(form, textvariable=self.book_type_var, values=list(BOOK_TYPES.keys()), state="readonly",
                          style="Form.TCombobox", width=33)),
            ("Book ID / ISBN",
             tk.Entry(form, textvariable=self.book_id_var, width=35, font=("Arial", 10), relief="solid", bd=1,
                      highlightthickness=0)),
            ("Title",
             tk.Entry(form, textvariable=self.book_title_var, width=35, font=("Arial", 10), relief="solid", bd=1,
                      highlightthickness=0)),
            ("Year", tk.Entry(form, textvariable=self.book_year_var, width=35, font=("Arial", 10), relief="solid", bd=1,
                              highlightthickness=0)),
            ("Author",
             tk.Entry(form, textvariable=self.book_author_var, width=35, font=("Arial", 10), relief="solid", bd=1,
                      highlightthickness=0)),
            ("Pages",
             tk.Entry(form, textvariable=self.book_pages_var, width=35, font=("Arial", 10), relief="solid", bd=1,
                      highlightthickness=0))
        ]

        # Hack to apply padding/colors to tk.Entry within mapping
        entry_style = {"relief": "flat", "highlightthickness": 1, "highlightbackground": self.colors['border'],
                       "padx": 10, "pady": 7, "font": ("Arial", 10)}

        for row, (label, widget) in enumerate(fields):
            tk.Label(form, text=label, bg="white", fg=self.colors['text_dark'], font=("Arial", 9, "bold")).grid(row=row,
                                                                                                                column=0,
                                                                                                                sticky="w",
                                                                                                                pady=10,
                                                                                                                padx=(0,
                                                                                                                      20))
            if isinstance(widget, tk.Entry):
                widget.config(**entry_style)
            widget.grid(row=row, column=1, sticky="w", pady=10)

        # Action Buttons
        btn_frame = tk.Frame(panel, bg="white")
        btn_frame.pack(anchor="w", padx=24, pady=(15, 25))

        tk.Button(btn_frame, text="✅ Save Book to Inventory", command=self.add_book, bg=self.colors['card_green'],
                  fg="white", relief="flat", padx=16, pady=10, font=("Arial", 9, "bold"), cursor="hand2").pack(
            side="left", padx=(0, 15))
        tk.Button(btn_frame, text="📷 Auto-Fill via WebCam Scan", command=self.trigger_scanner,
                  bg=self.colors['card_blue'], fg="white", relief="flat", padx=16, pady=10, font=("Arial", 9),
                  cursor="hand2").pack(side="left")
        return panel

    def trigger_scanner(self):
        """Launches webcam scanner to autofill form."""
        self.status_var.set("Opening webcam... hold a physical barcode to the camera.")
        self.root.update()
        isbn, title, author = scan_and_fetch_book()

        if isbn and title:
            self.book_id_var.set(isbn)
            self.book_title_var.set(title)
            self.book_author_var.set(author)
            self.status_var.set(f"Successfully scanned '{title}'.")
            messagebox.showinfo("Scanner", f"Found book: {title}. Please complete Category, Year, and Pages manually.")
        elif isbn:
            self.book_id_var.set(isbn)
            self.status_var.set("Scanned ISBN, but details not found online.")
        else:
            self.status_var.set("Scan cancelled or failed.")

    def add_book(self) -> None:
        item_id = self.book_id_var.get().strip()
        title = self.book_title_var.get().strip()
        year_raw = self.book_year_var.get().strip()
        author = self.book_author_var.get().strip()
        pages_raw = self.book_pages_var.get().strip()

        if not all([item_id, title, year_raw, author, pages_raw]):
            messagebox.showerror("Error", "Please fill in all book fields.");
            return

        try:
            year = int(year_raw)
            pages = int(pages_raw)
        except ValueError:
            messagebox.showerror("Error", "Year and pages must be numbers.");
            return

        book_class = BOOK_TYPES[self.book_type_var.get()]
        book = book_class(item_id, title, year, author, pages)

        if not self.library.add_item(book):
            messagebox.showerror("Error", "Book ID already exists in inventory.");
            return

        # Generate barcode automatically
        try:
            generate_local_barcode(item_id)
        except Exception:
            pass

        # Clear form
        self.book_id_var.set("")
        self.book_title_var.set("")
        self.book_year_var.set("")
        self.book_author_var.set("")
        self.book_pages_var.set("")
        self.refresh_views()
        self.status_var.set(f"Added book {item_id}.")
        messagebox.showinfo("Success", f"'{title}' added successfully.")

    def _build_delete_book_screen(self) -> tk.Frame:
        """Manual Delete Form."""
        panel = self._make_panel(self.content_frame, "Delete Book", "Remove a book permanently from inventory")
        wrap = tk.Frame(panel, bg="white")
        wrap.pack(anchor="w", padx=24, pady=12)

        tk.Label(wrap, text="Enter Book ID to delete", bg="white", fg=self.colors['text_dark'],
                 font=("Arial", 9, "bold")).pack(anchor='w', pady=(0, 5))
        entry_id = tk.Entry(wrap, width=35, relief="flat", highlightthickness=1,
                            highlightbackground=self.colors['border'], padx=10, pady=7)
        entry_id.pack(anchor='w', pady=5)

        tk.Button(wrap, text="🗑️ Delete Book", command=lambda: self.delete_book(entry_id), bg=self.colors['card_red'],
                  fg="white", relief="flat", padx=16, pady=9, font=("Arial", 9, "bold"), cursor="hand2").pack(
            anchor="w", pady=15)
        return panel

    def delete_book(self, entry_widget) -> None:
        book_id = entry_widget.get().strip()
        if not book_id: messagebox.showerror("Error", "Enter a book ID."); return

        # Confirmation
        book = self.library.items.get(book_id)
        b_title = book.title if book else "this book"
        if not messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to permanently delete '{b_title}' (ID: {book_id})?"):
            return

        ok, message = self.library.delete_item(book_id)
        if not ok:
            messagebox.showerror("Delete Failed", message)
        else:
            entry_widget.delete(0, tk.END)
            self.refresh_views()
            self.status_var.set(f"Deleted book {book_id}.")
            messagebox.showinfo("Success", message)

    # --- 👥 MEMBERS MANAGEMENT (ADMIN) ---

    def _build_member_screen(self) -> tk.Frame:
        """Admin Member Management Screen."""
        panel = self._make_panel(self.content_frame, "Members Database", "View registered library members")

        # Form to add new manual member
        form = self._make_panel(panel, "Register New Member (Manual)", "Add member not linked to user account")
        form.pack(fill='x', padx=24, pady=(10, 20))

        entry_frame = tk.Frame(form, bg="white")
        entry_frame.pack(fill='x', padx=24, pady=(0, 20))

        entry_style = {"relief": "flat", "highlightthickness": 1, "highlightbackground": self.colors['border'],
                       "padx": 10, "pady": 7}

        tk.Label(entry_frame, text="Member ID", bg="white", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky='w')
        self.new_mem_id = tk.Entry(entry_frame, width=30, **entry_style)
        self.new_mem_id.grid(row=1, column=0, sticky='w', pady=(5, 0), padx=(0, 20))

        tk.Label(entry_frame, text="Full Name", bg="white", font=("Arial", 9, "bold")).grid(row=0, column=1, sticky='w')
        self.new_mem_name = tk.Entry(entry_frame, width=35, **entry_style)
        self.new_mem_name.grid(row=1, column=1, sticky='w', pady=(5, 0))

        tk.Button(form, text="👤 Register Member", command=self.add_manual_member, bg=self.colors['card_green'],
                  fg="white", relief="flat", padx=16, pady=10, font=("Arial", 9, "bold")).pack(anchor='w', padx=24,
                                                                                               pady=(0, 24))

        # Members Table
        list_panel = self._make_panel(panel, "Member List")
        list_panel.pack(fill='both', expand=True, padx=24, pady=(0, 20))

        columns = ("id", "name", "borrowed")
        headings = {"id": "MEMBER ID", "name": "FULL NAME", "borrowed": "BOOKS ON HAND"}
        widths = {"id": 150, "name": 300, "borrowed": 120}
        self.members_tree = self._create_styled_treeview(list_panel, columns, headings, widths)

        return panel

    def add_manual_member(self):
        mid = self.new_mem_id.get().strip()
        name = self.new_mem_name.get().strip()
        if not mid or not name: messagebox.showerror("Error", "Fill IDs."); return

        if self.library.register_member(Member(mid, name)):
            messagebox.showinfo("Success", f"Registered {name}.")
            self.new_mem_id.delete(0, tk.END)
            self.new_mem_name.delete(0, tk.END)
            self.refresh_views()
        else:
            messagebox.showerror("Error", "ID exists.")

    # --- 📋 REPORTS (SHARED) ---

    def _build_report_screen(self) -> tk.Frame:
        """Shared Transaction History Screen."""
        title = "Transaction Reports" if self.current_role == 'admin' else "My Request History"
        panel = self._make_panel(self.content_frame, title, "Log of all book requests, borrows, and returns")

        columns = ("date", "member", "book", "type", "status")
        headings = {"date": "DATE & TIME", "member": "STUDENT NAME", "book": "BOOK TITLE", "type": "TYPE",
                    "status": "STATUS"}
        widths = {"date": 160, "member": 180, "book": 280, "type": 100, "status": 100}
        self.reports_tree = self._create_styled_treeview(panel, columns, headings, widths)

        # Tags for coloring statuses in report
        style = ttk.Style()
        self.reports_tree.tag_configure('pending', foreground=self.colors['status_pending'])
        self.reports_tree.tag_configure('rejected', foreground=self.colors['status_rejected'])
        self.reports_tree.tag_configure('active', foreground=self.colors['status_active'], font=("Arial", 10, "bold"))
        self.reports_tree.tag_configure('done', foreground=self.colors['status_done'])

        return panel

    # --- 🔍 SCREEN SCANNER UTILITY (ADMIN) ---

    def trigger_screen_scanner(self):
        """Attempts to scan screen for virtual barcodes."""
        self.status_var.set("Scanning screen for barcodes...")
        self.root.update()
        scanned_id = scan_screen_for_barcode()

        if scanned_id:
            book = self.library.items.get(scanned_id)
            if book:
                self.nav_click("view")  # Highlight catalog
                info = (
                    f"📖 Book Identified!\n\nTitle: {book.title}\nAuthor: {getattr(book, 'author', 'Unknown')}\nStatus: {'Borrowed' if book.is_borrowed else 'Available'}\n\n(ID: {scanned_id})")
                messagebox.showinfo("Screen Scanner", info)
                self.status_var.set(f"Successfully identified {book.title} from screen.")
            else:
                messagebox.showwarning("Scanner Result",
                                       f"Scanned valid ID '{scanned_id}' but it's not in the database.")
                self.status_var.set("Scanned unknown barcode.")
        else:
            messagebox.showerror("Scanner Error",
                                 "No barcode detected on your screen.\n\nMake sure a barcode window is open and fully visible.")
            self.status_var.set("Screenshot scan failed.")

    # --- 🔄 STUDENT MODULES: REQUEST & RETURN ---

    def _build_student_request_screen(self) -> tk.Frame:
        """Student panel to request available books or return borrowed ones."""
        panel = tk.Frame(self.content_frame, bg=self.colors["main_bg"])
        panel.config(padx=24)

        # Configure Grid
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_columnconfigure(1, weight=1)

        # --- Left: Request Form ---
        req_panel = self._make_panel(panel, "📝 Request a Book", "Select an available book to borrow")
        req_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 12), pady=(0, 24))

        form_frame = tk.Frame(req_panel, bg="white")
        form_frame.pack(fill='both', expand=True, padx=24, pady=(10, 24))

        tk.Label(form_frame, text="Select Book from Catalog", bg="white", font=("Arial", 10, "bold")).pack(anchor='w',
                                                                                                           pady=(0, 5))
        self.req_book_id_var = tk.StringVar()
        self.req_book_combo = ttk.Combobox(form_frame, textvariable=self.req_book_id_var, state="readonly",
                                           font=("Arial", 10))
        self.req_book_combo.pack(fill='x', pady=(0, 15))

        tk.Button(form_frame, text="📤 Submit Borrow Request", command=self.handle_student_request,
                  bg=self.colors['card_blue'], fg="white", relief="flat", padx=20, pady=12,
                  font=("Arial", 10, "bold")).pack(anchor='w', pady=10)

        # --- Right: Return Form ---
        rtn_panel = self._make_panel(panel, "📚 Return a Book", "Select a book you currently have to return")
        rtn_panel.grid(row=0, column=1, sticky='nsew', padx=(12, 0), pady=(0, 24))

        rtn_form = tk.Frame(rtn_panel, bg="white")
        rtn_form.pack(fill='both', expand=True, padx=24, pady=(10, 24))

        tk.Label(rtn_form, text="Your Currently Borrowed Books", bg="white", font=("Arial", 10, "bold")).pack(
            anchor='w', pady=(0, 5))
        self.return_book_id_var = tk.StringVar()
        self.return_book_combo = ttk.Combobox(rtn_form, textvariable=self.return_book_id_var, state="readonly",
                                              font=("Arial", 10))
        self.return_book_combo.pack(fill='x', pady=(0, 15))

        tk.Button(rtn_form, text="📥 Mark for Return", command=self.handle_student_return, bg=self.colors['card_orange'],
                  fg="white", relief="flat", padx=20, pady=12, font=("Arial", 10, "bold")).pack(anchor='w', pady=10)

        return panel

    def handle_student_request(self):
        raw_val = self.req_book_id_var.get()
        if not raw_val or raw_val == "No books available":
            messagebox.showwarning("Warning", "Please select a book.");
            return

        # Extract ID from "ID | Title" string
        book_id = raw_val.split(" | ")[0]
        student_id = self.current_user

        success, msg = self.library.student_request_book(student_id, book_id)
        if success:
            messagebox.showinfo("Success", f"{msg}\n\nPlease check 'My History' for approval status.")
            self.refresh_views()
            self.nav_click("report")  # Show them history automatically
        else:
            messagebox.showerror("Request Failed", msg)

    def handle_student_return(self):
        raw_val = self.return_book_id_var.get()
        if not raw_val or raw_val == "No books borrowed":
            messagebox.showwarning("Warning", "Please select a book.");
            return

        book_id = raw_val.split(" | ")[0]
        bk = self.library.items.get(book_id)
        b_title = bk.title if bk else "book"

        # Initiate Return
        success, msg = self.library.student_request_book(self.current_user,
                                                         book_id)  # Reuse request mechanism, it handles physical return call internally if status allows, or admin processes
        # Currently, logic requires admin to process actual return audit.
        # Student marks for return.

        # Simplified: Student initiates, log updated, admin processes later.
        if messagebox.askyesno("Confirm Return", f"Are you physically returning '{b_title}' now?"):
            # For this prototype, we'll log it as a request type 'Return', status 'Pending'
            self.library.log_transaction(self.current_user, book_id, "Return Request", "Pending")
            messagebox.showinfo("Return Pending",
                                "Return request submitted. Please return book to front desk. Admin will audit and close transaction.")
            self.refresh_views()
            self.nav_click("report")


def run() -> None:
    root = tk.Tk()
    style = ttk.Style(root)
    # Configure Combobox global style slightly for padding
    style.map('TCombobox', fieldbackground=[('readonly', 'white')])

    app = LibraryApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()