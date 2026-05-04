from __future__ import annotations

import re

from docpipe.models import Chunk, QualityMetrics


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


def chunk_markdown(markdown: str, max_chars: int = 1400) -> list[Chunk]:
    """Split Markdown into RAG-sized chunks while keeping headings and tables readable."""
    blocks = _split_blocks(markdown)
    chunks: list[Chunk] = []
    current: list[str] = []
    current_heading: str | None = None

    def flush() -> None:
        nonlocal current
        text = "\n\n".join(part.strip() for part in current if part.strip()).strip()
        if text:
            chunks.append(
                Chunk(index=len(chunks), text=text, chars=len(text), heading=current_heading)
            )
        current = []

    for block in blocks:
        heading = _heading_text(block)
        projected = len("\n\n".join([*current, block]))
        if heading and current:
            flush()
        elif current and projected > max_chars:
            flush()

        if heading:
            current_heading = heading
        current.append(block)

    flush()
    return chunks


def quality_metrics(markdown: str, chunks: list[Chunk]) -> QualityMetrics:
    lines = markdown.splitlines()
    return QualityMetrics(
        chars=len(markdown),
        words=len(re.findall(r"\S+", markdown)),
        lines=len(lines),
        headings=sum(1 for line in lines if HEADING_RE.match(line.strip())),
        tables=_count_tables(lines),
        chunks=len(chunks),
        empty=not bool(markdown.strip()),
    )


def _split_blocks(markdown: str) -> list[str]:
    blocks: list[str] = []
    table_buffer: list[str] = []
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append("\n".join(paragraph).strip())
            paragraph = []

    def flush_table() -> None:
        nonlocal table_buffer
        if table_buffer:
            blocks.append("\n".join(table_buffer).strip())
            table_buffer = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        is_table_line = "|" in line and line.strip().startswith("|")
        if is_table_line:
            flush_paragraph()
            table_buffer.append(line)
            continue

        flush_table()
        if not line.strip():
            flush_paragraph()
            continue
        if HEADING_RE.match(line.strip()):
            flush_paragraph()
            blocks.append(line.strip())
            continue
        paragraph.append(line)

    flush_table()
    flush_paragraph()
    return [block for block in blocks if block]


def _heading_text(block: str) -> str | None:
    match = HEADING_RE.match(block.strip())
    return match.group(2).strip() if match else None


def _count_tables(lines: list[str]) -> int:
    count = 0
    in_table = False
    for line in lines:
        is_table_line = "|" in line and line.strip().startswith("|")
        if is_table_line and not in_table:
            count += 1
        in_table = is_table_line
    return count
