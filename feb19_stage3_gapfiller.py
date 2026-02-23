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
        # Match the folder naming convention from Stage 1/2
        folder_name = f"{selected_book['book_name']}_{selected_book['author']}".replace(" ", "")
        target_folder = SOURCE_BOOKS_ROOT / folder_name
        
        if not target_folder.exists():
            # Fallback if the name doesn't have the author suffix
            target_folder = SOURCE_BOOKS_ROOT / selected_book['book_name'].replace(" ", "")
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
        return

    if not target_folder.exists():
        print(f"❌ Error: Source folder not found at {target_folder}")
        return

    /Users/limorkissos/Documents/books/inbox_photos/data_test/feb19_stage3_gapfiller.py

if __name__ == "__main__":
    run_stage_3_smart_fill()
