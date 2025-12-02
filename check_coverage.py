import json
import os

def check_coverage():
    geojson_path = 'vdq-zonagemunicipalzones.geojson.json'
    
    if not os.path.exists(geojson_path):
        print(f"Error: {geojson_path} not found.")
        return

    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = data.get('features', [])
    ids = set()
    for feat in features:
        props = feat.get('properties') or {}
        val = props.get('ID')
        if val:
            ids.add(str(val).strip())

    print(f"Total unique IDs in GeoJSON: {len(ids)}")

    missing_folders = []
    missing_pdfs = []
    found_count = 0

    for zone_id in ids:
        folder_path = zone_id
        pdf_path = os.path.join(zone_id, f"{zone_id}.pdf")

        if not os.path.isdir(folder_path):
            missing_folders.append(zone_id)
        elif not os.path.isfile(pdf_path):
            missing_pdfs.append(zone_id)
        else:
            found_count += 1

    print(f"Zones with valid folder and PDF: {found_count}")
    print(f"Missing folders: {len(missing_folders)}")
    print(f"Folders found but missing PDF: {len(missing_pdfs)}")

    if missing_folders:
        print("\nExample missing folders (first 10):")
        for i in missing_folders[:10]:
            print(i)
    
    if missing_pdfs:
        print("\nExample missing PDFs (first 10):")
        for i in missing_pdfs[:10]:
            print(i)

if __name__ == "__main__":
    check_coverage()
