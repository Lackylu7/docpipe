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
- 100 mixed files
- table-heavy PDF set
- scanned PDF set
- bilingual Chinese/English folder
