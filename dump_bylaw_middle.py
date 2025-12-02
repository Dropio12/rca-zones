import sys
from PyPDF2 import PdfReader

def dump_middle(pdf_path, start_page=50, num_pages=10):
    reader = PdfReader(pdf_path)
    text = []
    for i in range(start_page, min(start_page + num_pages, len(reader.pages))):
        text.append(f"--- PAGE {i+1} ---")
        text.append(reader.pages[i].extract_text())
    
    with open("bylaw_sample_middle.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(text))
    print("Dumped middle sample to bylaw_sample_middle.txt")

if __name__ == "__main__":
    dump_middle("R.C.A.3V.Q.4_compressed.pdf")
