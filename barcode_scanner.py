import cv2
from pyzbar.pyzbar import decode
import requests
import time


def fetch_book_data(isbn):
    """Fetch book details from Open Library using the ISBN"""
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        key = f"ISBN:{isbn}"

        if key in data:
            book = data[key]
            title = book.get("title", "")
            authors_data = book.get("authors", [])
            authors = [author["name"] for author in authors_data]
            author_str = ", ".join(authors) if authors else "Unknown Author"
            return title, author_str
    except Exception as e:
        print(f"Network error: {e}")

    return None, None


def scan_and_fetch_book():
    """Opens the webcam, reads one valid book barcode, and returns the data"""
    cap = cv2.VideoCapture(0)
    scanned_isbn = None
    scanned_title = None
    scanned_author = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        barcodes = decode(frame)

        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            if barcode_type in ['EAN13', 'ISBN13', 'ISBN10']:
                # Show loading text
                cv2.putText(frame, "Fetching data...", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.imshow("Book Barcode Scanner", frame)
                cv2.waitKey(1)  # Force UI update before the network request freezes it

                title, author = fetch_book_data(barcode_data)

                if title:
                    scanned_isbn = barcode_data
                    scanned_title = title
                    scanned_author = author

                    # Show success graphics briefly before closing
                    cv2.putText(frame, f"Found: {title}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow("Book Barcode Scanner", frame)
                    cv2.waitKey(1000)  # Pause for 1 second so the user sees it worked
                    break

        if scanned_isbn:
            break  # Exit the while loop if we successfully got a book

        cv2.imshow("Book Barcode Scanner", frame)

        # Allow manual exit with 'q' or 'Esc'
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

        # Safely exit if the user clicks the 'X' on the OpenCV window
        if cv2.getWindowProperty("Book Barcode Scanner", cv2.WND_PROP_VISIBLE) < 1:
            break

    # Clean up hardware resources safely
    cap.release()
    cv2.destroyAllWindows()

    return scanned_isbn, scanned_title, scanned_author