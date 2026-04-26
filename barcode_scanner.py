import cv2
from pyzbar.pyzbar import decode
import requests
import time

def fetch_book_data(isbn):
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
    cap = cv2.VideoCapture(0)
    scanned_isbn = None
    scanned_title = None
    scanned_author = None

    while True:
        ret, frame = cap.read()
        if not ret: break

        barcodes = decode(frame)

        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            if barcode_type in ['EAN13', 'ISBN13', 'ISBN10', 'CODE128']:
                if barcode_type == 'CODE128':
                    # Directly return the ID if it's our local generated barcode
                    scanned_isbn = barcode_data
                    scanned_title = f"Local Book (ID: {barcode_data})"
                    scanned_author = "Local Catalog"

                    cv2.putText(frame, f"Found Local: {barcode_data}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.imshow("Book Barcode Scanner", frame)
                    cv2.waitKey(1000)
                    break
                else:
                    cv2.putText(frame, "Fetching data...", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    cv2.imshow("Book Barcode Scanner", frame)
                    cv2.waitKey(1)

                    title, author = fetch_book_data(barcode_data)
                    if title:
                        scanned_isbn = barcode_data
                        scanned_title = title
                        scanned_author = author
                        cv2.putText(frame, f"Found: {title}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.imshow("Book Barcode Scanner", frame)
                        cv2.waitKey(1000)
                        break

        if scanned_isbn: break

        cv2.imshow("Book Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27: break
        if cv2.getWindowProperty("Book Barcode Scanner", cv2.WND_PROP_VISIBLE) < 1: break

    cap.release()
    cv2.destroyAllWindows()

    return scanned_isbn, scanned_title, scanned_author