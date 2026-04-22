class Member:
    def __init__(self, member_id: str, name: str) -> None:
        self.member_id = member_id
        self.name = name
        self.borrowed_item_ids: list[str] = []

    def borrow_item(self, item_id: str) -> None:
        self.borrowed_item_ids.append(item_id)

    def return_item(self, item_id: str) -> bool:
        if item_id not in self.borrowed_item_ids:
            return False
        self.borrowed_item_ids.remove(item_id)
        return True

    def __str__(self) -> str:
        return (
            f"Member {self.member_id} - {self.name} | "
            f"Borrowed items: {len(self.borrowed_item_ids)}"
        )
