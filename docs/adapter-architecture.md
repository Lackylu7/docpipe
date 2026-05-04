# Adapter Architecture

DocPipe keeps document parsers behind a small engine adapter registry.

Current production adapters:

- `markitdown`: broad and fast conversion for Office, web, text, image, and audio files
- `docling`: structure-aware conversion for PDFs and layout-heavy documents

Planned optional adapters:

- `unstructured`: enterprise document ETL and partitioning
- `mineru`: PDF/OCR-heavy workflows
- `marker`: PDF-to-Markdown workflows

## Why This Shape

DocPipe should not become a fork of every parser. Each parser remains an external
dependency or optional integration. DocPipe owns:

- routing
- retries
- output normalization
- chunk metadata
- quality reports
- knowledge-base export packs

## Adapter Contract

An adapter must:

- declare a stable name
- declare supported extensions
- expose a `convert(path: Path) -> str` method
- return Markdown or raise a clear `ConversionError`

## Routing

`auto` mode picks the best registered production adapter for a file:

- PDF defaults to Docling
- common Office/web/text formats default to MarkItDown
- failures can fall back to another compatible production adapter

Planned adapters are visible in the registry but not used automatically until their
implementation and dependencies are added.
