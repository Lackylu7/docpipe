from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

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
) -> None:
    report = convert_batch(input_path, output, engine=engine, max_chunk_chars=max_chunk_chars)
    if rag_pack:
        export_rag_pack(report, output)

    table = Table(title="DocPipe Conversion Report")
    table.add_column("File")
    table.add_column("Status")
    table.add_column("Engine")
    table.add_column("Chunks", justify="right")
    table.add_column("Error")

    for result in report.results:
        table.add_row(
            result.filename,
            result.status,
            result.used_engine or "",
            str(result.metrics.chunks if result.metrics else 0),
            result.error or "",
        )
    console.print(table)
    console.print(f"Output: {output.resolve()}")


if __name__ == "__main__":
    app()
