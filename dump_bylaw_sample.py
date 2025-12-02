import sys
from PyPDF2 import PdfReader

def dump_start(pdf_path, pages=20):
    reader = PdfReader(pdf_path)
    text = []
    for i in range(min(pages, len(reader.pages))):
        text.append(f"--- PAGE {i+1} ---")
        text.append(reader.pages[i].extract_text())
    
    with open("bylaw_sample.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(text))
    print("Dumped sample to bylaw_sample.txt")

if __name__ == "__main__":
    dump_start("R.C.A.3V.Q.4_compressed.pdf")
