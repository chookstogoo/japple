import os
import barcode
from barcode.writer import ImageWriter
from PIL import ImageGrab
from pyzbar.pyzbar import decode


def generate_local_barcode(item_id):
    """Generates a Code128 barcode and saves it to a local folder"""
    os.makedirs("barcodes", exist_ok=True)
    Code128 = barcode.get_barcode_class('code128')

    # Generate and save the image
    generated_barcode = Code128(item_id, writer=ImageWriter())
    filename = f"barcodes/{item_id}"
    generated_barcode.save(filename)

    return f"{filename}.png"


def scan_screen_for_barcode():
    """Takes a screenshot of your laptop monitor and searches it for barcodes"""
    print("Capturing screen...")
    screen = ImageGrab.grab()

    # Decode any barcodes found in the screenshot
    barcodes = decode(screen)

    for b in barcodes:
        data = b.data.decode("utf-8")
        print(f"Detected Virtual ID: {data}")
        return data

    print("No barcodes detected on screen.")
    return None