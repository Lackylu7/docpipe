# Synthetic Load Test

DocPipe includes a deterministic synthetic dataset generator for testing batch behavior
without using private customer files.

The generated folder imitates a mixed company knowledge base:

- policy documents
- support FAQs
- product manuals
- sales enablement notes
- finance and audit notes
- legal contract notes
- onboarding material
- operations SOPs

It writes Markdown, TXT, CSV, HTML, and JSON files into department folders, then converts
the whole folder through the normal DocPipe pipeline.

## Run

```powershell
docpipe stress-demo --files 80 --language zh-CN
```

Or with the local shortcut environment:

```powershell
.\.venv\Scripts\python.exe -m docpipe.cli stress-demo --files 120 --workflow-template operations-sop --language zh-CN
```

Outputs are written to:

```text
outputs/stress-demo/
  input/
  converted/
```

## What This Proves

The stress demo checks:

- recursive folder discovery
- mixed file-type conversion
- source metadata using relative paths
- same-name output collision protection
- RAG chunk creation
- review checklist generation
- export ZIP creation

It does not replace real customer validation. PDF, Word, Excel, PowerPoint, scanned files,
and table-heavy source documents still need separate validation before commercial use.
