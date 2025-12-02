import os
import json
import sys
import re
from typing import List, Dict

# Force UTF-8 output for Windows consoles
sys.stdout.reconfigure(encoding='utf-8')

def load_zone_spec(zone_id: str) -> str:
    """Loads the spec.json for a zone."""
    # Resolve paths relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zone_dir = os.path.join(base_dir, zone_id)
    spec_path = os.path.join(zone_dir, "spec.json")
    
    if not os.path.exists(spec_path):
        return f"Error: No spec.json found for zone {zone_id} at {spec_path}. Run extract_zone_specs.py first."
        
    with open(spec_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Convert raw tables to a string representation
    text_rep = []
    text_rep.append(f"Zone ID: {data['zone_id']}")
    text_rep.append(f"Source: {data['source_file']}")
    text_rep.append("Specifications:")
    
    # New format: 'tables' is a list of Markdown strings
    if 'tables' in data:
        for table in data['tables']:
            text_rep.append(table)
    # Fallback for old format
    elif 'raw_tables' in data:
         for table in data['raw_tables']:
            for row in table:
                row_str = " | ".join([c for c in row if c.strip()])
                if row_str:
                    text_rep.append(row_str)
                
    return "\n".join(text_rep)

def load_bylaws() -> List[Dict]:
    """Loads the general bylaws."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "bylaw_articles.json")
    if not os.path.exists(path):
        print(f"Warning: bylaw_articles.json not found at {path}.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def search_bylaws(query: str, articles: List[Dict], top_k: int = 5) -> List[Dict]:
    """
    Simple keyword search.
    In a real system, this would be a Vector Search (Embeddings).
    """
    query_words = set(query.lower().split())
    scored = []
    
    for art in articles:
        text = art['text'].lower()
        score = 0
        for word in query_words:
            if word in text:
                score += 1
        
        if score > 0:
            scored.append((score, art))
            
    # Sort by score desc
    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:top_k]]

def find_cross_references(text: str) -> List[str]:
    """Finds all 'article X' references in the text."""
    # Matches "article 123", "article 123.1", etc.
    # Case insensitive
    matches = re.findall(r'article\s+(\d+(?:\.\d+)?)', text, re.IGNORECASE)
    return list(set(matches))

def construct_prompt(zone_id: str, question: str, zone_spec: str, relevant_articles: List[Dict], bylaws: List[Dict]) -> str:
    # 1. Automatic Cross-Reference Resolution
    # Find articles mentioned in the Zone Spec
    referenced_ids = find_cross_references(zone_spec)
    
    referenced_articles = []
    for art_id in referenced_ids:
        # Find the article in the full bylaw list
        # This is O(N), could be O(1) with a dict
        found = next((a for a in bylaws if a['id'] == art_id), None)
        if found:
            referenced_articles.append(found)
            
    prompt = f"""You are a Zoning Expert. Answer the question based ONLY on the context below.
If the answer is in the Zone Specifications, cite "Zone Spec".
If the answer is in the General Bylaws, cite "Article X".

QUESTION: {question}
ZONE: {zone_id}

--- CONTEXT: ZONE SPECIFICATIONS ---
{zone_spec}

--- CONTEXT: REFERENCED ARTICLES (Automatically Detected) ---
"""
    if referenced_articles:
        for art in referenced_articles:
            prompt += f"\n[Article {art['id']}]\n{art['text']}\n"
    else:
        prompt += "(None detected)\n"

    prompt += "\n--- CONTEXT: RELEVANT BYLAWS (Search Results) ---\n"
    for art in relevant_articles:
        prompt += f"\n[Article {art['id']}]\n{art['text']}\n"
        
    prompt += "\nANSWER:"
    return prompt

def main():
    if len(sys.argv) < 3:
        print("Usage: python query_zoning.py <zone_id> <question>")
        sys.exit(1)
        
    zone_id = sys.argv[1]
    question = " ".join(sys.argv[2:])
    
    print(f"Querying Zone {zone_id} with: '{question}'")
    
    # 1. Load Zone Spec
    zone_spec = load_zone_spec(zone_id)
    if zone_spec.startswith("Error"):
        print(zone_spec)
        return

    # 2. Load Bylaws
    articles = load_bylaws()
    
    # 3. Search Bylaws (Vector/Keyword Search)
    relevant_articles = search_bylaws(question, articles)
    
    # 4. Construct Prompt (with Cross-References)
    prompt = construct_prompt(zone_id, question, zone_spec, relevant_articles, articles)
    
    print("\n" + "="*40)
    print("GENERATED PROMPT FOR LLM")
    print("="*40)
    print(prompt)
    print("="*40)
    print("\n(In a real system, this prompt would be sent to GPT-4/Claude/Gemini)")

if __name__ == "__main__":
    main()
