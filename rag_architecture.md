# Zoning RAG Architecture

## Goal
Build a RAG system to answer questions about building regulations for specific lots, with high accuracy and source citations.

## Challenges with Zoning Data
1.  **Hierarchical Structure**: Rules are split between "General Provisions" (apply to everyone) and "Zone Specifications" (apply to specific zones).
2.  **Tabular Data**: Zone specifications are almost always tables (grids). Standard text extraction destroys table structure, leading to hallucinations.
3.  **Cross-Referencing**: A zone spec might say "Subject to Article 123". The system must know what Article 123 is.

## Proposed Pipeline

### 1. Classification & Ingestion (The "Classify" Step)

We need to treat the documents as two different types of data:

#### A. Zone Specification Sheets (The "Grids")
*   **Source**: The pages extracted by your current `map_ids_to_pages.py` (e.g., `31001Ma.pdf`).
*   **Processing**: Do **not** use simple text extraction. Use a Table Extraction tool (e.g., `pdfplumber`, `Azure Document Intelligence`, or a Vision-Language Model like Gemini 1.5 Pro).
*   **Output**: Structured JSON or Markdown Table.
    ```json
    {
      "zone_id": "31001Ma",
      "uses_permitted": ["h1 (1-family)", "h2 (2-family)"],
      "max_height_meters": 10,
      "front_setback_min": 6,
      "source_file": "B-1.1R2_FR_033_003.pdf",
      "page": 45
    }
    ```

#### B. General Bylaws (The "Rules")
*   **Source**: The large PDF files (e.g., `R.C.A.3V.Q.4_compressed.pdf`).
*   **Processing**: Chunk by **Article** or **Section**. Do not use fixed-size character chunks (e.g., 500 chars) because it might cut a rule in half.
*   **Metadata**:
    ```json
    {
      "article_id": "123",
      "topic": "Hauteur des bâtiments",
      "text": "La hauteur est mesurée à partir de...",
      "source_file": "R.C.A.3V.Q.4_compressed.pdf",
      "page": 12
    }
    ```

### 2. Retrieval Strategy (The "No Errors" Step)

When a user asks: *"Can I build a 2-story house on Lot X?"*

1.  **Resolve Location**:
    *   Input: Lot X (Address or Cadastre).
    *   Action: Look up `Zone ID` in your GeoJSON (e.g., `31001Ma`).

2.  **Hybrid Retrieval**:
    *   **Step A (Specific)**: Fetch the Structured JSON for `Zone 31001Ma`.
    *   **Step B (General)**: Use the user's query ("2-story house") to vector search the General Bylaws.
    *   **Step C (Cross-Reference)**: If the Zone JSON mentions "See Article 50", automatically fetch Article 50.

3.  **Context Construction**:
    *   Feed the LLM:
        *   "User is asking about Zone 31001Ma."
        *   "Here is the Specification Grid for 31001Ma: [JSON Data]"
        *   "Here are relevant definitions from the Bylaw: [Article Text]"

### 3. Citations
*   Since every chunk (JSON or Text) has `source_file` and `page` in its metadata, the LLM can be instructed to append citations.
*   Example Output: *"Yes, 2 stories are allowed. The max height is 10m (Zone 31001Ma Spec, p.45) and height is measured from the street level (Article 123, p.12)."*

## Implementation Roadmap

1.  **Refine Extraction**: Update `map_ids_to_pages.py` to not just extract pages, but try to parse the text more cleanly (or use a better tool).
2.  **Index General Bylaws**: Write a script to parse the large PDF into Articles.
3.  **Build Vector Store**: Use a local vector store (like Chroma or FAISS) to store the General Bylaws.
4.  **Query Interface**: A simple script that takes a Zone ID + Question and runs the retrieval.
