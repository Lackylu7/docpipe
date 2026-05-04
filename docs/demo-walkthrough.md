# DocPipe Demo Walkthrough

This walkthrough shows the product story a new user should understand in about three
minutes: messy documents go in, reviewable knowledge-base import files come out.

## 1. Install

```powershell
cd docpipe
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## 2. Run The Included Demo

```powershell
docpipe demo
```

Or on Windows:

```powershell
scripts\run_demo.ps1
```

The command converts the included `samples/` folder and writes output to `outputs/demo/`.

## 3. Inspect The Results

Open these files first:

- `outputs/demo/conversion_report.md`
- `outputs/demo/rag_chunks.jsonl`
- `outputs/demo/exports/review_checklist.md`
- `outputs/demo/exports/docpipe_export_pack.zip`

For a committed example, see `docs/demo-result-preview.md`.

The report answers:

- which files converted successfully
- which route was used
- how many chunks were created
- whether any file needs review
- what the final export bundle contains

## 4. Try The Web App

```powershell
python -m streamlit run src/docpipe/web.py
```

Upload files from `samples/`, click Convert, then inspect:

- quality metrics
- review warnings
- Markdown preview
- chunk table
- export ZIP download
- review checklist download

## 5. What To Show A Customer

Use this short story:

> DocPipe prepares company documents for AI knowledge bases. It converts mixed files,
> creates RAG chunks, highlights risky conversions, and packages the result into a
> reviewable import bundle that can stay inside the customer's private environment.
