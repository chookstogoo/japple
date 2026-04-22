from abc import ABC, abstractmethod


class LibraryItem(ABC):
    """Abstract base class for all library items."""

    def __init__(self, item_id: str, title: str, year: int) -> None:
        self.item_id = item_id
        self.title = title
        self.year = year
        self.is_borrowed = False

    def borrow(self) -> bool:
        if self.is_borrowed:
            return False
        self.is_borrowed = True
        return True

    def return_item(self) -> bool:
        if not self.is_borrowed:
            return False
        self.is_borrowed = False
        return True

    @abstractmethod
    def get_item_type(self) -> str:
        pass

    @abstractmethod
    def get_details(self) -> str:
        pass

    def __str__(self) -> str:
        status = "Borrowed" if self.is_borrowed else "Available"
        return (
            f"[{self.get_item_type()}] {self.item_id} - {self.title} "
            f"({self.year}) | {self.get_details()} | {status}"
        )
