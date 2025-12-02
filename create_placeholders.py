import os
import json
from PyPDF2 import PdfWriter, PdfReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_simple_pdf(path, text):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(100, 750, text)
    can.save()
    packet.seek(0)
    
    with open(path, 'wb') as f:
        f.write(packet.getbuffer())

def create_placeholders():
    geojson_path = 'vdq-zonagemunicipalzones.geojson.json'
    
    if not os.path.exists(geojson_path):
        print("GeoJSON not found")
        return

    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = data.get('features', [])
    all_ids = set()
    for feat in features:
        props = feat.get('properties') or {}
        val = props.get('ID')
        if val:
            all_ids.add(str(val).strip())

    existing = set()
    for item in os.listdir('.'):
        if os.path.isdir(item):
            existing.add(item)
            
    missing = all_ids - existing
    print(f"Missing IDs: {len(missing)}")
    
    if not missing:
        print("All zones have folders.")
        return

    print("Creating placeholders...")
    count = 0
    for zone_id in missing:
        os.makedirs(zone_id, exist_ok=True)
        pdf_path = os.path.join(zone_id, f"{zone_id}.pdf")
        if not os.path.exists(pdf_path):
            try:
                create_simple_pdf(pdf_path, f"Information for Zone {zone_id} is currently unavailable.")
                count += 1
            except Exception as e:
                print(f"Error creating PDF for {zone_id}: {e}")
                
    print(f"Created {count} placeholder folders/PDFs.")

if __name__ == "__main__":
    create_placeholders()
