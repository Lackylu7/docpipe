# Smoke Test Result

Date: 2026-05-04

Environment:

- Windows 11
- Python 3.12.10
- MarkItDown 0.1.5
- Docling 2.92.0

Command:

```powershell
docpipe convert data\smoke-inputs --output outputs\smoke-v02 --engine auto --max-retries 1
```

Sample files:

| File | Type | Result | Engine |
| --- | --- | --- | --- |
| `onboarding.docx` | Word | success | Docling fallback |
| `policy.md` | Markdown | success | MarkItDown |
| `revenue.xlsx` | Excel | success | MarkItDown |
| `rollout.pptx` | PowerPoint | success | MarkItDown |
| `sales.csv` | CSV | success | MarkItDown |
| `smoke.pdf` | PDF | success | Docling |
| `support.html` | HTML | success | MarkItDown |

Generated outputs:

- per-file Markdown
- per-file JSON metadata
- `conversion_report.json`
- `conversion_report.md`
- `rag_chunks.jsonl`
- `exports/generic_chunks.jsonl`
- `exports/dify_chunks.csv`
- `exports/coze_chunks.csv`
- `exports/fastgpt_chunks.jsonl`
- `exports/ragflow_chunks.jsonl`
- `exports/manifest.json`
- structured chunk metadata: heading paths, token estimates, and table flags

Notes:

- Docling downloaded OCR and layout model assets on first run.
- Short synthetic samples correctly triggered `very_short_output` warnings.
- v0.2 smoke test succeeded with 7/7 files and generated 10 chunks.
- Real customer validation should use longer, messier documents with tables, scans,
  and mixed Chinese/English content.
