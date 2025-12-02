import re
import json
import pdfplumber
from typing import List, Dict

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text from PDF, ignoring headers/footers roughly."""
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Crop header/footer if needed, but for now just extract raw text
            # We might get page numbers, but we can clean them later
            text = page.extract_text()
            if text:
                full_text.append(text)
    return "\n".join(full_text)

def clean_text(text: str) -> str:
    """Removes page numbers and common footer noise."""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove standalone page numbers (e.g. "51")
        if re.match(r'^\d+$', line.strip()):
            continue
        # Remove the historical citation lines if desired, or keep them.
        # They look like: "2010, R.C.A.3V.Q. 4, a. 79."
        # Let's keep them as they are part of the text, but maybe mark them?
        # Actually, they are fine.
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def split_into_articles(text: str) -> List[Dict[str, str]]:
    """Splits text into articles based on 'Number. ' pattern."""
    # Pattern: Start of line, digits, dot, space.
    # We use capturing group for the number.
    # We need to be careful not to match "1. " inside a list (e.g. 1° is fine, but 1. might happen?)
    # In this text, lists use "1°", "a)", etc. So "1. " is likely an Article.
    
    # However, "1." might appear in other contexts. 
    # But looking at the dump, Articles are strictly "79. ", "80. ".
    
    pattern = re.compile(r'\n(\d+)\.\s')
    
    parts = pattern.split(text)
    # parts[0] is preamble (before Article 1)
    # parts[1] is number of first match (e.g. "1")
    # parts[2] is text of first match
    # parts[3] is number of second match...
    
    articles = []
    
    # Handle preamble if needed, but usually we skip to Article 1.
    if parts[0].strip():
        articles.append({
            "id": "preamble",
            "text": parts[0].strip()
        })
    
    # Iterate in pairs (number, text)
    for i in range(1, len(parts), 2):
        article_num = parts[i]
        article_text = parts[i+1]
        
        # The text might contain the next split point at the end, but re.split handles that.
        # We just need to clean up the text.
        
        articles.append({
            "id": article_num,
            "text": article_text.strip()
        })
        
    return articles

def main():
    pdf_path = "R.C.A.3V.Q.4_compressed.pdf"
    print(f"Extracting text from {pdf_path}...")
    raw_text = extract_text_from_pdf(pdf_path)
    
    print("Cleaning text...")
    cleaned_text = clean_text(raw_text)
    
    print("Splitting into articles...")
    articles = split_into_articles(cleaned_text)
    
    print(f"Found {len(articles)} articles.")
    
    # Save to JSON
    with open("bylaw_articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print("Saved to bylaw_articles.json")

if __name__ == "__main__":
    main()
