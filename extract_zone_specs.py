import os
import sys
import json
import pdfplumber
from tabulate import tabulate
from typing import Dict, List, Any

def extract_tables_from_pdf(pdf_path: str) -> List[str]:
    """
    Extracts tables from a PDF using pdfplumber and converts them to Markdown strings.
    """
    extracted_tables = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract tables with default settings
                tables = page.extract_tables()
                for table in tables:
                    # Clean up None values and newlines
                    clean_table = []
                    for row in table:
                        clean_row = [
                            (cell.strip().replace('\n', ' ') if cell else "") for cell in row
                        ]
                        clean_table.append(clean_row)
                    
                    if clean_table:
                        # Convert to Markdown
                        md_table = tabulate(clean_table, tablefmt="github")
                        extracted_tables.append(md_table)
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        
    return extracted_tables

def process_zone(zone_id: str, root_dir: str = "."):
    zone_dir = os.path.join(root_dir, zone_id)
    pdf_path = os.path.join(zone_dir, f"{zone_id}.pdf")
    
    if not os.path.isfile(pdf_path):
        print(f"PDF not found for zone {zone_id}: {pdf_path}")
        return

    print(f"Processing Zone {zone_id}...")
    tables = extract_tables_from_pdf(pdf_path)
    
    if not tables:
        print(f"  No tables found in {pdf_path}")
        return

    # Save to spec.json
    output_path = os.path.join(zone_dir, "spec.json")
    data = {
        "zone_id": zone_id,
        "source_file": f"{zone_id}.pdf",
        "tables": tables  # Now a list of Markdown strings
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  Saved {len(tables)} tables to {output_path}")

def main():
    if len(sys.argv) > 1:
        # Process specific zones provided as args
        for zone_id in sys.argv[1:]:
            process_zone(zone_id)
    else:
        # Process all directories that look like zones
        # (Assuming directories matching the ID pattern or just all subdirs with a matching PDF)
        root = "."
        for item in os.listdir(root):
            if os.path.isdir(item):
                # Check if it looks like a zone folder (has ID.pdf)
                pdf_path = os.path.join(root, item, f"{item}.pdf")
                if os.path.isfile(pdf_path):
                    process_zone(item)

if __name__ == "__main__":
    main()
