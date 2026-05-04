# DocPipe

DocPipe is an enterprise document preprocessing tool for AI knowledge bases. It uses
MarkItDown for broad, fast conversion and Docling for structure-heavy documents such as
PDFs with tables, layout, and OCR needs.

The goal is not to rewrite either project. DocPipe adds the missing product layer:

- one local web UI for batch conversion
- automatic engine routing
- Markdown and JSON export
- RAG-ready chunk generation
- conversion quality report
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

## Product Direction

The first commercial version should stay focused:

- batch conversion for enterprise document folders
- private local deployment
- export packs for Dify, FastGPT, RAGFlow, Coze, and custom RAG systems
- industry templates for contracts, training material, product manuals, and support docs

## License

This project is MIT licensed. MarkItDown and Docling are separate open-source projects
with their own licenses and notices.
