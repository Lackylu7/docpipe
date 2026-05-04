# Demo Result Preview

This is an example result from running:

```powershell
docpipe demo --output outputs/demo
```

## Summary

- Total files: 5
- Succeeded: 5
- Failed: 0
- Export ZIP: `outputs/demo/exports/docpipe_export_pack.zip`
- Review checklist: `outputs/demo/exports/review_checklist.md`
- Handoff guide: `outputs/demo/exports/handoff_guide.md`

## Conversion Report

| File | Status | Engine | Score | Warnings | Chunks |
| --- | --- | --- | ---: | --- | ---: |
| `company-policy.md` | success | markitdown | 90 | tiny_chunks | 5 |
| `product-manual.txt` | success | markitdown | 100 |  | 1 |
| `sales-faq.html` | success | markitdown | 90 | tiny_chunks | 4 |
| `support-tickets.csv` | success | markitdown | 100 |  | 1 |
| `vendor-evaluation.json` | success | markitdown | 100 |  | 1 |

## Review Checklist

| File | Status | Score | Warnings | Recommended action |
| --- | --- | ---: | --- | --- |
| `company-policy.md` | success | 90 | tiny_chunks | Open the Markdown preview and confirm content quality. |
| `sales-faq.html` | success | 90 | tiny_chunks | Open the Markdown preview and confirm content quality. |

## What This Shows

The included demo is intentionally small, but it exercises the full product workflow:

- discover mixed files from a folder
- convert each file into Markdown and JSON
- create RAG chunks
- score conversion quality
- create review tasks for risky files
- generate vendor starter exports
- write a template-specific handoff guide
- package the handoff ZIP
