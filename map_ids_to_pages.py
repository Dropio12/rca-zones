import os
import sys
import json
import re
from typing import Dict, List, Set

from PyPDF2 import PdfReader, PdfWriter


def load_ids_from_geojson(geojson_path: str) -> List[str]:
    """Load unique ID values from a GeoJSON FeatureCollection.

    Expects each feature to have properties["ID"]. Adjust if your key is different.
    """
    if not os.path.isfile(geojson_path):
        raise FileNotFoundError(f"GeoJSON file not found: {geojson_path}")

    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    ids: Set[str] = set()

    for feat in features:
        props = feat.get("properties") or {}
        value = props.get("ID")
        if value is None:
            continue
        # Ensure string and strip whitespace
        ids.add(str(value).strip())

    return sorted(ids)


def build_id_pattern(ids: List[str]) -> re.Pattern:
    """Build a regex that matches any of the IDs as substrings.

    We intentionally *do not* use word boundaries because in the PDF text
    some IDs are glued to preceding words (e.g. "bâtiment31005Ha").
    """
    if not ids:
        raise ValueError("No IDs found in GeoJSON.")

    # Escape IDs for regex and join them
    escaped = [re.escape(i) for i in ids]
    pattern_str = "(" + "|".join(escaped) + ")"
    return re.compile(pattern_str)


def map_ids_to_pdf_pages(ids: List[str], pdf_path: str) -> Dict[str, List[int]]:
    """Return a mapping ID -> sorted list of 1-based page numbers where the ID appears."""
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    pattern = build_id_pattern(ids)
    id_pages: Dict[str, List[int]] = {i: [] for i in ids}

    print(f"Scanning {num_pages} pages for {len(ids)} IDs...")

    for idx in range(num_pages):
        page_num = idx + 1  # 1-based page numbers
        page = reader.pages[idx]
        try:
            text = page.extract_text() or ""
        except Exception as e:
            print(f"Warning: could not extract text from page {page_num}: {e}")
            continue

        if not text:
            continue

        # Find all distinct IDs that appear on this page
        found_here = set(pattern.findall(text))
        if not found_here:
            continue

        for found_id in found_here:
            id_pages[found_id].append(page_num)

    # Sort page lists
    for i in id_pages:
        id_pages[i] = sorted(set(id_pages[i]))

    return id_pages


def write_zones_file(ids: List[str], output_root: str = ".") -> str:
    """Write zones.txt listing every ID (one per line) and return its path."""
    zones_path = os.path.join(output_root, "zones.txt")
    with open(zones_path, "w", encoding="utf-8") as f:
        for id_value in ids:
            f.write(f"{id_value}\n")
    print(f"Wrote {len(ids)} IDs to {zones_path}")
    return zones_path


def write_id_folders(id_pages: Dict[str, List[int]], pdf_path: str, output_root: str = ".") -> None:
    """Create a folder per ID (only if it appears in the PDF), a [ID].txt listing page numbers,
    and a [ID].pdf containing those pages.

    Text file format example:
        928
        1054
        /end
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    reader = PdfReader(pdf_path)

    for id_value, pages in id_pages.items():
        if not pages:
            # Skip IDs that never appear in the PDF; zones.txt will still list them.
            continue

        id_dir = os.path.join(output_root, id_value)
        os.makedirs(id_dir, exist_ok=True)

        # Write the text file with page numbers
        txt_path = os.path.join(id_dir, f"{id_value}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            for p in pages:
                f.write(f"{p}\n")
            f.write("/end\n")

        # Write a PDF containing those pages
        writer = PdfWriter()
        for p in pages:
            # pages are 1-based indices
            writer.add_page(reader.pages[p - 1])

        pdf_out_path = os.path.join(id_dir, f"{id_value}.pdf")
        with open(pdf_out_path, "wb") as f_out:
            writer.write(f_out)

        print(f"ID {id_value}: {len(pages)} page(s) -> {txt_path}, {pdf_out_path}")


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python map_ids_to_pages.py <geojson_path> <pdf_path>")
        sys.exit(1)

    geojson_path = sys.argv[1]
    pdf_path = sys.argv[2]

    ids = load_ids_from_geojson(geojson_path)
    if not ids:
        print("No IDs found in GeoJSON (properties['ID']).")
        sys.exit(1)

    print(f"Loaded {len(ids)} unique IDs from {geojson_path}")

    # Always write zones.txt with every ID, regardless of PDF matches
    write_zones_file(ids, output_root=".")

    id_pages = map_ids_to_pdf_pages(ids, pdf_path)
    write_id_folders(id_pages, pdf_path=pdf_path, output_root=".")


if __name__ == "__main__":
    main()
