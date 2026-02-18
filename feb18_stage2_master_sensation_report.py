import os
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
from openai import OpenAI

# ---------------------------
# Config
# ---------------------------
RESULTS_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
MODEL = "gpt-4o-mini"
PAGES_PER_ITERATION = None  # Set to None for full run, or an integer like 10 for testing

def parse_folder_name(folder_name: str) -> Tuple[str, str]:
    """Extracts Title and Author from folder name (BookTitle_AuthorName)."""
    parts = folder_name.split("_")
    # Safeguard if folder name doesn't have an underscore
    title = parts[0].strip()
    author = parts[1].strip() if len(parts) > 1 else "Unknown"
    return title, author

def identify_body_sensations(client: OpenAI, text: str) -> Dict[str, Any]:
    prompt = """
Your task is to act as a Clinical Sensory Extractor. Analyze the text for ONLY literal, physical, physiological sensations.

STRICT DEFINITIONS:
1. PHYSICAL SENSATIONS: Literal body states like headache, tummy ache, warmth, cold, shaking, trembling, heart racing, nausea, or pain.
2. SENSORY EXPERIENCES: Direct observations of smelling, hearing, tasting, or tactile touch.

STRICT NEGATIVE CONSTRAINTS (FORBIDDEN):
- DO NOT extract abstract emotions (e.g., love, pride, sadness, shame).
- DO NOT extract personality traits or behaviors (e.g., obedience, control, carefulness).
- If the narrator says "I felt love," IGNORE IT. 
- If the narrator says "My chest felt tight with love," extract ONLY "chest felt tight."

Instructions:
1. Identify if literal physical sensations are present.
2. For each, extract the specific body part or sensation name.
3. Provide the EXACT verbatim quote.

Return strictly in JSON:
{
  "sensations_found": boolean,
  "sensations": [
    {
      "name": "string (e.g., stomach ache, shivering, smell of smoke)",
      "quote": "string"
    }
  ]
}
"""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": f"{prompt}\n\nText to analyze: {text}"}],
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return {"sensations_found": False, "sensations": [] }

def process_stage_2():
    client = OpenAI()
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY is not set.")
        return

    master_library = {}
    print(f"--- 🔍 Stage 2: Global Consolidation ---")

    # 1. GLOBAL CRAWL
    all_json_files = sorted(list(RESULTS_BASE.rglob("page_*.json")))
    
    # Apply iteration limit if testing
    files_to_process = all_json_files[:PAGES_PER_ITERATION] if PAGES_PER_ITERATION else all_json_files

    for pf in files_to_process:
        try:
            data = json.loads(pf.read_text(encoding="utf-8"))
            folder_title, folder_author = parse_folder_name(pf.parent.name)
            
            try:
                p_num = int(data.get("page_number"))
            except (TypeError, ValueError):
                continue 
            
            if folder_title not in master_library:
                master_library[folder_title] = {
                    "author": folder_author,
                    "unique_pages": {},
                    "path": str(pf.parent)
                }
            
            master_library[folder_title]["unique_pages"][p_num] = data
        except Exception:
            continue

    all_books_summary = []
    body_sensation_report = {}

    # 2. Process the Unified Library
    for book_title, book_info in master_library.items():
        sorted_page_nums = sorted(book_info["unique_pages"].keys())
        book_word_count = 0
        sensations_in_book = []
        
        print(f"📖 Consolidating: {book_title} ({len(sorted_page_nums)} unique pages)")
        
        for p_num in sorted_page_nums:
            page_data = book_info["unique_pages"][p_num]
            content = page_data.get("content", "")
            book_word_count += len(content.split())
          
            # Sensation extraction
            sens_data = identify_body_sensations(client, content)
            if sens_data.get("sensations_found"):
                sensations_in_book.append({
                    "page_number": p_num,
                    "sensations": sens_data.get("sensations", [])
                })

        # Build Summary #1
        all_books_summary.append({
            "book_name": book_title,
            "author": book_info["author"],
            "page_range": f"{min(sorted_page_nums)} - {max(sorted_page_nums)}" if sorted_page_nums else "0",
            "unique_pages_count": len(sorted_page_nums),
            "total_word_count": book_word_count,
            "body_sensation_pages_found": len(sensations_in_book)
        })

        # Build Summary #2
        if sensations_in_book:
            body_sensation_report[book_title] = {
                "author": book_info["author"],
                "relevant_pages": sensations_in_book
            }

    # 3. Save Summaries
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = RESULTS_BASE / f"consolidated_summary_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "1_library_high_level.json").write_text(json.dumps(all_books_summary, indent=4))
    (output_dir / "2_body_sensations_report.json").write_text(json.dumps(body_sensation_report, indent=4))

    print(f"\n--- 🏁 Finished ---")
    print(f"📊 Global data healed and saved to: {output_dir}")

if __name__ == "__main__":
    process_stage_2()