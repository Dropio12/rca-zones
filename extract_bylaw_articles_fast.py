import re
import json
from PyPDF2 import PdfReader
from typing import List, Dict

def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    full_text = []
    print(f"Processing {len(reader.pages)} pages (Full Mode)...")
    for i, page in enumerate(reader.pages):
        # if i >= 50: break  <-- REMOVED LIMIT
        if i % 50 == 0:
            print(f"  Page {i}...")
        text = page.extract_text()
        if text:
            full_text.append(text)
    return "\n".join(full_text)

def clean_text(text: str) -> str:
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if re.match(r'^\d+$', line.strip()):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def split_into_articles(text: str) -> List[Dict[str, str]]:
    # Same regex as before
    pattern = re.compile(r'\n(\d+)\.\s')
    parts = pattern.split(text)
    
    articles = []
    if parts[0].strip():
        articles.append({
            "id": "preamble",
            "text": parts[0].strip()
        })
    
    for i in range(1, len(parts), 2):
        article_num = parts[i]
        article_text = parts[i+1]
        articles.append({
            "id": article_num,
            "text": article_text.strip()
        })
        
    return articles

def main():
    pdf_path = "R.C.A.3V.Q.4_compressed.pdf"
    print(f"Extracting text from {pdf_path} (Fast Mode)...")
    raw_text = extract_text_from_pdf(pdf_path)
    
    print("Cleaning text...")
    cleaned_text = clean_text(raw_text)
    
    print("Splitting into articles...")
    articles = split_into_articles(cleaned_text)
    
    print(f"Found {len(articles)} articles.")
    
    with open("bylaw_articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print("Saved to bylaw_articles.json")

if __name__ == "__main__":
    main()
