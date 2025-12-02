import os
import sys
import json
import re
from typing import Dict, List, Set
from PyPDF2 import PdfReader, PdfWriter

def load_missing_ids(geojson_path: str) -> Set[str]:
    if not os.path.isfile(geojson_path):
        print(f"GeoJSON not found: {geojson_path}")
        return set()

    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    all_ids = set()
    for feat in features:
        props = feat.get("properties") or {}
        val = props.get("ID")
        if val:
            all_ids.add(str(val).strip())
    
    # Check existing folders
    existing = set()
    for item in os.listdir('.'):
        if os.path.isdir(item):
            existing.add(item)
            
    missing = all_ids - existing
    print(f"Total IDs: {len(all_ids)}, Existing folders: {len(existing)}, Missing: {len(missing)}")
    return missing

def build_id_pattern(ids: Set[str]) -> re.Pattern:
    if not ids:
        return None
    # Sort by length descending to match longer IDs first if there are overlaps (though IDs seem fixed length)
    sorted_ids = sorted(list(ids), key=len, reverse=True)
    escaped = [re.escape(i) for i in sorted_ids]
    # Batching for regex performance? With 3000 IDs, one regex might be slow or hit limits.
    # But let's try one big regex first.
    pattern_str = "(" + "|".join(escaped) + ")"
    return re.compile(pattern_str)

def extract_from_pdf(pdf_path: str, target_ids: Set[str]) -> Set[str]:
    print(f"Scanning {pdf_path} for {len(target_ids)} IDs...")
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"Error opening {pdf_path}: {e}")
        return set()

    num_pages = len(reader.pages)
    pattern = build_id_pattern(target_ids)
    if not pattern:
        return set()

    id_pages: Dict[str, List[int]] = {}
    
    # Optimization: Read text page by page
    for idx in range(num_pages):
        if idx % 100 == 0:
            print(f"  Processing page {idx+1}/{num_pages}...", flush=True)
        
        try:
            page = reader.pages[idx]
            text = page.extract_text() or ""
        except:
            continue
            
        if not text:
            continue
            
        found = set(pattern.findall(text))
        for fid in found:
            if fid not in id_pages:
                id_pages[fid] = []
            id_pages[fid].append(idx + 1)

    found_ids = set(id_pages.keys())
    print(f"Found {len(found_ids)} IDs in {pdf_path}")

    if not found_ids:
        return set()

    # Write folders
    for fid, pages in id_pages.items():
        pages = sorted(list(set(pages)))
        id_dir = fid
        os.makedirs(id_dir, exist_ok=True)
        
        # Write txt
        with open(os.path.join(id_dir, f"{fid}.txt"), "w", encoding="utf-8") as f:
            for p in pages:
                f.write(f"{p}\n")
            f.write("/end\n")
            
        # Write PDF
        writer = PdfWriter()
        for p in pages:
            writer.add_page(reader.pages[p-1])
            
        with open(os.path.join(id_dir, f"{fid}.pdf"), "wb") as f:
            writer.write(f)
            
    return found_ids

def main():
    geojson_path = 'vdq-zonagemunicipalzones.geojson.json'
    missing_ids = load_missing_ids(geojson_path)
    
    if not missing_ids:
        print("No missing IDs to process.")
        return

    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    # Prioritize large regulation files
    priority = ["R.C.A.3V.Q.4_compressed.pdf", "ccq2022p1_20221031_FINAL_FRE_NOV7_BOOKMARKS.pdf"]
    
    sorted_pdfs = []
    for p in priority:
        if p in pdf_files:
            sorted_pdfs.append(p)
            pdf_files.remove(p)
    sorted_pdfs.extend(pdf_files)
    
    print(f"PDF processing order: {sorted_pdfs}")

    for pdf_file in sorted_pdfs:
        if not missing_ids:
            print("All IDs found!")
            break
            
        found = extract_from_pdf(pdf_file, missing_ids)
        missing_ids -= found
        print(f"Remaining missing IDs: {len(missing_ids)}")

if __name__ == "__main__":
    main()
