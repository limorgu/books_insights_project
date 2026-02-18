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

def parse_folder_name(folder_name: str) -> Tuple[str, str]:
    """
    Extracts Title and Author from folder name (Book_Title_Author_Name).
    Ensures 'The' and 'The_Winter_of_My_Soul' merge correctly.
    """
    clean_name = folder_name.replace("_", " ")
    parts = clean_name.split()
    if len(parts) >= 2:
        author = " ".join(parts[-3:])
        title = " ".join(parts[:-3])
        return title.strip() or folder_name, author.strip()
    return folder_name, "Unknown Author"

def identify_body_sensations(client: OpenAI, text: str) -> Dict[str, Any]:
    prompt = (
        "Analyze the following text for physical body sensations (tension, warmth, "
        "heartbeat, pain, tingling, etc.). Return JSON: "
        "{'has_sensations': boolean, 'found_sensations': list, 'context': string}"
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": f"{prompt}\n\nText: {text}"}],
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return {"has_sensations": False, "found_sensations": [], "context": ""}

def process_stage_2():
    client = OpenAI()
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY is not set.")
        return

    # master_library[Standardized Title] -> { "author": str, "pages": { page_num: data } }
    master_library = {}

    print(f"--- 🔍 Stage 2: Global Consolidation ---")

    # 1. GLOBAL CRAWL: Find every page JSON in every run folder ever created
    all_json_files = sorted(list(RESULTS_BASE.rglob("page_*.json")))

    for pf in all_json_files:
        try:
            data = json.loads(pf.read_text(encoding="utf-8"))
            # Group by folder-derived name to fix the AI naming errors
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
            
            # Deduplication: If page exists in multiple runs, newest file wins
            master_library[folder_title]["unique_pages"][p_num] = data
        except Exception:
            continue

    all_books_summary = []
    body_sensation_report = {}
    master_text_files = {} # For the 3rd JSON: Full Book Text

    # 2. Process the Unified Library
    for book_title, book_info in master_library.items():
        sorted_page_nums = sorted(book_info["unique_pages"].keys())
        
        book_word_count = 0
        sensations_in_book = []
        full_book_content = []
        
        print(f"📖 Consolidating: {book_title} ({len(sorted_page_nums)} unique pages)")
        
        for p_num in sorted_page_nums:
            page_data = book_info["unique_pages"][p_num]
            content = page_data.get("content", "")
            book_word_count += len(content.split())
            full_book_content.append(f"--- Page {p_num} ---\n{content}")
            
            # Sensation extraction
            sens_data = identify_body_sensations(client, content)
            if sens_data.get("has_sensations"):
                sensations_in_book.append({
                    "page_number": p_num,
                    "sensations": sens_data.get("found_sensations"),
                    "quote": content,
                    "context": sens_data.get("context")
                })

        # Summary #1 data
        all_books_summary.append({
            "book_name": book_title,
            "author": book_info["author"],
            "page_range": f"{min(sorted_page_nums)} - {max(sorted_page_nums)}" if sorted_page_nums else "0",
            "unique_pages_count": len(sorted_page_nums),
            "total_word_count": book_word_count,
            "body_sensation_pages_found": len(sensations_in_book)
        })

        # Summary #2 data
        if sensations_in_book:
            body_sensation_report[book_title] = {
                "author": book_info["author"],
                "relevant_pages": sensations_in_book
            }
            
        # Summary #3 data (Master Text)
        master_text_files[book_title] = "\n\n".join(full_book_content)

    # 3. Save All Summaries
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = RESULTS_BASE / f"consolidated_summary_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "1_library_high_level.json").write_text(json.dumps(all_books_summary, indent=4))
    (output_dir / "2_body_sensations_report.json").write_text(json.dumps(body_sensation_report, indent=4))
    (output_dir / "3_master_book_texts.json").write_text(json.dumps(master_text_files, indent=4))

    print(f"\n--- 🏁 Finished ---")
    print(f"📊 Global data healed and saved to: {output_dir}")

if __name__ == "__main__":
    process_stage_2()