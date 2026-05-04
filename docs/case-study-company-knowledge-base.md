# Case Study: Company Knowledge Base Demo

This case study uses the synthetic Chinese demo set in:

```text
examples/company-knowledge-base/
```

The folder contains only files that should be processed as customer-like source
documents. It is safe synthetic content, not customer data.

## Scenario

A small company wants to build an internal AI assistant. The source material is mixed:

- HR policy
- support FAQ
- product manual
- sales playbook
- training web page
- document inventory table

The team needs a local workflow that creates Markdown, RAG chunks, import starter files,
and review notes before the material enters a knowledge-base system.

## Run

```powershell
docpipe convert .\examples\company-knowledge-base --output .\outputs\company-demo --workflow-template enterprise-policy --language zh-CN
```

## Expected Outputs

- per-file Markdown
- per-file JSON metadata
- `conversion_report.md`
- `rag_chunks.jsonl`
- `exports/review_checklist.md`
- `exports/handoff_guide.md`
- `exports/docpipe_export_pack.zip`

## Demo Story

Use this story when showing the project:

> DocPipe takes a mixed folder of company documents, converts it locally, flags files
> that need human review, and packages a knowledge-base handoff bundle that a business
> owner can inspect before import.
