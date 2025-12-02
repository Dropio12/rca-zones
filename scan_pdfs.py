import os
import json
import re
from PyPDF2 import PdfReader

def load_ids_from_geojson(geojson_path):
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    features = data.get("features", [])
    ids = set()
    for feat in features:
        props = feat.get("properties") or {}
        val = props.get("ID")
        if val:
            ids.add(str(val).strip())
    return ids

def build_id_pattern(ids):
    escaped = [re.escape(i) for i in ids]
    pattern_str = "(" + "|".join(escaped) + ")"
    return re.compile(pattern_str)

def scan_pdfs():
    geojson_path = 'vdq-zonagemunicipalzones.geojson.json'
    if not os.path.exists(geojson_path):
        print("GeoJSON not found")
        return

    all_ids = load_ids_from_geojson(geojson_path)
    print(f"Total IDs: {len(all_ids)}")

    # Check which ones are already done
    existing_folders = set()
    for item in os.listdir('.'):
        if os.path.isdir(item) and item in all_ids:
            existing_folders.add(item)
    
    missing_ids = all_ids - existing_folders
    print(f"Missing IDs: {len(missing_ids)}")
    
    if not missing_ids:
        print("All IDs have folders!")
        return

    # Find all PDFs
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF files.")

    # Build pattern for missing IDs only (optimization)
    pattern = build_id_pattern(missing_ids)

    matches = {} # pdf -> count of found missing IDs

    for pdf_file in pdf_files:
        print(f"Scanning {pdf_file}...")
        try:
            reader = PdfReader(pdf_file)
            found_in_pdf = set()
            for page in reader.pages:
                try:
                    text = page.extract_text() or ""
                    found = pattern.findall(text)
                    found_in_pdf.update(found)
                except:
                    pass
            
            if found_in_pdf:
                matches[pdf_file] = len(found_in_pdf)
                print(f"  Found {len(found_in_pdf)} missing IDs in {pdf_file}")
                # Optional: print some found IDs
                # print(list(found_in_pdf)[:5])
            else:
                print(f"  No missing IDs found in {pdf_file}")
        except Exception as e:
            print(f"  Error reading {pdf_file}: {e}")

    print("\nSummary of potential recoveries:")
    for pdf, count in matches.items():
        print(f"{pdf}: {count}")

if __name__ == "__main__":
    scan_pdfs()
