import os
import json
import datetime
from pathlib import Path
from typing import Any, Dict, List
from openai import OpenAI
import PIL.Image
import io
import base64

# ---------------------------
# 1. Path Configuration
# ---------------------------
# This matches your Stage 1 and Stage 2 directory structure
SOURCE_BOOKS_ROOT = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_books_test")
RESULTS_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
LIBRARY_ROOT = RESULTS_BASE / "Organized_Library"
MODEL = "gpt-4o-mini"
WORD_THRESHOLD = 200

# ---------------------------
# 2. Helpers
# ---------------------------
def image_to_data_url(path: Path) -> str:
    img = PIL.Image.open(path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

def extract_page_data(client: OpenAI, image_path: Path) -> Dict[str, Any]:
    prompt = "Transcribe ALL text verbatim. Return JSON: {'content': string, 'page_number': int/null}"
    try:
        data_url = image_to_data_url(image_path)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": data_url}}]}],
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)
    except: return {"content": "", "page_number": None}

# ---------------------------
# 3. Main Stage 3 Logic
# ---------------------------
def run_stage_3_smart_fill():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY is not set.")
        return
    
    client = OpenAI()
    
    # 🔍 STEP A: Find the latest Audit Report from Stage 2
    # This automatically looks for the folder Stage 2 just created
    audit_folders = sorted(list(RESULTS_BASE.glob("library_audit_*")), reverse=True)
    if not audit_folders:
        print("❌ No Stage 2 Audit found. Please run Stage 2 first to identify gaps.")
        return
    
    latest_audit_file = audit_folders[0] / "2_gap_analysis_report.json"
    audit_data = json.loads(latest_audit_file.read_text())

    # 📊 STEP B: Display only incomplete books
    print("\n--- 📑 Books Needing Completion ---")
    
    incomplete_books = []
    for b in audit_data:
        # Match Stage 2 key: 'completion_percentage'
        pct = b.get('completion_percentage') or "0%"
        if pct != "100.0%":
            incomplete_books.append(b)
    
    if not incomplete_books:
        print("🎉 All books are 100% complete according to the last audit!")
        return

    for i, book in enumerate(incomplete_books):
        # Match Stage 2 keys: 'completion_percentage' and 'missing_count'
        pct_display = book.get('completion_percentage', "0%")
        missing = book.get('missing_count', "??")
        print(f"[{i}] {book['book_name']} - {pct_display} ({missing} missing)")
    # ⌨️ STEP C: User Input
    choice = input("\nEnter the number of the book to complete (or 'q' to quit): ").strip()
    if choice.lower() == 'q': return
    
    try:
        selected_book = incomplete_books[int(choice)]
        book_title_slug = selected_book['book_name'].replace(" ", "")
        
        # --- NEW SMART MATCHING LOGIC ---
        target_folder = None
        
        # 1. Try to find a folder that STARTS with the book title slug
        possible_folders = [
            d for d in SOURCE_BOOKS_ROOT.iterdir() 
            if d.is_dir() and d.name.startswith(book_title_slug)
        ]
        
        if possible_folders:
            # Pick the most likely match (usually the only one)
            target_folder = possible_folders[0]
            print(f"📂 Found matching folder: {target_folder.name}")
        else:
            # 2. Final fallback to the basic naming convention
            folder_name = f"{selected_book['book_name']}_{selected_book['author']}".replace(" ", "")
            target_folder = SOURCE_BOOKS_ROOT / folder_name

    except (ValueError, IndexError):
        print("❌ Invalid selection.")
        return

    if not target_folder or not target_folder.exists():
        print(f"❌ Error: Source folder not found for {book_title_slug}")
        print(f"Checked in: {SOURCE_BOOKS_ROOT}")
        return
    # ⚙️ STEP D: Execution Logic (Fill only the gaps)
    book_output_dir = LIBRARY_ROOT / target_folder.name
    book_output_dir.mkdir(parents=True, exist_ok=True)

    existing_json_content = []
    for jf in book_output_dir.glob("page_*.json"):
        try:
            existing_json_content.append(json.loads(jf.read_text()))
        except: continue

    already_done_images = {d.get("source_image") for d in existing_json_content if d.get("source_image")}
    already_done_pages = {int(d.get("page_number")) for d in existing_json_content if d.get("page_number") is not None}

    all_images = sorted([p for p in target_folder.iterdir() if p.suffix.lower() in ['.jpg', '.png', '.jpeg']])
    images_to_process = [img for img in all_images if img.name not in already_done_images]

    if not images_to_process:
        print(f"✅ No missing images found in source for {target_folder.name}!")
        return

    # --- NEW: User decides the processing limit ---
    print(f"\n🚀 Found {len(images_to_process)} missing pages.")
    limit_input = input(f"How many pages to process? (Enter a number, or 'all' for all {len(images_to_process)}): ").strip().lower()
    
    if limit_input == 'all':
        limit = len(images_to_process)
    else:
        try:
            limit = int(limit_input)
        except ValueError:
            print("⚠️ Invalid input. Defaulting to 10 pages for safety.")
            limit = 10

    # 🚀 Run with the selected limit
    for img in images_to_process[:limit]: 
        print(f"  📸 Scanning {img.name}...")
        res = extract_page_data(client, img)
        
        res["source_image"] = img.name 
        res["book_name"] = selected_book['book_name']
        res["book_author"] = selected_book['author']
        
        p_num = res.get("page_number")
        # Use page number for the filename, fallback to image name to prevent overwrites
        label = p_num if (p_num and int(p_num) not in already_done_pages) else f"file_{img.stem}"
            
        (book_output_dir / f"page_{label}.json").write_text(json.dumps(res, indent=4))

    print(f"\n✅ Finished processing {limit} pages. Re-run Stage 2 to see updated metrics!")
if __name__ == "__main__":
    run_stage_3_smart_fill()
