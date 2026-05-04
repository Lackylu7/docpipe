from __future__ import annotations

import csv
import json
from pathlib import Path

from docpipe.models import BatchReport


def export_knowledge_pack(report: BatchReport, output_dir: Path) -> dict[str, str]:
    """Write vendor-friendly starter exports without locking the pipeline to one platform."""
    export_dir = output_dir / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    chunks = _chunk_rows(report)
    paths = {
        "generic_jsonl": _write_jsonl(export_dir / "generic_chunks.jsonl", chunks),
        "dify_csv": _write_csv(export_dir / "dify_chunks.csv", chunks),
        "fastgpt_jsonl": _write_jsonl(export_dir / "fastgpt_chunks.jsonl", chunks),
        "ragflow_jsonl": _write_jsonl(export_dir / "ragflow_chunks.jsonl", chunks),
        "manifest": _write_manifest(export_dir / "manifest.json", report, chunks),
    }
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
                "quality_score",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


def _write_manifest(path: Path, report: BatchReport, rows: list[dict[str, object]]) -> Path:
    payload = {
        "job_id": report.job_id,
        "created_at": report.created_at,
        "total_files": report.total,
        "succeeded": report.succeeded,
        "failed": report.failed,
        "chunk_count": len(rows),
        "formats": {
            "generic_jsonl": "Vendor-neutral JSONL, one chunk per line.",
            "dify_csv": "CSV starter format with content and metadata columns.",
            "fastgpt_jsonl": "JSONL starter format for custom import adapters.",
            "ragflow_jsonl": "JSONL starter format for custom import adapters.",
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
