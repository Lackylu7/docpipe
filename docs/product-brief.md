# DocPipe Product Brief

## Positioning

DocPipe is a local-first document preprocessing tool for enterprise AI knowledge bases.
It turns messy documents into Markdown, JSON, and RAG chunks with a reviewable report.

## Target Customers

- small and mid-sized companies building internal AI assistants
- teams using Dify, FastGPT, RAGFlow, Coze, or custom RAG systems
- agencies that clean and migrate client documents into knowledge bases

## MVP Scope

- batch upload or folder conversion
- automatic engine routing between MarkItDown and Docling
- plugin-style engine registry for future adapters
- Markdown and JSON export
- RAG chunk JSONL export
- quality report for success, failure, engine choice, chunks, tables, and headings
- lightweight quality scoring and review warnings
- starter export folders for common knowledge-base workflows
- timestamped job folders for repeatable batch processing
- Windows local startup script
- Docker deployment files
- validation checklist for real customer samples
- structured chunks with heading paths, token estimates, and table flags

## Not In Scope Yet

- user accounts
- SaaS billing
- cloud storage
- permission management
- custom OCR model training
- direct vendor lock-in to one RAG platform

## Commercial Packaging

Start with service-led delivery:

- document cleanup project: 3000-20000 CNY
- private local deployment: 9800 CNY+
- monthly maintenance: 1000-5000 CNY

Then productize export templates and industry-specific chunking rules.

## Next Product Risks

- Export files are starter formats, not guaranteed one-click imports for every vendor.
- Enterprise sales will still need customer-specific import adapters and private
  deployment hardening.
