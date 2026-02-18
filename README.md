Project Overview: The Two-Step AI Library
This project is a modular, high-fidelity pipeline designed to extract text from scanned book pages and transform them into a structured research dataset. It focuses on maintaining data integrity, resume-aware automation, and thematic filtering (e.g., body sensations) for qualitative and quantitative analysis.

🛠 Features
Resume-Aware Extraction: Automatically skips previously processed images to save time and API costs.

Folder-Based Ground Truth: Uses physical directory structures to standardize book and author metadata.

Global Deduplication: Consolidates data from multiple runs into a single, unified library.

Thematic Filtering: Extracts specific topics (like physical sensations) with full-context quotes.

Quality Audit: Built-in accuracy scoring to monitor AI performance.

⚡ QuickStart Guide
1️⃣ Environment & API Setup
Activate your virtual environment and configure your persistent API keys.

Activate Environment:

Bash
# Navigate to your project root
cd /path/to/your/project

# Activate your virtual environment
source /path/to/env/bin/activate
Set API Keys:
Run these once to save your credentials to your shell profile:

Bash
echo 'export GEMINI_API_KEY="your_key_here"' >> ~/.zshrc
echo 'export OPENAI_API_KEY="your_key_here"' >> ~/.zshrc
source ~/.zshrc
2️⃣ Data Preparation
AI intelligence starts with human-aligned organization.

Input Folder: Place book images in your designated data directory.

Naming Convention: Name folders as BookTitle_AuthorName.

3️⃣ Step 1: High-Fidelity Extraction
Convert images into structured JSON data objects.

Bash
python stage1_extract_to_json.py
Outcome: Creates page-level JSONs containing verbatim text and metadata.

4️⃣ Step 2: Synthesis & Filtering
Consolidate the library and filter for thematic insights.

Bash
python stage2_consolidate_and_filter.py
Outcome: Generates a unified library summary, a thematic (sensation) report, and master text files.

5️⃣ Audit & Finalization
Verify the accuracy of the extraction before finalizing your research tables.

Run Accuracy Audit:

Bash
python stage4_accuracy_audit.py
Generate Final Tables:

Bash
python stage5_generate_research_tables.py
✅ Success Checklist
Zero Duplication: Check the final summary to ensure each page appears only once.

Data Completeness: Verify the "page range" in the high-level summary matches your physical book.

Correct Environment: If scripts fail, run which python to ensure you aren't in a "Ghost Environment."

📂 Output Structure
1_library_high_level.json: Global progress, page counts, and ranges.

2_thematic_report.json: Filtered insights (e.g., sensations) with full quotes.

3_master_texts.json: Complete, ordered text for every book in the library.
