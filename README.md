
```markdown
# The Two-Step AI Library: High-Fidelity Research Pipeline

This project is a modular, resume-aware pipeline designed to transform **scanned book pages** into structured, research-ready datasets.  
It prioritizes data integrity and human-aligned organization — shifting the focus from passive extraction to **active architecture**.

## Core Features

- **Resume-Aware Extraction**  
  A global "Pre-Flight Check" scans all historical runs to ensure no page is ever processed twice → saves time and API costs

- **Folder-Based Ground Truth**  
  Standardizes book and author metadata using physical directory naming (`Title_Author`) → eliminates AI-naming hallucinations

- **Global Deduplication**  
  Automatically heals fragmented data from different runs into a single, unified record per book

- **Thematic Extraction**  
  Filters for specific clinical or qualitative features (e.g. body sensations) directly at the source with **full-context quotes**

- **Accuracy Auditing**  
  Integrated "Trust Score" monitoring ensures the AI's output remains a reliable source of truth

## ⚡ QuickStart Guide

### 1. Environment Setup

```bash
# Navigate to project and activate environment
cd /path/to/your/project
source /path/to/env/bin/activate

# Install Persistent API Keys (run once)
echo 'export OPENAI_API_KEY="your_actual_key"' >> ~/.zshrc
source ~/.zshrc
```

💡 **Note**: If using VS Code, make sure the interpreter is set to your active environment path to avoid "Ghost Environment" errors.

### 2. Prepare Data

- Place book folders inside your data input directory
- **Naming Convention**: `BookTitle_AuthorName/`
- **Content**: High-resolution images of book pages

### 3. Step 1 – High-Fidelity Extraction

Converts images → structured JSON data objects

```bash
python stage1_extract_to_json.py
```

**Result**: Creates page-level JSON files containing verbatim text + metadata

### 4. Step 2 – Synthesis & Filtering

Consolidates the library and extracts thematic insights

```bash
python stage2_consolidate_and_filter.py
```

**Result**: Generates the three master reports (see Output Structure below)

## 📂 Output Structure

The pipeline creates a timestamped output folder containing three essential JSON summaries:

1. **`1_library_high_level.json`**  
   Global progress report  
   → page ranges, unique page counts, total word counts per book

2. **`2_thematic_report.json`**  
   Filtered insights (e.g. body sensations)  
   → organized by book and page number, with **full verbatim quotes** and context

3. **`3_master_texts.json`**  
   Consolidated file containing the **complete, ordered text** for every book in the library

## ✅ Success Checklist

- [ ] Zero duplication — each physical page exists only **once** in the final summary
- [ ] Full traceability — every finding links back to a specific page number + source image
- [ ] Human-in-the-loop ready — use the built-in accuracy audit scripts to periodically verify AI ratings

---

Built with focus on **data provenance**, **reproducibility** and **long-term research value**.
```

Feel free to add badges, screenshots, a license section, or a table of contents later. This version should look clean and professional on GitHub right away.
