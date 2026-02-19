
```markdown
# QuickStart Guide: Building Your Research Dataset from Scratch

⚡ **The Two-Step AI Library – actually a reliable three-stage pipeline**

This repository gives you an automated, resume-aware, audit-driven, cost-efficient system to convert raw book images into structured, research-ready JSON datasets.

## 🟢 1. Environment & API Setup

Before running anything, set up your environment and credentials.

### Activate Virtual Environment

```bash
# Navigate to project root
cd /path/to/your/folder

# Create and activate
python3 -m venv .venv
source .venv/bin/activate

# Install core dependencies
pip install openai pillow
Persistent API Keys
Add your key so it survives new terminal sessions:
Bashecho 'export OPENAI_API_KEY="your_actual_key"' >> ~/.zshrc
source ~/.zshrc
VS Code Tip: If VS Code keeps using system Python or a "ghost" env:
Bashrm -rf .venv
Then re-open the folder — it should prompt to use the new .venv.
🛠 2. The Three-Stage Pipeline
Stage 1: High-Fidelity Extraction (Ingestion)
Converts raw images → structured JSON objects.
Bashpython stage1_ingestion.py

Resume-aware: Skips images that already have a matching JSON
Data Prep: Organize images in folders like:
BookTitle_AuthorName/01_page.jpg, BookTitle_AuthorName/02_page.jpg, etc.

Stage 2: Operations Center (Audit)
Cross-checks images vs. processed library → finds sequence gaps.
Bashpython stage2_audit.py

Output: gap_analysis_report.json
Shows completion % per book + exact missing page numbers

Stage 3: Precision Infill (Refinement)
Targets incomplete books and processes only missing pages.
Bashpython stage3_gap_filler.py

Interactive CLI: Choose which book(s) to complete
Prevents wasting API calls on already-finished content

🔍 3. Quality Control & Synthesis
After ingestion:

Thematic Filtering — Combine results into filtered master tables (e.g., body sensations only)
Accuracy AuditBashpython stage4_accuracy_audit.py→ Generates Trust Scores + verifies transcription fidelity

✅ Success Checklist

 No duplicate pages in final output (global deduplication)
which python points to .venv/bin/python (not system Python)
 All books in gap_analysis_report.json show 100.0% completion
```

