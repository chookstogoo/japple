from models.library_item import LibraryItem


class HistoryBook(LibraryItem):
    def __init__(self, item_id: str, title: str, year: int, author: str, pages: int) -> None:
        super().__init__(item_id, title, year)
        self.author = author
        self.pages = pages

    def get_item_type(self) -> str:
        return "History"

    def get_details(self) -> str:
        return f"Author: {self.author}, Pages: {self.pages}"
