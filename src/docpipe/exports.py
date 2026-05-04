from __future__ import annotations

import csv
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from docpipe.i18n import Language
from docpipe.models import BatchReport, ConversionResult
from docpipe.templates import (
    get_template,
    template_description,
    template_handoff_steps,
    template_name,
    template_review_focus,
)


def export_knowledge_pack(
    report: BatchReport,
    output_dir: Path,
    workflow_template: str = "general",
    language: Language = "en",
) -> dict[str, str]:
    """Write vendor-friendly starter exports without locking the pipeline to one platform."""
    export_dir = output_dir / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    get_template(workflow_template)

    chunks = _chunk_rows(report)
    paths = {}
    paths["generic_jsonl"] = _write_jsonl(export_dir / "generic_chunks.jsonl", chunks)
    paths["dify_csv"] = _write_csv(export_dir / "dify_chunks.csv", chunks)
    paths["coze_csv"] = _write_csv(export_dir / "coze_chunks.csv", chunks)
    paths["fastgpt_jsonl"] = _write_jsonl(export_dir / "fastgpt_chunks.jsonl", chunks)
    paths["ragflow_jsonl"] = _write_jsonl(export_dir / "ragflow_chunks.jsonl", chunks)
    paths["review_checklist_csv"] = _write_review_checklist_csv(
        export_dir / "review_checklist.csv", report, language
    )
    paths["review_checklist_md"] = _write_review_checklist_md(
        export_dir / "review_checklist.md", report, language
    )
    paths["handoff_guide"] = _write_handoff_guide(
        export_dir / "handoff_guide.md", report, workflow_template, language
    )
    paths["manifest"] = _write_manifest(
        export_dir / "manifest.json", report, chunks, workflow_template, language
    )
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


def _write_manifest(
    path: Path,
    report: BatchReport,
    rows: list[dict[str, object]],
    workflow_template: str,
    language: Language,
) -> Path:
    review_count = sum(1 for result in report.results if _needs_review(result))
    template = get_template(workflow_template)
    payload = {
        "job_id": report.job_id,
        "created_at": report.created_at,
        "language": language,
        "workflow_template": template.key,
        "workflow_template_name": template.name,
        "workflow_template_display_name": template_name(template, language),
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
            "handoff_guide": "Template-specific import and review guide.",
            "zip": "Portable handoff bundle containing reports, exports, Markdown, and JSON output.",
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _review_rows(report: BatchReport, language: Language) -> list[dict[str, object]]:
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
                "recommended_action": _recommended_action(
                    result.status, warnings, result.error, language
                ),
            }
        )
    return rows


def _write_review_checklist_csv(path: Path, report: BatchReport, language: Language) -> Path:
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
        writer.writerows(_review_rows(report, language))
    return path


def _write_review_checklist_md(path: Path, report: BatchReport, language: Language) -> Path:
    rows = _review_rows(report, language)
    if language == "zh-CN":
        lines = ["# 复核清单", "", "导入知识库前，请优先检查以下文件。", ""]
        no_review = "没有需要人工复核的文件。"
        headers = "| 文件 | 状态 | 分数 | 警告 | 建议操作 |"
    else:
        lines = [
            "# Review Checklist",
            "",
            "Check these files before importing the export pack into a knowledge base.",
            "",
        ]
        no_review = "No files require manual review."
        headers = "| File | Status | Score | Warnings | Recommended action |"
    if not rows:
        lines.append(no_review)
    else:
        lines.extend(
            [
                headers,
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


def _write_handoff_guide(
    path: Path, report: BatchReport, workflow_template: str, language: Language
) -> Path:
    template = get_template(workflow_template)
    review_count = sum(1 for result in report.results if _needs_review(result))
    if language == "zh-CN":
        lines = [
            "# DocPipe 交付指南",
            "",
            f"工作流模板：**{template_name(template, language)}**",
            "",
            template_description(template, language),
            "",
            "## 批处理概览",
            "",
            f"- 任务 ID：`{report.job_id}`",
            f"- 文件总数：{report.total}",
            f"- 转换成功：{report.succeeded}",
            f"- 转换失败：{report.failed}",
            f"- 需要复核：{review_count}",
            "",
            "## 复核重点",
            "",
        ]
        lines.extend(f"- {item}" for item in template_review_focus(template, language))
        lines.extend(["", "## 建议交付步骤", ""])
        lines.extend(
            f"{index}. {step}"
            for index, step in enumerate(template_handoff_steps(template, language), start=1)
        )
        lines.extend(
            [
                "",
                "## 建议优先打开",
                "",
                "- `conversion_report.md`",
                "- `exports/review_checklist.md`",
                "- `rag_chunks.jsonl`",
                "- 目标知识库系统对应的导入文件",
                "",
                "## 导入提醒",
                "",
                "这些导出文件是通用起点，正式生产导入前可能仍需要按客户系统做字段映射。",
            ]
        )
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    lines = [
        "# DocPipe Handoff Guide",
        "",
        f"Workflow template: **{template.name}**",
        "",
        template.description,
        "",
        "## Batch Summary",
        "",
        f"- Job ID: `{report.job_id}`",
        f"- Total files: {report.total}",
        f"- Succeeded: {report.succeeded}",
        f"- Failed: {report.failed}",
        f"- Files requiring review: {review_count}",
        "",
        "## Review Focus",
        "",
    ]
    lines.extend(f"- {item}" for item in template.review_focus)
    lines.extend(["", "## Recommended Handoff Steps", ""])
    lines.extend(f"{index}. {step}" for index, step in enumerate(template.handoff_steps, start=1))
    lines.extend(
        [
            "",
            "## Files To Open First",
            "",
            "- `conversion_report.md`",
            "- `exports/review_checklist.md`",
            "- `rag_chunks.jsonl`",
            "- the vendor starter file for the target knowledge-base system",
            "",
            "## Import Caution",
            "",
            "Starter exports may need customer-specific field mapping before production import.",
        ]
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


def _recommended_action(
    status: str, warnings: str, error: str | None, language: Language = "en"
) -> str:
    if language == "zh-CN":
        if status == "failed":
            return "换一条解析路线重试，或检查源文件是否损坏/加密。"
        if "possible_table_loss" in warnings:
            return "对照原文件检查表格是否丢失或错位。"
        if "long_document_without_headings" in warnings:
            return "导入前建议补充标题，或先拆分源文件。"
        if error:
            return "导入前查看转换详情。"
        return "打开 Markdown 预览，确认内容质量。"

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
