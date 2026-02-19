import os
import json
import io
import base64
import datetime
import random
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List
from PIL import Image
from openai import OpenAI

# ---------------------------
# config
# ---------------------------
ROOT_DIR_DEFAULT = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_books_test")
OUTPUT_BASE = Path("/Users/limorkissos/Documents/books/inbox_photos/data_test/Feb_results")
MODEL = "gpt-4o-mini"
WORD_THRESHOLD = 200
PAGES_PER_ITERATION = 100

# ---------------------------
# helpers
# ---------------------------
def image_to_data_url(path: Path) -> str:
    """Converts image to base64 for OpenAI Vision API."""
    img = Image.open(path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"

def parse_book_author_from_folder(book_folder: Path) -> Tuple[str, str]:
    """Splits folder name by underscore to get Title and Author."""
    name_parts = book_folder.name.split("_")
    if len(name_parts) >= 2:
        author = name_parts[-1].strip()
        title = " ".join(name_parts[:-1]).replace("_", " ").strip()
        return title or book_folder.name, author
    return book_folder.name, "Unknown"

def get_globally_processed_images(output_base: Path, book_title: str) -> set:
    processed_images = set()
    # This '.rglob' is powerful—it looks in ALL subfolders, including 'Organized_Library'
    for json_file in output_base.rglob("page_*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("book_name") == book_title:
                    source_img = data.get("source_image")
                    if source_img:
                        processed_images.add(source_img)
        except Exception:
            continue
    return processed_images

def extract_page_data(client: OpenAI, image_path: Path) -> Dict[str, Any]:
    """Extracts text and metadata from image with error handling for JSON and Nulls."""
    prompt = (
        "Carefully transcribe ALL text from this page verbatim. Do not cut off or summarize. "
        "Extract the page number and any chapter/section title if visible. "
        "Return in JSON format: {'content': string, 'page_number': int/null, 'title': string/null}"
    )
    data_url = image_to_data_url(image_path)
    
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": data_url}}]}],
            response_format={"type": "json_object"}
        )
        
        # Hard Fix: Parse JSON and validate content is not None
        raw_content = resp.choices[0].message.content
        if not raw_content:
            return {"content": "", "page_number": None, "title": None}
            
        result = json.loads(raw_content)
        
        # Ensure 'content' key exists and is a string (prevents .split() error)
        if result.get("content") is None:
            result["content"] = ""
            
        return result

    except json.JSONDecodeError:
        print(f"  ⚠️ Warning: AI returned invalid JSON for {image_path.name}. Skipping.")
        return {"content": "", "page_number": None, "title": None}
    except Exception as e:
        print(f"  ❌ API Error on {image_path.name}: {e}")
        return {"content": "", "page_number": None, "title": None}

# ---------------------------
# Main Runner
# ---------------------------
def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY is not set.")
        return

    client = OpenAI()
    root_dir = ROOT_DIR_DEFAULT.expanduser()
    
    # 1. Select Book
    book_folders = [p for p in root_dir.iterdir() if p.is_dir()]
    if not book_folders:
        print(f"⚠️ No book folders found in {root_dir}")
        return

    target_book_dir = random.choice(book_folders)
    book_title, author_name = parse_book_author_from_folder(target_book_dir)
    
    print(f"--- 🚀 Session Started ---")
    print(f"📖 Target Book: {book_title} by {author_name}")

    # 2. Global Scan to prevent duplicates
    already_processed = get_globally_processed_images(OUTPUT_BASE, book_title)
    
    # 3. Gather and Filter Images
    all_images = sorted([
        p for p in target_book_dir.iterdir() 
        if p.suffix.lower() in [".jpg", ".jpeg", ".png"]
    ])
    
    images_to_scan = [img for img in all_images if img.name not in already_processed]
    
    if not images_to_scan:
        print(f"✅ All {len(all_images)} images for this book are already processed!")
        return

    print(f"📊 Status: {len(already_processed)} done, {len(images_to_scan)} remaining.")

    # 4. Prepare Output Directory (Organized Library Mode)
    # This bypasses the 'run_' folders and goes straight to your clean library
    library_root = OUTPUT_BASE / "Organized_Library"
    
    # We use the full folder name (Title_Author) to ensure it matches your consolidation
    book_folder_name = f"{book_title.replace(' ', '')}_{author_name.replace(' ', '')}"
    book_output_dir = library_root / book_folder_name
    
    # Create the folder if it's a new book; otherwise, it uses the existing one
    book_output_dir.mkdir(parents=True, exist_ok=True)

    current_index = 0
    total_to_do = len(images_to_scan)

    # 5. Extraction Loop
    while current_index < total_to_do:
        end_idx = min(current_index + PAGES_PER_ITERATION, total_to_do)
        batch = images_to_scan[current_index:end_idx]

        print(f"\n📑 Processing batch ({current_index + 1}-{end_idx} of {total_to_do})...")

        for img_path in batch:
            try:
                print(f"  📸 Scanning {img_path.name}...")
                raw_data = extract_page_data(client, img_path)
                
                # Double-check: Use 'or ""' to ensure we never try to split None
                content = raw_data.get("content") or ""
                page_num = raw_data.get("page_number")
                
                # Safely split into words
                words = content.split()
                
                if len(words) >= WORD_THRESHOLD:
                    page_json = {
                        "book_name": book_title,
                        "book_author": author_name,
                        "page_number": page_num,
                        "content": content,
                        "source_image": img_path.name
                    }
                    
                    label = page_num if page_num is not None else f"file_{img_path.stem}"
                    page_file = book_output_dir / f"page_{label}.json"
                    page_file.write_text(json.dumps(page_json, indent=4), encoding="utf-8")
                else:
                    print(f"  ⏳ Skipping {img_path.name}: Word count ({len(words)}) below threshold.")

            except Exception as e:
                print(f"  ❌ Unexpected error on {img_path.name}: {e}")
            
            current_index += 1

        # Check for continuation
        if current_index < total_to_do:
            cmd = input(f"\n✅ Batch complete. Continue? (Enter for next {PAGES_PER_ITERATION}, or 'stop'): ").lower()
            if cmd == 'stop': break

    print(f"\n--- 🏁 Session Finished ---")
    print(f"📁 Results saved in: {book_output_dir}")

if __name__ == "__main__":
    main()