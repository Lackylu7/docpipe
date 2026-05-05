# Benchmarks

Benchmarks should be treated as directional. Performance depends on file type, parser
route, CPU, memory, and whether OCR/model assets need to be downloaded.

## Current Local Case Benchmark

Environment:

- Windows 11
- Python 3.12.10
- local virtual environment

Command:

```powershell
Measure-Command {
  .\.venv\Scripts\python.exe -m docpipe.cli convert .\examples\company-knowledge-base `
    --output .\outputs\company-demo `
    --workflow-template enterprise-policy `
    --language zh-CN `
    --no-job-dir
}
```

Dataset:

- 6 synthetic Chinese company documents
- Markdown, CSV, TXT, and HTML

Result from the latest local run:

- elapsed time: 2.09 seconds
- total files: 6
- succeeded / failed: 6 / 0
- chunk count: 17
- files requiring review: 3
- parser engines used: MarkItDown

## Next Benchmark Targets

- 50 mixed Office/text files
- table-heavy PDF set
- scanned PDF set
- bilingual Chinese/English folder

## Synthetic Mixed-Company Load Test

Command:

```powershell
Measure-Command {
  .\.venv\Scripts\python.exe -m docpipe.cli stress-demo --files 80 `
    --language zh-CN `
    --workflow-template operations-sop
}
```

Dataset:

- 80 generated synthetic company documents
- 8 folders: policy, support, product, sales, finance, legal, training, operations
- Markdown, TXT, CSV, HTML, and JSON

Result from the latest local run:

- elapsed time: 9.40 seconds
- total files: 80
- succeeded / failed: 80 / 0
- chunk count: 176
- files requiring review: 32
- parser engines used: MarkItDown
- export ZIP created: yes

This load test is useful for regression checks, but it is synthetic. It should be paired
with real PDF, Word, Excel, PowerPoint, scanned, and table-heavy files before customer
claims are made.
