from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from docpipe.exports import export_knowledge_pack
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
) -> None:
    report = convert_batch(
        input_path,
        output,
        engine=engine,
        max_chunk_chars=max_chunk_chars,
        create_job_dir=job_dir,
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
    table.add_column("Error")

    for result in report.results:
        table.add_row(
            result.filename,
            result.status,
            result.used_engine or "",
            str(result.metrics.quality_score if result.metrics else ""),
            ", ".join(result.metrics.warnings) if result.metrics else "",
            str(result.metrics.chunks if result.metrics else 0),
            result.error or "",
        )
    console.print(table)
    console.print(f"Job: {report.job_id}")
    console.print(f"Output: {actual_output.resolve()}")


if __name__ == "__main__":
    app()
