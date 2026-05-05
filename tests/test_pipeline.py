from pathlib import Path

from docpipe.engines import choose_engine
from docpipe.pipeline import convert_batch, discover_files


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


def test_convert_batch_uses_relative_source_labels_and_unique_outputs(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    (input_dir / "team-a").mkdir(parents=True)
    (input_dir / "team-b").mkdir(parents=True)
    (input_dir / "team-a" / "policy.txt").write_text("Team A policy notes", encoding="utf-8")
    (input_dir / "team-b" / "policy.txt").write_text("Team B policy notes", encoding="utf-8")

    report = convert_batch(input_dir, output_dir, engine="markitdown", create_job_dir=False)

    assert report.total == 2
    assert {result.source_path for result in report.results} == {
        "team-a/policy.txt",
        "team-b/policy.txt",
    }
    assert len({result.output_markdown_path for result in report.results}) == 2
    assert (output_dir / "team-a_policy.md").exists()
    assert (output_dir / "team-b_policy.md").exists()
