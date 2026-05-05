from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from docpipe.engines import list_engines
from docpipe.exports import export_knowledge_pack
from docpipe.history import list_jobs
from docpipe.i18n import Language
from docpipe.models import EngineName
from docpipe.pipeline import convert_batch, export_rag_pack
from docpipe.synthetic import generate_synthetic_dataset
from docpipe.templates import get_template, list_templates, template_description, template_name

app = typer.Typer(help="Convert enterprise documents into Markdown, JSON, and RAG chunks.")
console = Console()


@app.command()
def convert(
    input_path: Path = typer.Argument(..., exists=True, help="File or folder to convert."),
    output: Path = typer.Option(Path("outputs"), "--output", "-o", help="Output folder."),
    engine: EngineName = typer.Option("auto", "--engine", "-e", help="auto, markitdown, or docling."),
    workflow_template: str = typer.Option(
        "general", help="Workflow template for review and handoff guidance."
    ),
    language: Language = typer.Option("en", help="Output language: en or zh-CN."),
    max_chunk_chars: int = typer.Option(
        0, help="Maximum characters per RAG chunk. Use 0 for the selected workflow template."
    ),
    rag_pack: bool = typer.Option(True, help="Write rag_chunks.jsonl."),
    job_dir: bool = typer.Option(True, help="Write outputs into a timestamped job folder."),
    export_pack: bool = typer.Option(True, help="Write starter export files for knowledge bases."),
    max_retries: int = typer.Option(1, help="Retry each engine this many times after a failure."),
) -> None:
    template = get_template(workflow_template)
    chunk_chars = max_chunk_chars or template.max_chunk_chars
    report = convert_batch(
        input_path,
        output,
        engine=engine,
        max_chunk_chars=chunk_chars,
        create_job_dir=job_dir,
        max_retries=max_retries,
    )
    actual_output = Path(report.output_dir)
    if rag_pack:
        export_rag_pack(report, actual_output)
    if export_pack:
        export_knowledge_pack(
            report, actual_output, workflow_template=workflow_template, language=language
        )

    table = Table(title="DocPipe Conversion Report")
    table.add_column("File")
    table.add_column("Status")
    table.add_column("Engine")
    table.add_column("Score", justify="right")
    table.add_column("Warnings")
    table.add_column("Chunks", justify="right")
    table.add_column("Attempts", justify="right")
    table.add_column("Error")

    for result in report.results:
        table.add_row(
            result.filename,
            result.status,
            result.used_engine or "",
            str(result.metrics.quality_score if result.metrics else ""),
            ", ".join(result.metrics.warnings) if result.metrics else "",
            str(result.metrics.chunks if result.metrics else 0),
            str(result.attempts),
            result.error or "",
        )
    console.print(table)
    console.print(f"Job: {report.job_id}")
    console.print(f"Workflow template: {template_name(template, language)}")
    console.print(f"Output: {actual_output.resolve()}")


@app.command()
def demo(
    output: Path = typer.Option(Path("outputs/demo"), "--output", "-o", help="Demo output folder."),
    workflow_template: str = typer.Option(
        "enterprise-policy", help="Workflow template for the included demo."
    ),
    language: Language = typer.Option("zh-CN", help="Output language: en or zh-CN."),
    max_chunk_chars: int = typer.Option(
        0, help="Maximum characters per RAG chunk. Use 0 for the selected workflow template."
    ),
) -> None:
    """Run DocPipe against the included sample documents."""
    sample_dir = _find_samples_dir()
    template = get_template(workflow_template)
    chunk_chars = max_chunk_chars or template.max_chunk_chars
    report = convert_batch(
        sample_dir,
        output,
        engine="auto",
        max_chunk_chars=chunk_chars,
        job_id="demo",
        create_job_dir=False,
        max_retries=1,
    )
    actual_output = Path(report.output_dir)
    export_rag_pack(report, actual_output)
    export_paths = export_knowledge_pack(
        report, actual_output, workflow_template=workflow_template, language=language
    )

    if language == "zh-CN":
        console.print("[bold]DocPipe 演示已完成[/bold]")
        console.print(f"工作流模板：{template_name(template, language)}")
        console.print(f"样例目录：{sample_dir.resolve()}")
        console.print(f"输出目录：{actual_output.resolve()}")
        console.print(f"导出 ZIP：{Path(export_paths['zip']).resolve()}")
        console.print(f"复核清单：{Path(export_paths['review_checklist_md']).resolve()}")
        console.print(f"交付指南：{Path(export_paths['handoff_guide']).resolve()}")
        console.print(f"转换成功：{report.succeeded}/{report.total}")
    else:
        console.print("[bold]DocPipe demo completed[/bold]")
        console.print(f"Workflow template: {template_name(template, language)}")
        console.print(f"Samples: {sample_dir.resolve()}")
        console.print(f"Output: {actual_output.resolve()}")
        console.print(f"Export ZIP: {Path(export_paths['zip']).resolve()}")
        console.print(f"Review checklist: {Path(export_paths['review_checklist_md']).resolve()}")
        console.print(f"Handoff guide: {Path(export_paths['handoff_guide']).resolve()}")
        console.print(f"Converted: {report.succeeded}/{report.total}")


