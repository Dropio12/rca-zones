# Zoning RAG System

This folder contains the prototype for a Retrieval-Augmented Generation (RAG) system for Zoning Bylaws.

## Architecture
The system uses a "Two-Tier" retrieval strategy:
1.  **Zone Specifications**: Extracted as structured data from the specific zone PDF (e.g., `31001Ma.pdf`).
2.  **General Bylaws**: Extracted as "Articles" from the main bylaw PDF (`R.C.A.3V.Q.4...`).

## Scripts

### 1. `extract_zone_specs.py`
Extracts tables from zone PDFs into `spec.json`.
**Usage:**
```bash
python extract_zone_specs.py [ZoneID]
# Example: python extract_zone_specs.py 31001Ma
# To process all: python extract_zone_specs.py
```

### 2. `extract_bylaw_articles_fast.py`
Extracts articles from the General Bylaw PDF into `bylaw_articles.json`.
**Usage:**
```bash
python extract_bylaw_articles_fast.py
```
*Note: Currently limited to the first 50 pages for testing. Edit the script to remove the limit.*

### 3. `query_zoning.py`
The main interface. Queries a specific zone and constructs a prompt for an LLM.
**Usage:**
```bash
python query_zoning.py <ZoneID> "<Question>"
# Example: python query_zoning.py 31001Ma "Quelle est la hauteur maximale?"
```

## Next Steps
1.  **Vector Search**: Replace the keyword search in `query_zoning.py` with `chromadb` or `sentence-transformers` for better accuracy.
2.  **Full Extraction**: Run `extract_bylaw_articles_fast.py` on the full PDF (remove the 50-page limit).
3.  **LLM Integration**: Connect `query_zoning.py` to an actual LLM API (OpenAI/Anthropic) to generate the final answer.
