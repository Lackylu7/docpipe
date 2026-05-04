from __future__ import annotations

import re

from docpipe.models import Chunk, QualityMetrics


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


def chunk_markdown(markdown: str, max_chars: int = 1400) -> list[Chunk]:
    """Split Markdown into RAG-sized chunks while preserving structure metadata."""
    blocks = _split_blocks(markdown)
    chunks: list[Chunk] = []
    current: list[str] = []
    current_heading: str | None = None
    current_heading_path: list[str] = []
    heading_stack: list[str] = []

    def flush() -> None:
        nonlocal current
        text = "\n\n".join(part.strip() for part in current if part.strip()).strip()
        if text:
            chunks.append(
                Chunk(
                    index=len(chunks),
                    text=text,
                    chars=len(text),
                    heading=current_heading,
                    heading_path=current_heading_path.copy(),
                    token_estimate=_estimate_tokens(text),
                    contains_table=_contains_table(text),
                )
            )
        current = []

    for block in blocks:
        heading = _heading_info(block)
        projected = len("\n\n".join([*current, block]))
        if heading and current:
            flush()
        elif current and projected > max_chars:
            flush()

        if heading:
            level, text = heading
            heading_stack = heading_stack[: level - 1]
            heading_stack.append(text)
            current_heading = text
            current_heading_path = heading_stack.copy()
        current.append(block)

    flush()
    return chunks


def quality_metrics(markdown: str, chunks: list[Chunk]) -> QualityMetrics:
    lines = markdown.splitlines()
    chars = len(markdown)
    headings = sum(1 for line in lines if HEADING_RE.match(line.strip()))
    tables = _count_tables(lines)
    warnings = _quality_warnings(
        markdown,
        chars=chars,
        headings=headings,
        chunks=len(chunks),
        tables=tables,
        chunk_lengths=[chunk.chars for chunk in chunks],
    )
    score = _quality_score(warnings)
    return QualityMetrics(
        chars=chars,
        words=len(re.findall(r"\S+", markdown)),
        lines=len(lines),
        headings=headings,
        tables=tables,
        chunks=len(chunks),
        empty=not bool(markdown.strip()),
        quality_score=score,
        warnings=warnings,
        review_required=score < 80 or bool(warnings),
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


def _heading_info(block: str) -> tuple[int, str] | None:
    match = HEADING_RE.match(block.strip())
    if not match:
        return None
    return len(match.group(1)), match.group(2).strip()


def _count_tables(lines: list[str]) -> int:
    count = 0
    in_table = False
    for line in lines:
        is_table_line = "|" in line and line.strip().startswith("|")
        if is_table_line and not in_table:
            count += 1
        in_table = is_table_line
    return count


def _quality_warnings(
    markdown: str,
    chars: int,
    headings: int,
    chunks: int,
    tables: int,
    chunk_lengths: list[int],
) -> list[str]:
    warnings: list[str] = []
    stripped = markdown.strip()
    if not stripped:
        warnings.append("empty_output")
        return warnings
    if chars < 200:
        warnings.append("very_short_output")
    if chunks == 0:
        warnings.append("no_chunks")
    if chunks > 1 and max(chunk_lengths, default=0) > 2800:
        warnings.append("oversized_chunks")
    if chunks > 3 and min(chunk_lengths, default=0) < 120:
        warnings.append("tiny_chunks")
    if chars > 2000 and headings == 0:
        warnings.append("long_document_without_headings")
    if "|" in markdown and tables == 0:
        warnings.append("possible_table_loss")
    if _duplicate_line_ratio(markdown) > 0.35:
        warnings.append("repetitive_lines")
    if _mojibake_ratio(markdown) > 0.01:
        warnings.append("possible_encoding_noise")
    if _replacement_char_ratio(markdown) > 0:
        warnings.append("contains_replacement_characters")
    return warnings


def _quality_score(warnings: list[str]) -> int:
    score = 100
    penalties = {
        "empty_output": 100,
        "very_short_output": 25,
        "no_chunks": 30,
        "oversized_chunks": 15,
        "tiny_chunks": 10,
        "long_document_without_headings": 15,
        "possible_table_loss": 20,
        "repetitive_lines": 15,
        "possible_encoding_noise": 25,
        "contains_replacement_characters": 25,
    }
    for warning in warnings:
        score -= penalties.get(warning, 10)
    return max(score, 0)


def _mojibake_ratio(text: str) -> float:
    if not text:
        return 0
    suspicious = sum(text.count(char) for char in ("Ã", "Â", "�", "鈥", "馃", "锟"))
    return suspicious / len(text)


def _replacement_char_ratio(text: str) -> float:
    if not text:
        return 0
    return text.count("\ufffd") / len(text)


def _contains_table(text: str) -> bool:
    return any("|" in line and line.strip().startswith("|") for line in text.splitlines())


def _estimate_tokens(text: str) -> int:
    ascii_words = len(re.findall(r"[A-Za-z0-9_]+", text))
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    punctuation_adjustment = max(len(text) // 18, 0)
    return max(ascii_words + cjk_chars + punctuation_adjustment, 1 if text.strip() else 0)


def _duplicate_line_ratio(text: str) -> float:
    lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 20]
    if not lines:
        return 0
    return 1 - (len(set(lines)) / len(lines))
