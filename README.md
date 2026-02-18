
The Two-Step AI Library: High-Fidelity Research Pipeline
This project is a modular, resume-aware pipeline designed to transform scanned book pages into structured, research-ready datasets. It prioritizes data integrity and human-aligned organization, shifting the focus from passive extraction to active architecture.

Core Features
Resume-Aware Extraction: A global "Pre-Flight Check" scans all historical runs to ensure no page is ever processed twice, saving time and API costs.

Folder-Based Ground Truth: Standardizes book and author metadata using physical directory naming conventions (Title_Author), eliminating AI-naming hallucinations.

Global Deduplication: Automatically heals fragmented data from different runs into a single, unified record per book.

Thematic Extraction: Filters for specific clinical or qualitative features (e.g., body sensations) directly at the source with full-context quotes.

Accuracy Auditing: Integrated "Trust Score" monitoring ensures that the AI's output remains a source of truth.

⚡ QuickStart Guide
1. Environment Setup
Activate your environment and configure your persistent API keys.

Bash
# Navigate to project and activate environment
cd /path/to/your/project
source /path/to/env/bin/activate

# Install Persistent API Keys (Run once)
echo 'export OPENAI_API_KEY="your_actual_key"' >> ~/.zshrc
source ~/.zshrc
💡 Note: If using VS Code, ensure the interpreter is set to your active environment path to avoid "Ghost Environment" errors.

2. Prepare Data
Place book folders inside your data input directory.

Naming Convention: BookTitle_AuthorName/.

Content: High-resolution images of book pages.

3. Step 1: High-Fidelity Extraction
Convert images into structured JSON data objects.

Bash
python stage1_extract_to_json.py
Result: Creates page-level JSONs containing verbatim text and metadata.

4. Step 2: Synthesis & Filtering
Consolidate the library and extract thematic insights.

Bash
python stage2_consolidate_and_filter.py
Result: Generates the three master reports described below.

📂 Output Structure
The pipeline produces three essential JSON summaries in an timestamped output folder:

1_library_high_level.json: Global progress report including page ranges, unique page counts, and total word counts per book.

2_thematic_report.json: Filtered insights (e.g., body sensations) organized by book and page number, featuring full verbatim quotes and context.

3_master_texts.json: A consolidated file containing the complete, ordered text for every book in the library.

✅ Success Checklist
Zero Duplication: Each physical page exists only once in the final summary.

Traceability: Every finding is linked back to a specific page number and source image.

Human-in-the-Loop: Use the built-in accuracy audit scripts to verify AI ratings periodically.
