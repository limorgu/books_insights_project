# AI-Powered Book Dataset Builder

This tool automates turning raw book page images into a clean, structured, research-ready JSON dataset.
⚡ Turn raw book page images into a clean, structured, research-ready dataset — fast and cost-efficient.

This repo provides a **three-stage pipeline** that:
- Extracts text & structure from images
- Audits for completeness (finds gaps)
- Precisely fills only missing pages

Designed to be **resume-aware** (skips already processed pages), **audit-driven**, and **API-cost-aware**.

### Get Started in 3 Steps

1. **Extract** — Convert images to structured JSON  
   ```bash
   python stage1_ingestion.py

2. **Audit** — Check for missing pages & completion
   ```bash
   python stage2_audit.py

   → Produces gap_analysis_report.json

4. **Fill Gaps** — Process only the missing pages
   ```bash
   python stage3_gap_filler.py

   → Interactive CLI to select books

Full Instructions
→ Detailed environment setup, folder naming rules, API key config, quality checks, and success checklist:
QuickStart Guide → QUICKSTART.md



   
