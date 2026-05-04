from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from docpipe.engines import list_engines
from docpipe.exports import export_knowledge_pack
from docpipe.history import list_jobs
from docpipe.models import EngineName
from docpipe.pipeline import convert_batch, export_rag_pack

app = typer.Typer(help="Convert enterprise documents into Markdown, JSON, and RAG chunks.")
console = Console()


@app.command()
def convert(
    input_path: Path = typer.Argument(..., exists=True, help="File or folder to convert."),
    output: Path = typer.Option(Path("outputs"), "--output", "-o", help="Output folder."),
    engine: EngineName = typer.Option("auto", "--engine", "-e", help="auto, markitdown, or docling."),
    max_chunk_chars: int = typer.Option(1400, help="Maximum characters per RAG chunk."),
    rag_pack: bool = typer.Option(True, help="Write rag_chunks.jsonl."),
    job_dir: bool = typer.Option(True, help="Write outputs into a timestamped job folder."),
    export_pack: bool = typer.Option(True, help="Write starter export files for knowledge bases."),
    max_retries: int = typer.Option(1, help="Retry each engine this many times after a failure."),
) -> None:
    report = convert_batch(
        input_path,
        output,
        engine=engine,
        max_chunk_chars=max_chunk_chars,
        create_job_dir=job_dir,
        max_retries=max_retries,
    )
    actual_output = Path(report.output_dir)
    if rag_pack:
        export_rag_pack(report, actual_output)
    if export_pack:
        export_knowledge_pack(report, actual_output)

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
    console.print(f"Output: {actual_output.resolve()}")


@app.command()
def demo(
    output: Path = typer.Option(Path("outputs/demo"), "--output", "-o", help="Demo output folder."),
    max_chunk_chars: int = typer.Option(1200, help="Maximum characters per RAG chunk."),
) -> None:
    """Run DocPipe against the included sample documents."""
    sample_dir = _find_samples_dir()
    report = convert_batch(
        sample_dir,
        output,
        engine="auto",
        max_chunk_chars=max_chunk_chars,
        job_id="demo",
        create_job_dir=False,
        max_retries=1,
    )
    actual_output = Path(report.output_dir)
    export_rag_pack(report, actual_output)
    export_paths = export_knowledge_pack(report, actual_output)

    console.print("[bold]DocPipe demo completed[/bold]")
    console.print(f"Samples: {sample_dir.resolve()}")
    console.print(f"Output: {actual_output.resolve()}")
    console.print(f"Export ZIP: {Path(export_paths['zip']).resolve()}")
    console.print(f"Review checklist: {Path(export_paths['review_checklist_md']).resolve()}")
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
