

```markdown
⚡ QuickStart Guide: The Two-Step AI Library Building Your Research Dataset from Scratch

This repository provides an automated, three-stage pipeline for converting raw book imagery into a structured, research-ready dataset. The system is designed to be resume-aware, audit-driven, and cost-efficient.

🟢 1. Environment & API Setup  
Before running the pipeline, ensure your environment is configured and your API credentials are set.

**Activate Virtual Environment**  
Bash

Navigate to your project root  
```bash
cd /path/to/your/folder
```

Create and activate environment  
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies  
```bash
pip install openai pillow
```

**Persistent API Keys**  
Run these commands to ensure your shell session has access to the required models:

```bash
echo 'export OPENAI_API_KEY="your_actual_key"' >> ~/.zshrc
source ~/.zshrc
```

**VS Code Tip:** If the IDE defaults to a "ghost" or system environment, run  
```bash
rm -rf .venv
```  
in the project root to force a clean environment selection.

🛠 2. The Three-Stage Pipeline

**Stage 1: High-Fidelity Extraction (Ingestion)**  
Converts raw images into structured JSON objects.

Command:  
```bash
python stage1_ingestion.py
```

Logic: This script is resume-aware; it automatically skips source images that already have a corresponding JSON in the library.

Data Prep: Place images in folders following the `BookTitle_AuthorName/` convention.

**Stage 2: Operations Center (Audit)**  
Cross-references source images against the organized library to detect sequence gaps.

Command:  
```bash
python stage2_audit.py
```

Result: Generates a `gap_analysis_report.json` showing completion percentages and specific missing page numbers per book.

**Stage 3: Precision Infill (Refinement)**  
Targets specific books to reach 100% completion based on the Stage 2 Audit.

Command:  
```bash
python stage3_gap_filler.py
```

Workflow: An interactive CLI allows you to select an incomplete book and scan only the missing pages, preventing wasted API costs.

🔍 3. Quality Control & Synthesis  
Once ingestion is complete, run the synthesis scripts to generate research-ready tables.

- **Thematic Filtering**: Consolidate findings into a master table filtered for specific thematic insights (e.g., body sensations).  
- **Accuracy Audit**: Run  
  ```bash
  python stage4_accuracy_audit.py
  ```  
  to generate Trust Scores and verify verbatim transcription accuracy.

✅ Success Checklist

- **Global Deduplication**: Ensure no page repetitions exist in the final summary.
- **Environment Check**: Use `which python` to ensure you are running from the local `.venv` and not system Python.
- **Gap Closure**: Verify that all books in the Stage 2 report show 100.0% completion.
```

