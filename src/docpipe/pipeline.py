from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from docpipe.chunker import chunk_markdown, quality_metrics
from docpipe.engines import choose_engine, convert_with_engine, fallback_engines
from docpipe.models import BatchReport, ConversionResult, EngineName, SourceProfile


SUPPORTED_EXTENSIONS = {
    ".pdf",
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


def discover_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    return sorted(
        path
        for path in input_path.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def convert_file(
    source_path: Path,
    output_dir: Path,
    engine: EngineName = "auto",
    max_chunk_chars: int = 1400,
    max_retries: int = 1,
) -> ConversionResult:
    source_path = source_path.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    requested_engine = engine
    selected_engine = choose_engine(source_path, engine)
    source_profile = profile_source(source_path)
    attempts = 0

    try:
        engines = [selected_engine] if engine != "auto" else fallback_engines(source_path, selected_engine)

        last_error: Exception | None = None
        markdown = ""
        used_engine = selected_engine
        for candidate in engines:
            for _ in range(max_retries + 1):
                attempts += 1
                try:
                    markdown = convert_with_engine(source_path, candidate)
                    used_engine = candidate
                    last_error = None
                    break
                except Exception as exc:
                    last_error = exc
            if last_error is None:
                break
        if last_error is not None:
            raise last_error

        chunks = chunk_markdown(markdown, max_chars=max_chunk_chars)
        metrics = quality_metrics(markdown, chunks)
        stem = _safe_stem(source_path)
        markdown_path = output_dir / f"{stem}.md"
        json_path = output_dir / f"{stem}.json"
        markdown_path.write_text(markdown, encoding="utf-8")

        result = ConversionResult(
            source_path=str(source_path),
            output_markdown_path=str(markdown_path),
            output_json_path=str(json_path),
            requested_engine=requested_engine,
            used_engine=used_engine,
            status="success",
            markdown=markdown,
            chunks=chunks,
            metrics=metrics,
            source_profile=source_profile,
            attempts=attempts,
        )
        json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        return result
    except Exception as exc:
        return ConversionResult(
            source_path=str(source_path),
            requested_engine=requested_engine,
            used_engine=selected_engine,
            status="failed",
            error=str(exc),
            source_profile=source_profile,
            attempts=max(attempts, 1),
        )


def convert_batch(
    input_path: Path,
    output_dir: Path,
    engine: EngineName = "auto",
    max_chunk_chars: int = 1400,
    job_id: str | None = None,
    create_job_dir: bool = False,
    max_retries: int = 1,
) -> BatchReport:
    job_id = job_id or _new_job_id()
    output_dir = output_dir / job_id if create_job_dir else output_dir
    files = discover_files(input_path)
    results = [
        convert_file(
            path,
            output_dir=output_dir,
            engine=engine,
            max_chunk_chars=max_chunk_chars,
            max_retries=max_retries,
        )
        for path in files
    ]
    report = BatchReport(
        job_id=job_id,
        output_dir=str(output_dir.resolve()),
        total=len(results),
        succeeded=sum(1 for result in results if result.status == "success"),
        failed=sum(1 for result in results if result.status == "failed"),
        results=results,
    )
    write_reports(report, output_dir)
    return report


def write_reports(report: BatchReport, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "conversion_report.json").write_text(
        report.model_dump_json(indent=2), encoding="utf-8"
    )
    lines = [
        "# Conversion Report",
        "",
        f"- Total: {report.total}",
        f"- Succeeded: {report.succeeded}",
        f"- Failed: {report.failed}",
        f"- Job ID: {report.job_id}",
        f"- Output: {report.output_dir}",
        "",
        "| File | Status | Engine | Score | Warnings | Chunks | Attempts | Error |",
        "| --- | --- | --- | ---: | --- | ---: | ---: | --- |",
    ]
    for result in report.results:
        chunks = result.metrics.chunks if result.metrics else 0
        score = result.metrics.quality_score if result.metrics else ""
        warnings = ", ".join(result.metrics.warnings) if result.metrics else ""
        error = (result.error or "").replace("\n", " ")[:140]
        lines.append(
            f"| {Path(result.source_path).name} | {result.status} | "
            f"{result.used_engine or ''} | {score} | {warnings} | {chunks} | "
            f"{result.attempts} | {error} |"
        )
    (output_dir / "conversion_report.md").write_text("\n".join(lines), encoding="utf-8")


def export_rag_pack(report: BatchReport, output_dir: Path) -> Path:
    rows = []
    for result in report.results:
        if result.status != "success":
            continue
        for chunk in result.chunks:
            rows.append(
                {
                    "source": result.source_path,
                    "filename": Path(result.source_path).name,
                    "engine": result.used_engine,
                    "chunk_index": chunk.index,
                    "heading": chunk.heading,
                    "heading_path": chunk.heading_path,
                    "token_estimate": chunk.token_estimate,
                    "contains_table": chunk.contains_table,
                    "text": chunk.text,
                }
            )
    path = output_dir / "rag_chunks.jsonl"
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")
    return path


def _safe_stem(path: Path) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in path.stem)


def _new_job_id() -> str:
    return datetime.now(UTC).strftime("job-%Y%m%d-%H%M%S")


def profile_source(path: Path) -> SourceProfile:
    preview = None
    if path.suffix.lower() in {".txt", ".md", ".csv", ".json", ".xml", ".html", ".htm"}:
        try:
            preview = path.read_text(encoding="utf-8", errors="replace")[:4000]
        except OSError:
            preview = None
    return SourceProfile(
        size_bytes=path.stat().st_size,
        extension=path.suffix.lower(),
        text_preview=preview,
    )
