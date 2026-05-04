# Limitations

DocPipe is useful for local pilots and service-led document cleanup, but it is still an
MVP. These limitations should be clear before customer use.

## Document Quality

- Scanned PDFs and image-heavy files may need OCR-specific tuning.
- Complex tables should be checked against the original source.
- Documents without headings may produce less useful chunks.
- Very short sections may trigger review warnings even when the conversion is acceptable.
- Audio and image support depends on the installed parser capabilities.

## Import Targets

Export files are starter formats. Dify, Coze, FastGPT, RAGFlow, and custom RAG systems may
still require field mapping, upload scripts, or customer-specific import adapters.

## Scale

The current Web app runs conversion in the foreground. Large folders should be tested
before use in a customer environment. Future versions should add a background job queue,
retry-from-history, and clearer progress reporting.

## Security

DocPipe is local-first by default, but the operator is responsible for:

- running it in the correct customer environment
- protecting output folders
- reviewing whether optional cloud parsers or models are enabled
- deleting temporary files according to customer policy

## Production Readiness

DocPipe does not yet include user accounts, role-based permissions, audit logs, billing,
or enterprise SSO. For now, position it as a local/private deployment tool or
service-delivery accelerator.