@app.command("stress-demo")
def stress_demo(
    output: Path = typer.Option(
        Path("outputs/stress-demo"), "--output", "-o", help="Stress-demo output folder."
    ),
    files: int = typer.Option(80, "--files", min=1, max=500, help="Synthetic file count."),
    seed: int = typer.Option(7, "--seed", help="Deterministic synthetic data seed."),
    workflow_template: str = typer.Option(
        "general", help="Workflow template used for chunk size and handoff guidance."
    ),
    language: Language = typer.Option("zh-CN", help="Output language: en or zh-CN."),
    max_chunk_chars: int = typer.Option(
        0, help="Maximum characters per RAG chunk. Use 0 for the selected workflow template."
    ),
) -> None:
    """Generate a mixed synthetic company folder, then run a batch conversion."""
    dataset_dir = output / "input"
    run_dir = output / "converted"
    summary = generate_synthetic_dataset(dataset_dir, file_count=files, seed=seed)
    template = get_template(workflow_template)
    chunk_chars = max_chunk_chars or template.max_chunk_chars

    report = convert_batch(
        dataset_dir,
        run_dir,
        engine="auto",
        max_chunk_chars=chunk_chars,
        job_id="stress-demo",
        create_job_dir=False,
        max_retries=1,
    )
    actual_output = Path(report.output_dir)
    export_rag_pack(report, actual_output)
    export_paths = export_knowledge_pack(
        report, actual_output, workflow_template=workflow_template, language=language
    )

    console.print("[bold]DocPipe stress demo completed[/bold]")
    console.print(f"Generated files: {summary.file_count}")
    console.print(f"Categories: {', '.join(summary.categories)}")
    console.print(f"Input: {dataset_dir.resolve()}")
    console.print(f"Output: {actual_output.resolve()}")
    console.print(f"Export ZIP: {Path(export_paths['zip']).resolve()}")
    console.print(f"Converted: {report.succeeded}/{report.total}")


@app.command()
def history(output: Path = typer.Option(Path("outputs"), "--output", "-o", help="Output root.")) -> None:
    table = Table(title="DocPipe Job History")
    table.add_column("Job")
    table.add_column("Created")
    table.add_column("Total", justify="right")
    table.add_column("Succeeded", justify="right")
    table.add_column("Failed", justify="right")
    table.add_column("Output")
    for job in list_jobs(output):
        table.add_row(
            str(job["job_id"]),
            str(job.get("created_at") or ""),
            str(job["total"]),
            str(job["succeeded"]),
            str(job["failed"]),
            str(job["output_dir"]),
        )
    console.print(table)


@app.command()
def engines() -> None:
    table = Table(title="DocPipe Engine Registry")
    table.add_column("Engine")
    table.add_column("Priority", justify="right")
    table.add_column("Extensions")
    table.add_column("Description")
    for adapter in list_engines():
        table.add_row(
            adapter.name,
            str(adapter.priority),
            ", ".join(sorted(adapter.extensions)) or "planned adapter",
            adapter.description,
        )
    console.print(table)


@app.command()
def templates(language: Language = typer.Option("en", help="Display language: en or zh-CN.")) -> None:
    table = Table(title="DocPipe Workflow Templates")
    table.add_column("Key")
    table.add_column("Name")
    table.add_column("Chunk chars", justify="right")
    table.add_column("Best for")
    for template in list_templates():
        table.add_row(
            template.key,
            template_name(template, language),
            str(template.max_chunk_chars),
            template_description(template, language),
        )
    console.print(table)


def _find_samples_dir() -> Path:
    candidates = [
        Path.cwd() / "samples",
        Path(__file__).resolve().parents[2] / "samples",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise typer.BadParameter("No samples folder found. Run this command from the DocPipe repo root.")


if __name__ == "__main__":
    app()
