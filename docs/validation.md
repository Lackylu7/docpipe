# Validation Plan

Use this checklist before presenting DocPipe to a customer.

## Sample Set

Prepare at least:

- 2 PDFs with text
- 2 PDFs with tables
- 2 Word documents
- 2 Excel files
- 2 PowerPoint decks
- 2 HTML or Markdown files

## Checks

- Conversion succeeds.
- Markdown is readable.
- Tables remain understandable.
- Heading hierarchy is useful.
- `quality_score` is not hiding obvious failures.
- `warnings` flag suspicious outputs.
- `rag_chunks.jsonl` contains useful chunk text.
- Export files are created.
- Job folder contains reports and per-file JSON.

## Customer Demo Script

1. Upload a mixed batch of documents.
2. Show the conversion report.
3. Open one Markdown preview.
4. Show chunk preview.
5. Open `exports/manifest.json`.
6. Explain that vendor exports are starter formats and can be adapted to the customer's
   chosen knowledge-base platform.
