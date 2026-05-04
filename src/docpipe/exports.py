from __future__ import annotations

import csv
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from docpipe.models import BatchReport, ConversionResult


def export_knowledge_pack(report: BatchReport, output_dir: Path) -> dict[str, str]:
    """Write vendor-friendly starter exports without locking the pipeline to one platform."""
    export_dir = output_dir / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    chunks = _chunk_rows(report)
    paths = {}
    paths["generic_jsonl"] = _write_jsonl(export_dir / "generic_chunks.jsonl", chunks)
    paths["dify_csv"] = _write_csv(export_dir / "dify_chunks.csv", chunks)
    paths["coze_csv"] = _write_csv(export_dir / "coze_chunks.csv", chunks)
    paths["fastgpt_jsonl"] = _write_jsonl(export_dir / "fastgpt_chunks.jsonl", chunks)
    paths["ragflow_jsonl"] = _write_jsonl(export_dir / "ragflow_chunks.jsonl", chunks)
    paths["review_checklist_csv"] = _write_review_checklist_csv(
        export_dir / "review_checklist.csv", report
    )
    paths["review_checklist_md"] = _write_review_checklist_md(
        export_dir / "review_checklist.md", report
    )
    paths["manifest"] = _write_manifest(export_dir / "manifest.json", report, chunks)
    paths["zip"] = _write_export_zip(export_dir / "docpipe_export_pack.zip", output_dir)
    return {name: str(path) for name, path in paths.items()}


def _chunk_rows(report: BatchReport) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for result in report.results:
        if result.status != "success":
            continue
        for chunk in result.chunks:
            rows.append(
                {
                    "content": chunk.text,
                    "source": result.source_path,
                    "filename": Path(result.source_path).name,
                    "engine": result.used_engine,
                    "chunk_index": chunk.index,
                    "heading": chunk.heading or "",
                    "heading_path": " > ".join(chunk.heading_path),
                    "token_estimate": chunk.token_estimate,
                    "contains_table": chunk.contains_table,
                    "quality_score": result.metrics.quality_score if result.metrics else None,
                }
            )
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> Path:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows),
        encoding="utf-8",
    )
    return path


def _write_csv(path: Path, rows: list[dict[str, object]]) -> Path:
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "content",
                "source",
                "filename",
                "engine",
                "chunk_index",
                "heading",
                "heading_path",
                "token_estimate",
                "contains_table",
                "quality_score",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


def _write_manifest(path: Path, report: BatchReport, rows: list[dict[str, object]]) -> Path:
    review_count = sum(1 for result in report.results if _needs_review(result))
    payload = {
        "job_id": report.job_id,
        "created_at": report.created_at,
        "total_files": report.total,
        "succeeded": report.succeeded,
        "failed": report.failed,
        "chunk_count": len(rows),
        "review_required": review_count,
        "formats": {
            "generic_jsonl": "Vendor-neutral JSONL, one chunk per line.",
            "dify_csv": "CSV starter format with content and metadata columns.",
            "coze_csv": "CSV starter format with content and metadata columns.",
            "fastgpt_jsonl": "JSONL starter format for custom import adapters.",
            "ragflow_jsonl": "JSONL starter format for custom import adapters.",
            "review_checklist_csv": "Files that should be checked before knowledge-base import.",
            "review_checklist_md": "Human-readable review checklist for handoff.",
            "zip": "Portable handoff bundle containing reports, exports, Markdown, and JSON output.",
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _review_rows(report: BatchReport) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for result in report.results:
        if not _needs_review(result):
            continue
        warnings = ", ".join(result.metrics.warnings) if result.metrics else ""
        rows.append(
            {
                "filename": result.filename,
                "status": result.status,
                "engine": result.used_engine or "",
                "score": result.metrics.quality_score if result.metrics else "",
                "warnings": warnings,
                "error": result.error or "",
                "attempts": result.attempts,
                "source": result.source_path,
                "recommended_action": _recommended_action(result.status, warnings, result.error),
            }
        )
    return rows


def _write_review_checklist_csv(path: Path, report: BatchReport) -> Path:
    fieldnames = [
        "filename",
        "status",
        "engine",
        "score",
        "warnings",
        "error",
        "attempts",
        "source",
        "recommended_action",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(_review_rows(report))
    return path


def _write_review_checklist_md(path: Path, report: BatchReport) -> Path:
    rows = _review_rows(report)
    lines = [
        "# Review Checklist",
        "",
        "Check these files before importing the export pack into a knowledge base.",
        "",
    ]
    if not rows:
        lines.append("No files require manual review.")
    else:
        lines.extend(
            [
                "| File | Status | Score | Warnings | Recommended action |",
                "| --- | --- | ---: | --- | --- |",
            ]
        )
        for row in rows:
            lines.append(
                f"| {row['filename']} | {row['status']} | {row['score']} | "
                f"{_escape_table(str(row['warnings']))} | "
                f"{_escape_table(str(row['recommended_action']))} |"
            )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_export_zip(path: Path, output_dir: Path) -> Path:
    path = path.resolve()
    output_dir = output_dir.resolve()
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        for item in sorted(output_dir.rglob("*")):
            if not item.is_file() or item == path:
                continue
            archive.write(item, item.relative_to(output_dir))
    return path


def _needs_review(result: ConversionResult) -> bool:
    return result.status == "failed" or not result.metrics or result.metrics.review_required


def _recommended_action(status: str, warnings: str, error: str | None) -> str:
    if status == "failed":
        return "Retry with another route or inspect the source file."
    if "possible_table_loss" in warnings:
        return "Compare tables against the source document."
    if "long_document_without_headings" in warnings:
        return "Add headings or split the source before import."
    if error:
        return "Review conversion details before import."
    return "Open the Markdown preview and confirm content quality."


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
