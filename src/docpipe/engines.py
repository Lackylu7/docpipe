from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class EngineAdapter:
    name: ResolvedEngineName
    extensions: set[str]
    priority: int
    description: str

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions

    def convert(self, path: Path) -> str:
        if self.name == "markitdown":
            return _convert_markitdown(path)
        if self.name == "docling":
            return _convert_docling(path)
        raise ConversionError(
            f"Engine '{self.name}' is not installed. Add its adapter before using it."
        )


ENGINE_REGISTRY: dict[ResolvedEngineName, EngineAdapter] = {
    "markitdown": EngineAdapter(
        name="markitdown",
        extensions=MARKITDOWN_EXTENSIONS,
        priority=20,
        description="Fast broad conversion for Office, web, text, images, and audio.",
    ),
    "docling": EngineAdapter(
        name="docling",
        extensions=DOCLING_EXTENSIONS,
        priority=10,
        description="Structure-aware conversion for PDF, layout, and table-heavy documents.",
    ),
    "unstructured": EngineAdapter(
        name="unstructured",
        extensions=set(),
        priority=90,
        description="Planned optional adapter for Unstructured document ETL.",
    ),
    "mineru": EngineAdapter(
        name="mineru",
        extensions=set(),
        priority=91,
        description="Planned optional adapter for MinerU PDF/OCR pipelines.",
    ),
    "marker": EngineAdapter(
        name="marker",
        extensions=set(),
        priority=92,
        description="Planned optional adapter for Marker PDF-to-Markdown pipelines.",
    ),
}


def choose_engine(path: Path, requested: EngineName) -> ResolvedEngineName:
    if requested != "auto":
        return requested
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "docling"
    if suffix in MARKITDOWN_EXTENSIONS:
        return "markitdown"
    candidates = [
        adapter for adapter in ENGINE_REGISTRY.values() if adapter.supports(path) and adapter.priority < 90
    ]
    if not candidates:
        return "markitdown"
    return sorted(candidates, key=lambda adapter: adapter.priority)[0].name


def fallback_engines(path: Path, primary: ResolvedEngineName) -> list[ResolvedEngineName]:
    engines = [primary]
    for adapter in sorted(ENGINE_REGISTRY.values(), key=lambda item: item.priority):
        if adapter.priority >= 90 or adapter.name == primary:
            continue
        if adapter.supports(path) or adapter.name == "markitdown":
            engines.append(adapter.name)
    return engines


def fallback_engine(engine: ResolvedEngineName) -> ResolvedEngineName:
    return "docling" if engine == "markitdown" else "markitdown"


def convert_with_engine(path: Path, engine: ResolvedEngineName) -> str:
    return ENGINE_REGISTRY[engine].convert(path)


def list_engines() -> list[EngineAdapter]:
    return sorted(ENGINE_REGISTRY.values(), key=lambda adapter: adapter.priority)


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
