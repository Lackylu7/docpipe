from pathlib import Path

from docpipe.engines import choose_engine
from docpipe.pipeline import discover_files


def test_choose_engine_defaults_pdf_to_docling() -> None:
    assert choose_engine(Path("contract.pdf"), "auto") == "docling"


def test_choose_engine_defaults_office_to_markitdown() -> None:
    assert choose_engine(Path("deck.pptx"), "auto") == "markitdown"


def test_choose_engine_allows_planned_adapters() -> None:
    assert choose_engine(Path("contract.pdf"), "mineru") == "mineru"


def test_discover_files_filters_supported_extensions(tmp_path: Path) -> None:
    supported = tmp_path / "a.pdf"
    ignored = tmp_path / "a.exe"
    supported.write_text("fake", encoding="utf-8")
    ignored.write_text("fake", encoding="utf-8")

    assert discover_files(tmp_path) == [supported]
