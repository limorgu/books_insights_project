 ⚡ QuickStart Guide: The Two-Step AI Library
Building Your Research Dataset from Scratch

This guide provides the exact workflow to activate your environment and move through the extraction and synthesis pipeline established in Note #5 and Note #6.

1️⃣ Environment & API Setup
Before running any scripts, you must activate your specialized virtual environment and ensure your API keys are registered.

Activate your environment:

Bash
# Navigate to your project root
cd /path/to/your/folder

# Activate the environment
source /path/to/your/folder/bin/activate
Install Persistent API Keys:
Run these once in your terminal to ensure your system remembers your credentials permanently:

Bash
echo 'export GEMINI_API_KEY="your_actual_key"' >> ~/.zshrc
echo 'export OPENAI_API_KEY="your_actual_key"' >> ~/.zshrc
source ~/.zshrc
💡 VS Code Tip: If VS Code defaults to a "ghost" .venv, run rm -rf .venv in the project root to force it to use your active environment.

2️⃣ Data Preparation
AI intelligence starts with human-aligned organization.

Location: Place book images inside your data input folder.

Naming Convention: Use BookTitle_AuthorName/ for folder names. This acts as the "Ground Truth" for the pipeline.

3️⃣ Step 1: High-Fidelity Extraction
Run the extraction script to convert images into structured data objects.

Bash
python stage1_extract_features_to_json.py
Result: Creates enriched JSONs for every page.

Resume-Aware: This script is safe to rerun; it automatically skips images that have already been processed.

4️⃣ Step 2: Synthesis & Filtering
Consolidate your findings into a master research table and filter for thematic insights like body sensations.

Bash
python stage2_make_json_features_table.py
Result: A master summary file in your output folder.

Verification: Check the terminal output for data completion counts to audit for any missing information.

5️⃣ Audit & Finalization (Quality Control)
Practice "The Vigilant Monitor" by running a sample audit to verify AI trust scores.

Audit for Accuracy:

Bash
python stage4_accuracy_audit.py
Result: A report showing Trust Scores and accuracy ratings.

Generate Final Research Tables:

Bash
python stage5_generate_final_tables.py
Result: Final research-ready datasets grouped by Book and Author.

✅ Success Checklist
Global Deduplication: Ensure no page repetitions exist in the final summary.

Thematic Accuracy: Check the Body Sensations report for high-fidelity quotes.

Environment Check: Use the which python command to ensure you aren't in a "Ghost Environment".