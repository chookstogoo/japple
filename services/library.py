import sqlite3
import os
from datetime import datetime
from models.library_item import LibraryItem
from models.member import Member

from models.biology_book import BiologyBook
from models.chemistry_book import ChemistryBook
from models.engineering_book import EngineeringBook
from models.history_book import HistoryBook
from models.mathematics_book import MathematicsBook
from models.physics_book import PhysicsBook

BOOK_CLASSES = {
    "Biology": BiologyBook,
    "Chemistry": ChemistryBook,
    "Engineering": EngineeringBook,
    "History": HistoryBook,
    "Mathematics": MathematicsBook,
    "Physics": PhysicsBook,
}


class Library:
    def __init__(self, name: str) -> None:
        self.name = name
        self.items: dict[str, LibraryItem] = {}
        self.members: dict[str, Member] = {}
        self.users = {}

        self.conn = sqlite3.connect("library.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

        self._setup_db()
        self._load_data()

    def _setup_db(self):
        # Setup basic tables
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS books (item_id TEXT PRIMARY KEY, type TEXT, title TEXT, year INTEGER, author TEXT, pages INTEGER, is_borrowed INTEGER)''')
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS members (member_id TEXT PRIMARY KEY, name TEXT, borrowed_ids TEXT)''')

        # Define transaction statuses: 'Pending', 'Active', 'Rejected', 'Done'
        # New transactions table schema tracking specific IDs
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                member_id TEXT,
                                member_name TEXT, 
                                book_id TEXT,
                                book_title TEXT, 
                                type TEXT, 
                                date TEXT, 
                                status TEXT)''')

        # Create default admin if not exists
        self.cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users VALUES ('admin', 'password123', 'admin')")

        # Migrate old "member" roles to "student"
        self.cursor.execute("UPDATE users SET role='student' WHERE role='member'")
        self.conn.commit()

    def _load_data(self):
        # Load Users
        for row in self.cursor.execute("SELECT username, password, role FROM users"):
            self.users[row[0]] = {"password": row[1], "role": row[2]}

        # Load Books
        for row in self.cursor.execute("SELECT item_id, type, title, year, author, pages, is_borrowed FROM books"):
            book_type = row[1]
            book_class = BOOK_CLASSES.get(book_type, LibraryItem)
            book = book_class(row[0], row[2], row[3], row[4], row[5])
            if row[6] == 1:
                book.is_borrowed = True
            self.items[row[0]] = book

        # Load Members
        for row in self.cursor.execute("SELECT member_id, name, borrowed_ids FROM members"):
            member = Member(row[0], row[1])
            if row[2]:
                member.borrowed_item_ids = row[2].split(",")
            self.members[row[0]] = member

    # --- UPDATED TRANSACTION HANDLERS ---

    def get_all_transactions(self):
        """Returns all transactions, sorted by date."""
        transactions = []
        for row in self.cursor.execute(
                "SELECT id, member_name, book_title, type, date, status FROM transactions ORDER BY id DESC"):
            transactions.append(
                {"id": row[0], "member": row[1], "book": row[2], "type": row[3], "date": row[4], "status": row[5]})
        return transactions

    def get_pending_requests(self):
        """Returns only pending 'Request' transactions."""
        requests = []
        # Join with books and members table to get IDs easily for processing
        query = """
            SELECT t.id, t.member_id, m.name, t.book_id, b.title, t.date, t.status
            FROM transactions t
            JOIN members m ON t.member_id = m.member_id
            JOIN books b ON t.book_id = b.item_id
            WHERE t.type = 'Request' AND t.status = 'Pending'
            ORDER BY t.id ASC
        """
        for row in self.cursor.execute(query):
            requests.append({
                "id": row[0],
                "member_id": row[1],
                "member_name": row[2],
                "book_id": row[3],
                "book_title": row[4],
                "date": row[5],
                "status": row[6]
            })
        return requests

    def log_transaction(self, member_id, book_id, t_type, status, date=None):
        """Internal helper to log any library transaction."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        member = self.members.get(member_id)
        book = self.items.get(book_id)

        m_name = member.name if member else "Unknown Member"
        b_title = book.title if book else "Unknown Book"

        self.cursor.execute("""INSERT INTO transactions 
                               (member_id, member_name, book_id, book_title, type, date, status) 
                               VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (member_id, m_name, book_id, b_title, t_type, date, status))
        self.conn.commit()

    # --- ADMIN WORKFLOW MANAGEMENT ---

    def student_request_book(self, member_id, book_id) -> tuple[bool, str]:
        """A student initiates a book request."""
        member = self.members.get(member_id)
        book = self.items.get(book_id)

        if not member: return False, "Member ID not found."
        if not book: return False, "Book ID not found."
        if book.is_borrowed: return False, "Book is currently unavailable."

        # Check if student already has a pending request for this specific book
        self.cursor.execute("SELECT id FROM transactions WHERE member_id=? AND book_id=? AND status='Pending'",
                            (member_id, book_id))
        if self.cursor.fetchone():
            return False, "You already have a pending request for this book."

        # Log as 'Pending'
        self.log_transaction(member_id, book_id, "Request", "Pending")
        return True, "Request submitted successfully."

    def admin_reject_request(self, transaction_id) -> bool:
        """Admin rejects a pending student request."""
        self.cursor.execute("UPDATE transactions SET status='Rejected' WHERE id=?", (transaction_id,))
        self.conn.commit()
        return True

    def admin_approve_request(self, transaction_id) -> tuple[bool, str]:
        """Admin approves request, initiating the borrow process."""
        # 1. Get the details of the transaction
        self.cursor.execute("SELECT member_id, book_id FROM transactions WHERE id=? AND status='Pending'",
                            (transaction_id,))
        row = self.cursor.fetchone()
        if not row: return False, "Transaction not found or not pending."

        mem_id, bk_id = row[0], row[1]

        # 2. Perform physical borrow
        success, msg = self.borrow_item(mem_id, bk_id)

        if success:
            # 3. If physically borrowed, update workflow status to 'Active' (Issued)
            self.cursor.execute("UPDATE transactions SET status='Active' WHERE id=?", (transaction_id,))
            self.conn.commit()
            return True, "Request approved. Book issued."
        else:
            return False, msg

    def admin_process_return(self, member_id, book_id) -> tuple[bool, str]:
        """Final return processing by Admin. Sets status to 'Done'."""

        # 1. Perform physical return
        success, msg = self.return_item(member_id, book_id)

        if success:
            # 2. Look for the corresponding active transaction entry to mark workflow as 'Done'
            self.cursor.execute(
                "UPDATE transactions SET status='Done' WHERE member_id=? AND book_id=? AND status='Active'",
                (member_id, book_id))
            self.conn.commit()
            return True, "Book successfully returned and audited."
        else:
            return False, msg

    # --- CORE LIBRARY OPERATIONS (MODIFIED LOGGING) ---

    def register_user(self, username, password, role) -> tuple[bool, str]:
        if username in self.users:
            return False, "Username already exists."
        self.cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, role))
        self.conn.commit()
        self.users[username] = {"password": password, "role": role}
        return True, "Account created successfully."

    def authenticate_user(self, username, password) -> tuple[bool, str]:
        if username in self.users and self.users[username]["password"] == password:
            return True, self.users[username]["role"]
        return False, None

    def add_item(self, item: LibraryItem) -> bool:
        if item.item_id in self.items: return False
        book_type = item.get_item_type()
        self.cursor.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (item.item_id, book_type, item.title, item.year, getattr(item, 'author', ''),
                             getattr(item, 'pages', 0), 0))
        self.conn.commit()
        self.items[item.item_id] = item
        return True

    def register_member(self, member: Member) -> bool:
        if member.member_id in self.members: return False
        self.cursor.execute("INSERT INTO members VALUES (?, ?, ?)", (member.member_id, member.name, ""))
        self.conn.commit()
        self.members[member.member_id] = member
        return True

    def borrow_item(self, member_id: str, item_id: str) -> tuple[bool, str]:
        """Updates internal state and DB for physical borrowing."""
        member = self.members.get(member_id)
        item = self.items.get(item_id)
        if member is None: return False, "Member not found."
        if item is None: return False, "Item not found."
        if not item.borrow(): return False, "Item is already borrowed."

        member.borrow_item(item_id)
        self.cursor.execute("UPDATE books SET is_borrowed = 1 WHERE item_id = ?", (item_id,))
        borrowed_str = ",".join(member.borrowed_item_ids)
        self.cursor.execute("UPDATE members SET borrowed_ids = ? WHERE member_id = ?", (borrowed_str, member_id))
        self.conn.commit()
        return True, f"{member.name} physically borrowed '{item.title}'."

    def return_item(self, member_id: str, item_id: str) -> tuple[bool, str]:
        """Updates internal state and DB for physical returning."""
        member = self.members.get(member_id)
        item = self.items.get(item_id)
        if member is None: return False, "Member not found."
        if item is None: return False, "Item not found."
        if not member.return_item(item_id): return False, "This member did not borrow the item."
        if not item.return_item(): return False, "Item was not marked as borrowed."

        self.cursor.execute("UPDATE books SET is_borrowed = 0 WHERE item_id = ?", (item_id,))
        borrowed_str = ",".join(member.borrowed_item_ids)
        self.cursor.execute("UPDATE members SET borrowed_ids = ? WHERE member_id = ?", (borrowed_str, member_id))
        self.conn.commit()
        return True, f"{member.name} physically returned '{item.title}'."

    def delete_item(self, item_id: str) -> tuple[bool, str]:
        item = self.items.get(item_id)
        if item is None: return False, "Item not found."
        if item.is_borrowed: return False, "Cannot delete borrowed book. Return it first."

        self.cursor.execute("DELETE FROM books WHERE item_id = ?", (item_id,))
        # Cleanup associated virtual barcodes
        try:
            os.remove(f"barcodes/{item_id}.png")
        except FileNotFoundError:
            pass

        self.conn.commit()
        del self.items[item_id]
        return True, "Item deleted successfully."