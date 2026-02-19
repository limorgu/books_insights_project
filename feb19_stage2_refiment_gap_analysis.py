import os
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

# ---------------------------
# Config
# ---------------------------
SOURCE_BOOKS_ROOT = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_books_test")
RESULTS_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
LIBRARY_ROOT = RESULTS_BASE / "Organized_Library"

def parse_folder_name(folder_name: str) -> Tuple[str, str]:
    parts = folder_name.split("_")
    title = parts[0].strip()
    author = parts[1].strip() if len(parts) > 1 else "Unknown"
    return title, author

def process_stage_2_with_audit():
    master_library = {}
    audit_report = []
    
    print(f"--- 🧹 Stage 2: Data Refinement & Gap Audit ---")

    # 1. Map out the PHYSICAL SOURCE (What SHOULD exist)
    source_folders = [d for d in SOURCE_BOOKS_ROOT.iterdir() if d.is_dir()]
    
    # 2. Map out the ORGANIZED LIBRARY (What DOES exist)
    all_json_files = list(LIBRARY_ROOT.rglob("page_*.json"))
    
    # Pre-index existing JSONs by book
    json_map = {}
    for pf in all_json_files:
        book_folder = pf.parent.name
        if book_folder not in json_map:
            json_map[book_folder] = []
        json_map[book_folder].append(pf)

    # 3. Perform the Audit per Book
    for s_folder in source_folders:
        title, author = parse_folder_name(s_folder.name)
        
        # Count raw images in source
        raw_images = [img for img in s_folder.iterdir() if img.suffix.lower() in ['.jpg', '.jpeg', '.png']]
        total_source_count = len(raw_images)
        
        # Find matching organized folder (trying exact or slug match)
        org_folder_name = s_folder.name.replace(" ", "")
        book_jsons = json_map.get(org_folder_name, [])
        
        found_pages = []
        total_words = 0
        
        for jf in book_jsons:
            try:
                data = json.loads(jf.read_text())
                p_num = data.get("page_number")
                if p_num is not None:
                    found_pages.append(int(p_num))
                total_words += len(data.get("content", "").split())
            except: continue

        found_pages.sort()
        processed_count = len(book_jsons)
        
        # Calculate Gaps
        gaps = []
        if found_pages:
            full_range = set(range(min(found_pages), max(found_pages) + 1))
            gaps = sorted(list(full_range - set(found_pages)))
        
        # Calculate Completion %
        completion_pct = (processed_count / total_source_count * 100) if total_source_count > 0 else 0
        
        # Build the Audit Entry
        audit_entry = {
            "book_name": title,
            "author": author,
            "status": "In Progress" if processed_count > 0 else "Not Started",
            "completion_percentage": f"{completion_pct:.1f}%",
            "pages_processed": processed_count,
            "total_images_in_source": total_source_count,
            "missing_count": total_source_count - processed_count,
            "sequence_gaps": gaps,
            "total_word_count": total_words
        }
        audit_report.append(audit_entry)
        
        # Also build the high-level library summary
        if processed_count > 0:
            master_library[title] = {
                "author": author,
                "page_range": f"{min(found_pages)} - {max(found_pages)}" if found_pages else "N/A",
                "unique_pages": processed_count,
                "word_count": total_words
            }

    # 4. Save Reports
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = RESULTS_BASE / f"library_audit_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "1_library_high_level.json").write_text(json.dumps(list(master_library.values()), indent=4))
    (output_dir / "2_gap_analysis_report.json").write_text(json.dumps(audit_report, indent=4))

    print(f"\n✅ Audit Complete!")
    print(f"📊 Report saved to: {output_dir}")
    if any(b['status'] == "Not Started" for b in audit_report):
        print("⚠️ Warning: Some books have 0% progress (e.g., My Brilliant Friend).")

if __name__ == "__main__":
    process_stage_2_with_audit()