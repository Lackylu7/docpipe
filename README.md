# DocPipe

DocPipe is an enterprise document preprocessing tool for AI knowledge bases. It uses
MarkItDown for broad, fast conversion and Docling for structure-heavy documents such as
PDFs with tables, layout, and OCR needs.

The goal is not to rewrite either project. DocPipe adds the missing product layer:

- one local web UI for batch conversion
- automatic engine routing
- plugin-style engine registry
- Markdown and JSON export
- RAG-ready chunk generation
- conversion quality report
- basic quality scoring and review warnings
- starter export pack for knowledge-base imports
- private, local-first workflow for enterprise files

## When To Use Which Engine

| File type | Default engine | Why |
| --- | --- | --- |
| PDF | Docling | Better layout, tables, reading order, and structured output |
| Word / Excel / PowerPoint | MarkItDown | Fast Office-to-Markdown conversion |
| HTML / text / CSV / JSON | MarkItDown | Lightweight text extraction |
| Unknown | MarkItDown first, Docling fallback | Broad compatibility |

## Quick Start

Use Python 3.11 or 3.12. Some document AI dependencies may lag behind the newest
Python releases.

```powershell
cd docpipe
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Run the web UI:

```powershell
python -m streamlit run src/docpipe/web.py
```

Or use the Windows launcher:

```powershell
scripts\run_web.ps1
```

Run the CLI:

```powershell
docpipe convert .\samples --output .\outputs --engine auto
```

## Output

For every converted file, DocPipe writes:

- `*.md`: cleaned Markdown
- `*.json`: metadata, chunks, and quality metrics

It also writes:

- `conversion_report.json`
- `conversion_report.md`
- `rag_chunks.jsonl`
- `exports/generic_chunks.jsonl`
- `exports/dify_chunks.csv`
- `exports/coze_chunks.csv`
- `exports/fastgpt_chunks.jsonl`
- `exports/ragflow_chunks.jsonl`
- `exports/manifest.json`

Each conversion run can be written into a timestamped job folder, making it easier to
review historical runs and reprocess failed batches.

## Quality Signals

DocPipe adds lightweight quality checks so teams can review risky conversions before
loading them into a knowledge base:

- empty or very short output
- possible encoding noise
- replacement characters
- long documents without headings
- missing chunks

These checks are intentionally conservative. They do not claim semantic correctness;
they highlight documents that deserve human review.

## Product Direction

The first commercial version should stay focused:

- batch conversion for enterprise document folders
- private local deployment
- export packs for Dify, FastGPT, RAGFlow, Coze, and custom RAG systems
- industry templates for contracts, training material, product manuals, and support docs

## Deployment And Validation

- `docs/deployment.md`: Windows and Docker deployment notes
- `docs/validation.md`: real-document validation checklist
- `docs/smoke-test.md`: latest local smoke-test result
- `docs/adapter-architecture.md`: parser adapter design

Docker quick start:

```powershell
docker compose up --build
```

## License

This project is MIT licensed. MarkItDown and Docling are separate open-source projects
with their own licenses and notices.
