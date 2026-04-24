import sqlite3
from models.library_item import LibraryItem
from models.member import Member

# Import all book types so the database can rebuild them
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

        # 1. Connect to SQLite (Creates library.db file in your PyCharm folder)
        self.conn = sqlite3.connect("library.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

        # 2. Build the database structure if it's the first time running
        self._setup_db()

        # 3. Load all saved data from the database into your existing dictionaries
        self._load_data()

    def _setup_db(self):
        """Creates the tables if they don't exist yet."""
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS books (item_id TEXT PRIMARY KEY, type TEXT, title TEXT, year INTEGER, author TEXT, pages INTEGER, is_borrowed INTEGER)''')
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS members (member_id TEXT PRIMARY KEY, name TEXT, borrowed_ids TEXT)''')

        # Create a default admin so you don't get locked out
        self.cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users VALUES ('admin', 'password123', 'admin')")
        self.conn.commit()

    def _load_data(self):
        """Pulls data from SQLite into the dictionaries so the UI works normally."""
        # Load Users
        for row in self.cursor.execute("SELECT username, password, role FROM users"):
            self.users[row[0]] = {"password": row[1], "role": row[2]}

        # Load Books
        for row in self.cursor.execute("SELECT item_id, type, title, year, author, pages, is_borrowed FROM books"):
            book_type = row[1]
            book_class = BOOK_CLASSES.get(book_type, LibraryItem)  # Grab the correct class
            book = book_class(row[0], row[2], row[3], row[4], row[5])
            if row[6] == 1:
                book.is_borrowed = True
            self.items[row[0]] = book

        # Load Members
        for row in self.cursor.execute("SELECT member_id, name, borrowed_ids FROM members"):
            member = Member(row[0], row[1])
            if row[2]:  # If they have borrowed books, convert the comma string back to a list
                member.borrowed_item_ids = row[2].split(",")
            self.members[row[0]] = member

    def register_user(self, username, password, role) -> tuple[bool, str]:
        if username in self.users:
            return False, "Username already exists."

        # Save to DB
        self.cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, role))
        self.conn.commit()

        # Save to Dictionary
        self.users[username] = {"password": password, "role": role}
        return True, "Account created successfully."

    def authenticate_user(self, username, password) -> tuple[bool, str]:
        if username in self.users and self.users[username]["password"] == password:
            return True, self.users[username]["role"]
        return False, None

    def add_item(self, item: LibraryItem) -> bool:
        if item.item_id in self.items:
            return False

        book_type = item.get_item_type()

        # Save to DB
        self.cursor.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (item.item_id, book_type, item.title, item.year, getattr(item, 'author', ''),
                             getattr(item, 'pages', 0), 0))
        self.conn.commit()

        # Save to Dictionary
        self.items[item.item_id] = item
        return True

    def register_member(self, member: Member) -> bool:
        if member.member_id in self.members:
            return False

        # Save to DB
        self.cursor.execute("INSERT INTO members VALUES (?, ?, ?)", (member.member_id, member.name, ""))
        self.conn.commit()

        # Save to Dictionary
        self.members[member.member_id] = member
        return True

    def borrow_item(self, member_id: str, item_id: str) -> tuple[bool, str]:
        member = self.members.get(member_id)
        item = self.items.get(item_id)

        if member is None: return False, "Member not found."
        if item is None: return False, "Item not found."
        if not item.borrow(): return False, "Item is already borrowed."

        member.borrow_item(item_id)

        # Update DB for both the book and the member
        self.cursor.execute("UPDATE books SET is_borrowed = 1 WHERE item_id = ?", (item_id,))
        borrowed_str = ",".join(member.borrowed_item_ids)
        self.cursor.execute("UPDATE members SET borrowed_ids = ? WHERE member_id = ?", (borrowed_str, member_id))
        self.conn.commit()

        return True, f"{member.name} borrowed '{item.title}'."

    def return_item(self, member_id: str, item_id: str) -> tuple[bool, str]:
        member = self.members.get(member_id)
        item = self.items.get(item_id)

        if member is None: return False, "Member not found."
        if item is None: return False, "Item not found."
        if not member.return_item(item_id): return False, "This member did not borrow the item."
        if not item.return_item(): return False, "Item was not marked as borrowed."

        # Update DB for both the book and the member
        self.cursor.execute("UPDATE books SET is_borrowed = 0 WHERE item_id = ?", (item_id,))
        borrowed_str = ",".join(member.borrowed_item_ids)
        self.cursor.execute("UPDATE members SET borrowed_ids = ? WHERE member_id = ?", (borrowed_str, member_id))
        self.conn.commit()

        return True, f"{member.name} returned '{item.title}'."

    def list_items(self) -> list[str]:
        return [str(item) for item in self.items.values()]

    def list_members(self) -> list[str]:
        return [str(member) for member in self.members.values()]

    def delete_item(self, item_id: str) -> tuple[bool, str]:
        item = self.items.get(item_id)
        if item is None:
            return False, "Item not found."

        # Delete from DB
        self.cursor.execute("DELETE FROM books WHERE item_id = ?", (item_id,))

        for member in self.members.values():
            if item_id in member.borrowed_item_ids:
                member.borrowed_item_ids.remove(item_id)

                # Sync the deleted borrow state back to the DB
                borrowed_str = ",".join(member.borrowed_item_ids)
                self.cursor.execute("UPDATE members SET borrowed_ids = ? WHERE member_id = ?",
                                    (borrowed_str, member.member_id))

        self.conn.commit()
        del self.items[item_id]
        return True, "Item deleted successfully."