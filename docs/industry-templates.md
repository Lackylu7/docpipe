# Industry Templates

DocPipe workflow templates turn a generic converter into a repeatable customer delivery
flow. Each template controls the default chunk size and the review guidance written into
`exports/handoff_guide.md`.

## Available Templates

| Key | Best for | Default chunk size |
| --- | --- | ---: |
| `general` | mixed company folders | 1400 |
| `enterprise-policy` | HR policies, SOPs, compliance manuals, internal rules | 1100 |
| `support-faq` | ticket exports, help-center pages, FAQ cleanup | 900 |
| `product-manual` | manuals, onboarding guides, release notes, training material | 1600 |

## CLI Usage

List templates:

```powershell
docpipe templates
```

Run the included demo with the enterprise policy template:

```powershell
docpipe demo --workflow-template enterprise-policy
```

Convert a customer folder with the support FAQ template:

```powershell
docpipe convert .\customer-docs --workflow-template support-faq
```

## Handoff Guide

Every export pack now includes:

```text
exports/handoff_guide.md
```

The guide gives the customer:

- selected workflow template
- batch summary
- review focus
- recommended handoff steps
- files to open first
- import caution for vendor-specific field mapping

This is intentionally service-friendly. It helps a consultant, agency, or internal AI
team explain what was processed and what should be checked before production import.
