import sqlite3


def export_to_text():
    # Connect to your saved database
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # Open a new text file to write into
    with open("database_dump.txt", "w", encoding="utf-8") as f:
        f.write("=== LIBRARY SYSTEM DATABASE TEXT DUMP ===\n\n")

        # 1. Get the Users
        f.write("--- TABLE: users ---\n")
        f.write("Format: (Username, Password, Role)\n")
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            f.write(f"{row}\n")

        # 2. Get the Books
        f.write("\n--- TABLE: books ---\n")
        f.write("Format: (ID, Type, Title, Year, Author, Pages, BorrowedStatus)\n")
        cursor.execute("SELECT * FROM books")
        for row in cursor.fetchall():
            f.write(f"{row}\n")

        # 3. Get the Members
        f.write("\n--- TABLE: members ---\n")
        f.write("Format: (ID, Name, BorrowedItemIDs)\n")
        cursor.execute("SELECT * FROM members")
        for row in cursor.fetchall():
            f.write(f"{row}\n")

    print("Success! Open 'database_dump.txt' in PyCharm to see your data.")
    conn.close()


if __name__ == "__main__":
    export_to_text()