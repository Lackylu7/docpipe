from __future__ import annotations

from pathlib import Path

from docpipe.models import EngineName, ResolvedEngineName


MARKITDOWN_EXTENSIONS = {
    ".docx",
    ".pptx",
    ".xlsx",
    ".xls",
    ".csv",
    ".html",
    ".htm",
    ".txt",
    ".json",
    ".xml",
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".wav",
    ".mp3",
    ".m4a",
}

DOCLING_EXTENSIONS = {".pdf", ".docx", ".pptx", ".html", ".htm", ".png", ".jpg", ".jpeg"}


class ConversionError(RuntimeError):
    pass


def choose_engine(path: Path, requested: EngineName) -> ResolvedEngineName:
    if requested in {"markitdown", "docling"}:
        return requested
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "docling"
    if suffix in MARKITDOWN_EXTENSIONS:
        return "markitdown"
    return "markitdown"


def fallback_engine(engine: ResolvedEngineName) -> ResolvedEngineName:
    return "docling" if engine == "markitdown" else "markitdown"


def convert_with_engine(path: Path, engine: ResolvedEngineName) -> str:
    if engine == "markitdown":
        return _convert_markitdown(path)
    return _convert_docling(path)


def _convert_markitdown(path: Path) -> str:
    try:
        from markitdown import MarkItDown
    except ImportError as exc:
        raise ConversionError("MarkItDown is not installed. Run: pip install markitdown") from exc

    result = MarkItDown().convert(str(path))
    text = getattr(result, "text_content", None) or getattr(result, "markdown", None)
    if text is None:
        raise ConversionError("MarkItDown returned no Markdown text.")
    return str(text)


def _convert_docling(path: Path) -> str:
    try:
        from docling.document_converter import DocumentConverter
    except ImportError as exc:
        raise ConversionError("Docling is not installed. Run: pip install docling") from exc

    result = DocumentConverter().convert(str(path))
    document = getattr(result, "document", None)
    if document is None:
        raise ConversionError("Docling returned no document object.")
    if hasattr(document, "export_to_markdown"):
        return str(document.export_to_markdown())
    if hasattr(document, "export_to_text"):
        return str(document.export_to_text())
    raise ConversionError("Docling document cannot be exported to Markdown.")
