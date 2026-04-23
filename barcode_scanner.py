import cv2
from pyzbar.pyzbar import decode
import requests


def fetch_book_data(isbn):
    """Fetch book details from Open Library using the ISBN"""
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        key = f"ISBN:{isbn}"

        if key in data:
            book = data[key]
            title = book.get("title", "Unknown Title")

            # Extract authors if available
            authors_data = book.get("authors", [])
            authors = [author["name"] for author in authors_data]
            author_str = ", ".join(authors) if authors else "Unknown Author"

            return title, author_str
    except Exception as e:
        print(f"Network error: {e}")

    return None, None


def run_scanner():
    """Launch the webcam, scan barcodes, and overlay graphical data"""
    cap = cv2.VideoCapture(0)
    print("Starting webcam... Hold a book barcode up to the camera.")
    print("Press 'q' on your keyboard to close the scanner.")

    last_scanned_isbn = None
    display_title = ""
    display_author = ""

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Check your webcam.")
            break

        # Decode any barcodes in the current frame
        barcodes = decode(frame)

        for barcode in barcodes:
            # 1. Draw a graphical bounding box around the barcode
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            # 2. Decode the raw data
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            # 3. If it's a new barcode, query the API
            if barcode_data != last_scanned_isbn:
                print(f"Scanned {barcode_type}: {barcode_data}")
                last_scanned_isbn = barcode_data

                # Book barcodes are typically EAN13 or ISBN13/ISBN10 formats
                if barcode_type in ['EAN13', 'ISBN13', 'ISBN10']:
                    title, author = fetch_book_data(barcode_data)
                    if title:
                        display_title = title
                        display_author = author
                    else:
                        display_title = "Book not found in database"
                        display_author = f"ISBN: {barcode_data}"
                else:
                    display_title = f"Unknown Format: {barcode_type}"
                    display_author = barcode_data

            # 4. Create graphical text overlays above the barcode
            # We add a slight black shadow/outline to make the text readable against any background
            cv2.putText(frame, display_title, (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4)
            cv2.putText(frame, display_title, (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            if display_author:
                cv2.putText(frame, display_author, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
                cv2.putText(frame, display_author, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Render the live feed
        cv2.imshow("Book Barcode Scanner", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up hardware resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_scanner()