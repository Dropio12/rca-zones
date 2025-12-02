import os
import re
import sys
from collections import defaultdict
from PyPDF2 import PdfReader, PdfWriter

# Pattern for zone codes like 31005HA (5 digits + 2 uppercase letters).
# Adjust this if your zone codes look different.
ZONE_PATTERN = re.compile(r"\b\d{5}[a-zA-Z]{2}\b")


def find_zones_in_text(text: str):
    if not text:
        return []
    return ZONE_PATTERN.findall(text)


def split_pdf_by_zone(pdf_path: str, output_root: str = "zones"):
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    # Map zone -> list of page indices
    zone_pages = defaultdict(list)
    # Map zone -> concatenated text
    zone_texts = defaultdict(list)

    print(f"Scanning {num_pages} pages for zones...")

    for idx in range(num_pages):
        page = reader.pages[idx]
        try:
            text = page.extract_text() or ""
        except Exception as e:
            print(f"Warning: could not extract text from page {idx + 1}: {e}")
            text = ""

        zones_found = find_zones_in_text(text)

        if not zones_found:
            # No zone on this page – skip or handle differently if needed
            continue

        # If multiple zones appear on a page, attach the page to all of them
        for zone in zones_found:
            zone_pages[zone].append(idx)
            zone_texts[zone].append(f"\n\n--- Page {idx + 1} ---\n{text}")

    if not zone_pages:
        print("No zones found in document with the given pattern.")
        return

    os.makedirs(output_root, exist_ok=True)

    for zone, pages in zone_pages.items():
        zone_dir = os.path.join(output_root, zone)
        os.makedirs(zone_dir, exist_ok=True)

        # Create PDF for this zone
        writer = PdfWriter()
        for page_idx in pages:
            writer.add_page(reader.pages[page_idx])

        zone_pdf_path = os.path.join(zone_dir, f"{zone}.pdf")
        with open(zone_pdf_path, "wb") as f:
            writer.write(f)

        # Create rules.txt – all extracted text for that zone
        rules_txt_path = os.path.join(zone_dir, "rules.txt")
        with open(rules_txt_path, "w", encoding="utf-8") as f:
            f.write("".join(zone_texts[zone]))

        print(f"Zone {zone}:")
        print(f"  Pages: {[p + 1 for p in pages]}")
        print(f"  PDF:   {zone_pdf_path}")
        print(f"  Rules: {rules_txt_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python split_zones.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.isfile(pdf_path):
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    output_dir = sys.argv[2] if len(sys.argv) > 2 else "zones"
    split_pdf_by_zone(pdf_path, output_dir)


if __name__ == "__main__":
    main()
