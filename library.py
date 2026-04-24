from models.library_item import LibraryItem
from models.member import Member


class Library:
    def __init__(self, name: str) -> None:
        self.name = name
        self.items: dict[str, LibraryItem] = {}
        self.members: dict[str, Member] = {}

        # User Authentication Storage
        self.users = {}
        # Create a default fallback admin so you don't get locked out
        self.users["admin"] = {"password": "password123", "role": "admin"}

    def register_user(self, username, password, role) -> tuple[bool, str]:
        if username in self.users:
            return False, "Username already exists."
        self.users[username] = {"password": password, "role": role}
        return True, "Account created successfully."

    def authenticate_user(self, username, password) -> tuple[bool, str]:
        if username in self.users and self.users[username]["password"] == password:
            return True, self.users[username]["role"]
        return False, None

    def add_item(self, item: LibraryItem) -> bool:
        if item.item_id in self.items:
            return False
        self.items[item.item_id] = item
        return True

    def register_member(self, member: Member) -> bool:
        if member.member_id in self.members:
            return False
        self.members[member.member_id] = member
        return True

    def borrow_item(self, member_id: str, item_id: str) -> tuple[bool, str]:
        member = self.members.get(member_id)
        item = self.items.get(item_id)

        if member is None:
            return False, "Member not found."
        if item is None:
            return False, "Item not found."
        if not item.borrow():
            return False, "Item is already borrowed."

        member.borrow_item(item_id)
        return True, f"{member.name} borrowed '{item.title}'."

    def return_item(self, member_id: str, item_id: str) -> tuple[bool, str]:
        member = self.members.get(member_id)
        item = self.items.get(item_id)

        if member is None:
            return False, "Member not found."
        if item is None:
            return False, "Item not found."
        if not member.return_item(item_id):
            return False, "This member did not borrow the item."
        if not item.return_item():
            return False, "Item was not marked as borrowed."

        return True, f"{member.name} returned '{item.title}'."

    def list_items(self) -> list[str]:
        return [str(item) for item in self.items.values()]

    def list_members(self) -> list[str]:
        return [str(member) for member in self.members.values()]

    def delete_item(self, item_id: str) -> tuple[bool, str]:
        item = self.items.get(item_id)
        if item is None:
            return False, "Item not found."

        for member in self.members.values():
            if item_id in member.borrowed_item_ids:
                member.borrowed_item_ids.remove(item_id)

        del self.items[item_id]
        return True, "Item deleted successfully."